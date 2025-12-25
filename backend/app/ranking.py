"""
Domain Ranking & Recommendation Engine

Explainable, rule-based scoring system for ranking domains in the marketplace.

This module ranks domains using a weighted scoring approach with four key components:
1. Keyword Relevance - How well the domain matches search intent
2. Engagement (CTR) - Click-through rate as a conversion signal
3. Price Competitiveness - How competitive the price is within its category
4. Conversion Signal - Bonus for sold domains or high-interest signals

All weights are explicitly defined and easily tunable. Scores are deterministic
and never stored in the database; they're computed dynamically on demand.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from .models import Domain


# ============================================================================
# SCORING WEIGHTS (Tunable Parameters)
# ============================================================================
# These weights control the importance of each ranking component.
# Total should not exceed 100 (allows room for bonuses).
# Adjust these to change marketplace ranking behavior.

WEIGHTS = {
    "keyword_relevance": 30,    # Domain keyword_score importance
    "engagement": 25,            # Click-through rate importance
    "price_competitiveness": 25, # Price ranking within category
    "conversion_signal": 15,     # Sold + high-interest bonus
}

# Bonus multipliers (applied to base score if conditions met)
BONUSES = {
    "sold": 0.10,               # +10% bonus if domain is sold
    "high_interest": 0.08,      # +8% bonus if clicks are high relative to views
}

# CTR thresholds and engagement tiers
CTR_THRESHOLD = 0.05            # 5% CTR is considered "engaged"
HIGH_INTEREST_THRESHOLD = 0.15  # 15% CTR is "high interest"


# ============================================================================
# SCORING FUNCTIONS
# ============================================================================

def calculate_keyword_relevance(keyword_score: float) -> float:
    """
    Score based on keyword relevance.
    
    Keyword score ranges 0-100; we normalize to 0-WEIGHTS["keyword_relevance"].
    
    Args:
        keyword_score: Domain keyword relevance score (0-100)
    
    Returns:
        Normalized keyword relevance score contribution
    """
    # Keyword score is already 0-100, normalize to weight allocation
    normalized = (keyword_score / 100.0) * WEIGHTS["keyword_relevance"]
    return max(0, min(normalized, WEIGHTS["keyword_relevance"]))


def calculate_engagement(views: int, clicks: int) -> float:
    """
    Score based on engagement (click-through rate).
    
    CTR = clicks / views. Higher CTR indicates more engagement.
    This is a strong conversion signal in marketplaces.
    
    Args:
        views: Number of domain views
        clicks: Number of domain clicks
    
    Returns:
        Engagement score contribution
    """
    if views == 0:
        # No views = no engagement data; return neutral score
        return WEIGHTS["engagement"] * 0.3  # 30% of engagement credit for unknown data
    
    ctr = clicks / views
    
    # Score based on CTR tier
    # 0% CTR = 0 points
    # 5% CTR (threshold) = 50% of weight
    # 15% CTR (high interest) = 100% of weight
    # Anything above 15% = 100% (capped)
    
    if ctr >= HIGH_INTEREST_THRESHOLD:
        # High engagement: full credit
        return WEIGHTS["engagement"]
    elif ctr >= CTR_THRESHOLD:
        # Moderate engagement: proportional credit
        ratio = (ctr - 0) / HIGH_INTEREST_THRESHOLD
        return WEIGHTS["engagement"] * ratio
    else:
        # Low engagement: minimal credit
        return WEIGHTS["engagement"] * (ctr / CTR_THRESHOLD) * 0.5


def calculate_price_competitiveness(
    domain_price: float,
    category: str,
    db: Session
) -> float:
    """
    Score based on price competitiveness within category.
    
    Lower prices within a category rank higher. Uses percentile ranking:
    - Cheapest in category = 100% of weight
    - Most expensive in category = 0% of weight
    
    Args:
        domain_price: This domain's price
        category: Domain category
        db: Database session for category analysis
    
    Returns:
        Price competitiveness score contribution
    """
    try:
        # Get price stats for this category (unsold domains only)
        category_prices = db.query(Domain.price).filter(
            Domain.category == category,
            Domain.is_sold == False
        ).all()
        
        if not category_prices or len(category_prices) == 0:
            # No comparable domains in category; return neutral
            return WEIGHTS["price_competitiveness"] * 0.5
        
        prices = [p[0] for p in category_prices]
        min_price = min(prices)
        max_price = max(prices)
        
        if min_price == max_price:
            # All prices the same in category; give equal credit
            return WEIGHTS["price_competitiveness"] * 0.5
        
        # Percentile ranking: where does this domain fall?
        # Lower price = higher percentile
        price_percentile = 1.0 - ((domain_price - min_price) / (max_price - min_price))
        price_percentile = max(0, min(price_percentile, 1.0))  # Clamp to [0, 1]
        
        return WEIGHTS["price_competitiveness"] * price_percentile
    
    except Exception:
        # If any error in category analysis, return neutral
        return WEIGHTS["price_competitiveness"] * 0.5


def calculate_conversion_signal(
    is_sold: bool,
    clicks: int,
    views: int
) -> float:
    """
    Score based on conversion signals (sold status + engagement level).
    
    Sold domains have proven market appeal. High-interest unsold domains
    show strong buying intent.
    
    Args:
        is_sold: Whether domain is sold
        clicks: Number of clicks
        views: Number of views
    
    Returns:
        Conversion signal score contribution
    """
    score = WEIGHTS["conversion_signal"]
    
    if is_sold:
        # Sold domain: strong conversion proof
        score *= (1 + BONUSES["sold"])
    elif views > 0:
        # Unsold but high-interest: shows buying demand
        ctr = clicks / views
        if ctr >= HIGH_INTEREST_THRESHOLD:
            score *= (1 + BONUSES["high_interest"])
    
    return min(score, WEIGHTS["conversion_signal"] * 1.2)  # Cap at 120%


# ============================================================================
# MAIN RANKING FUNCTION
# ============================================================================

def rank_domain(
    domain: Domain,
    db: Session,
    category_stats: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Calculate comprehensive ranking score for a domain.
    
    Returns both total score (0-100) and breakdown of contributing factors.
    This is the main function used by recommendation endpoints.
    
    Args:
        domain: Domain ORM object
        db: Database session for category analysis
        category_stats: Optional pre-computed category stats (for efficiency)
    
    Returns:
        Dictionary with:
        - total_score: Overall ranking (0-100)
        - scores: Breakdown of each component
        - explanation: Human-readable summary
    """
    
    # Calculate component scores
    keyword_score = calculate_keyword_relevance(domain.keyword_score)
    engagement_score = calculate_engagement(domain.views, domain.clicks)
    price_score = calculate_price_competitiveness(domain.price, domain.category, db)
    conversion_score = calculate_conversion_signal(
        domain.is_sold,
        domain.clicks,
        domain.views
    )
    
    # Total ranking score
    total_score = keyword_score + engagement_score + price_score + conversion_score
    
    # Normalize to 0-100 scale
    max_possible = sum(WEIGHTS.values()) + (
        WEIGHTS["conversion_signal"] * max(BONUSES.values())
    )
    normalized_score = min(100, (total_score / max_possible) * 100)
    
    # Build explanation
    ctr = (domain.clicks / domain.views) if domain.views > 0 else 0
    explanation_parts = []
    
    if domain.keyword_score >= 80:
        explanation_parts.append(f"Strong keyword relevance ({domain.keyword_score}/100)")
    
    if ctr >= HIGH_INTEREST_THRESHOLD:
        explanation_parts.append(f"High engagement ({ctr*100:.1f}% CTR)")
    elif ctr >= CTR_THRESHOLD:
        explanation_parts.append(f"Moderate engagement ({ctr*100:.1f}% CTR)")
    
    if domain.is_sold:
        explanation_parts.append("Proven conversion (sold)")
    
    explanation = "; ".join(explanation_parts) if explanation_parts else "Baseline domain"
    
    return {
        "total_score": round(normalized_score, 2),
        "scores": {
            "keyword_relevance": round(keyword_score, 2),
            "engagement": round(engagement_score, 2),
            "price_competitiveness": round(price_score, 2),
            "conversion_signal": round(conversion_score, 2),
        },
        "explanation": explanation,
    }


def get_top_recommendations(
    db: Session,
    limit: int = 10,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
    category_filter: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get top-ranked domain recommendations.
    
    Ranks all eligible domains, applies optional filters, and returns
    top results with score breakdowns.
    
    Args:
        db: Database session
        limit: Maximum number of recommendations to return
        price_min: Minimum price filter (optional)
        price_max: Maximum price filter (optional)
        category_filter: Specific category filter (optional)
    
    Returns:
        List of ranked domains with score details
    """
    # Build base query: only unsold domains (we recommend available inventory)
    query = db.query(Domain).filter(Domain.is_sold == False)
    
    # Apply optional filters
    if price_min is not None:
        query = query.filter(Domain.price >= price_min)
    if price_max is not None:
        query = query.filter(Domain.price <= price_max)
    if category_filter is not None:
        query = query.filter(Domain.category == category_filter)
    
    domains = query.all()
    
    # Rank each domain
    ranked = []
    for domain in domains:
        ranking = rank_domain(domain, db)
        ranked.append({
            "id": domain.id,
            "domain_name": domain.domain_name,
            "category": domain.category,
            "price": domain.price,
            "keyword_score": domain.keyword_score,
            "views": domain.views,
            "clicks": domain.clicks,
            "ctr": round(domain.clicks / domain.views, 4) if domain.views > 0 else 0,
            "ranking": ranking,
        })
    
    # Sort by total score (descending)
    ranked.sort(key=lambda x: x["ranking"]["total_score"], reverse=True)
    
    # Return top N
    return ranked[:limit]


def get_category_recommendations(
    db: Session,
    category: str,
    limit: int = 10,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
) -> List[Dict[str, Any]]:
    """
    Get top-ranked domain recommendations for a specific category.
    
    Focuses ranking within a single category for category-specific browsing.
    
    Args:
        db: Database session
        category: Category to filter by
        limit: Maximum number of recommendations
        price_min: Minimum price filter (optional)
        price_max: Maximum price filter (optional)
    
    Returns:
        List of ranked domains in the category with score details
    """
    return get_top_recommendations(
        db,
        limit=limit,
        price_min=price_min,
        price_max=price_max,
        category_filter=category,
    )
