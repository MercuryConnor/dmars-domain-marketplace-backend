"""
Domain & Analytics API Routes

CRUD endpoints for domains and read-only analytics endpoints.
Routing layer delegates persistence to CRUD helpers and analytics to analytics module.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from .database import get_db
from . import crud
from .schemas import DomainCreate, DomainUpdate, DomainResponse
from .models import Domain
from . import analytics
from . import ranking

# Domain CRUD router
router = APIRouter(prefix="/domains", tags=["domains"])

# Analytics router (read-only)
analytics_router = APIRouter(prefix="/analytics", tags=["analytics"])

# Recommendations router (read-only ranking & recommendations)
recommendations_router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.post("", response_model=DomainResponse, status_code=status.HTTP_201_CREATED)
def create_domain_endpoint(
    domain_create: DomainCreate,
    db: Session = Depends(get_db),
):
    """Create a new domain listing. Reject duplicates by domain_name."""
    existing = db.query(Domain).filter(Domain.domain_name == domain_create.domain_name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Domain name already exists",
        )
    domain = crud.create_domain(db, domain_create)
    return domain


@router.get("", response_model=List[DomainResponse])
def list_domains_endpoint(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=200, description="Number of records to return"),
    category: Optional[str] = Query(None, description="Filter by category"),
    is_sold: Optional[bool] = Query(None, description="Filter by sold status"),
    db: Session = Depends(get_db),
):
    """List domains with optional pagination and filtering."""
    domains = crud.get_domains(db, skip=skip, limit=limit, category=category, is_sold=is_sold)
    return domains


@router.get("/{domain_id}", response_model=DomainResponse)
def get_domain_endpoint(domain_id: int, db: Session = Depends(get_db)):
    """Retrieve a domain by ID."""
    domain = crud.get_domain(db, domain_id)
    if not domain:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Domain not found")
    return domain


@router.patch("/{domain_id}", response_model=DomainResponse)
def update_domain_endpoint(
    domain_id: int,
    domain_update: DomainUpdate,
    db: Session = Depends(get_db),
):
    """Partially update a domain listing."""
    domain = crud.update_domain(db, domain_id, domain_update)
    if not domain:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Domain not found")
    return domain


@router.delete("/{domain_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_domain_endpoint(domain_id: int, db: Session = Depends(get_db)):
    """Delete a domain listing."""
    deleted = crud.delete_domain(db, domain_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Domain not found")
    return None


# ----------------------
# Analytics endpoints
# ----------------------


@analytics_router.get("/summary")
def analytics_summary(db: Session = Depends(get_db)):
    """Global KPIs and category breakdown."""
    return analytics.get_summary(db)


@analytics_router.get("/categories")
def analytics_categories(db: Session = Depends(get_db)):
    """Category-level analytics: count, sold count, conversion, average price."""
    return analytics.get_category_stats(db)


@analytics_router.get("/demand")
def analytics_demand(db: Session = Depends(get_db), top_n: int = Query(10, ge=1, le=100)):
    """Demand indicators: high-interest domains and price vs engagement patterns."""
    return analytics.get_demand_indicators(db, top_n=top_n)


# ----------------------
# Recommendations endpoints
# ----------------------


@recommendations_router.get("/top")
def recommendations_top(
    limit: int = Query(10, ge=1, le=100, description="Number of recommendations"),
    price_min: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    price_max: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    db: Session = Depends(get_db),
):
    """
    Get top domain recommendations across all categories.
    
    Domains are ranked by explainable scoring based on:
    - Keyword relevance
    - Engagement (click-through rate)
    - Price competitiveness within category
    - Conversion signals (sold status, high interest)
    
    Response includes domain info and detailed score breakdown.
    """
    recommendations = ranking.get_top_recommendations(
        db,
        limit=limit,
        price_min=price_min,
        price_max=price_max,
    )
    return {
        "count": len(recommendations),
        "limit": limit,
        "recommendations": recommendations,
        "ranking_explanation": {
            "weights": ranking.WEIGHTS,
            "bonuses": ranking.BONUSES,
            "scoring_components": [
                "keyword_relevance - domain keyword score relevance (0-100)",
                "engagement - click-through rate as conversion signal",
                "price_competitiveness - price ranking within category",
                "conversion_signal - sold status and high-interest bonus",
            ]
        }
    }


@recommendations_router.get("/category/{category}")
def recommendations_by_category(
    category: str,
    limit: int = Query(10, ge=1, le=100, description="Number of recommendations"),
    price_min: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    price_max: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    db: Session = Depends(get_db),
):
    """
    Get top domain recommendations for a specific category.
    
    Focuses ranking within a category for category-specific browsing.
    Same ranking logic as /recommendations/top but filtered to one category.
    
    Response includes domain info and detailed score breakdown.
    """
    recommendations = ranking.get_category_recommendations(
        db,
        category=category,
        limit=limit,
        price_min=price_min,
        price_max=price_max,
    )
    return {
        "category": category,
        "count": len(recommendations),
        "limit": limit,
        "recommendations": recommendations,
        "ranking_explanation": {
            "weights": ranking.WEIGHTS,
            "bonuses": ranking.BONUSES,
            "scoring_components": [
                "keyword_relevance - domain keyword score relevance (0-100)",
                "engagement - click-through rate as conversion signal",
                "price_competitiveness - price ranking within category",
                "conversion_signal - sold status and high-interest bonus",
            ]
        }
    }
