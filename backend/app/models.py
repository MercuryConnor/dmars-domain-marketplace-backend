"""
Database Models

SQLAlchemy ORM models for domain marketplace entities.

This module defines:
- Domain: Main marketplace listing model with all base metrics
- Metrics are atomic and independently measurable
- No derived fields (those are computed in analytics module)
- Proper indexing for common queries and filtering
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Index
from datetime import datetime, timezone
from .database import Base


class Domain(Base):
    """
    Domain marketplace listing model.
    
    Represents a single domain for sale with marketplace metrics.
    All fields are base metrics—no derived fields are stored here.
    
    Attributes:
        id: Unique identifier
        domain_name: Domain name (unique)
        category: Marketplace category
        price: Listing price (positive)
        keyword_score: Domain keyword relevance (0-100)
        views: Number of user views
        clicks: Number of user clicks
        is_sold: Whether domain was sold
        created_at: Timestamp of creation
        updated_at: Timestamp of last modification
    """
    
    __tablename__ = "domains"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Core domain information
    domain_name = Column(String(255), unique=True, nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    
    # Marketplace metrics (base, not derived)
    price = Column(Float, nullable=False)
    keyword_score = Column(Float, nullable=False)
    views = Column(Integer, default=0, nullable=False)
    clicks = Column(Integer, default=0, nullable=False)
    is_sold = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # Composite indexes for common queries
    __table_args__ = (
        Index("ix_domain_category_created", "category", "created_at"),
        Index("ix_domain_is_sold", "is_sold"),
    )
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"<Domain(id={self.id}, domain_name='{self.domain_name}', "
            f"category='{self.category}', price={self.price})>"
        )
