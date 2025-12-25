"""
Request/Response Schemas

Pydantic models for API validation and serialization.

This module defines:
- DomainBase: Shared base schema with common fields
- DomainCreate: Schema for creating new domains with validation
- DomainUpdate: Schema for updating domains (all fields optional)
- DomainResponse: Schema for API responses including metadata
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class DomainBase(BaseModel):
    """
    Base schema with shared attributes across all domain schemas.
    
    Contains core marketplace data for a domain listing.
    """
    
    domain_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Domain name (unique, 1-255 characters)"
    )
    category: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Marketplace category (1-100 characters)"
    )
    price: float = Field(
        ...,
        gt=0,
        description="Listing price (must be positive)"
    )
    keyword_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Keyword relevance score (0-100)"
    )
    views: int = Field(
        ...,
        ge=0,
        description="Number of user views (non-negative)"
    )
    clicks: int = Field(
        ...,
        ge=0,
        description="Number of user clicks (non-negative)"
    )
    is_sold: bool = Field(
        ...,
        description="Whether domain has been sold"
    )


class DomainCreate(DomainBase):
    """
    Schema for creating a new domain listing.
    
    Inherits all validation from DomainBase.
    All fields are required for creation.
    """
    
    pass


class DomainUpdate(BaseModel):
    """
    Schema for updating an existing domain listing.
    
    All fields are optional—only provided fields will be updated.
    Inherits same validation rules as DomainBase when fields are provided.
    """
    
    domain_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Domain name (optional, 1-255 characters)"
    )
    category: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Marketplace category (optional, 1-100 characters)"
    )
    price: Optional[float] = Field(
        None,
        gt=0,
        description="Listing price (optional, must be positive if provided)"
    )
    keyword_score: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Keyword relevance score (optional, 0-100)"
    )
    views: Optional[int] = Field(
        None,
        ge=0,
        description="Number of user views (optional, non-negative)"
    )
    clicks: Optional[int] = Field(
        None,
        ge=0,
        description="Number of user clicks (optional, non-negative)"
    )
    is_sold: Optional[bool] = Field(
        None,
        description="Whether domain has been sold (optional)"
    )


class DomainResponse(DomainBase):
    """
    Schema for domain responses from API endpoints.
    
    Includes metadata (id, timestamps) in addition to base domain data.
    Uses from_attributes (orm_mode) to seamlessly convert SQLAlchemy models to response objects.
    """
    
    id: int = Field(..., description="Unique domain identifier")
    created_at: datetime = Field(..., description="Timestamp when domain was created")
    updated_at: datetime = Field(..., description="Timestamp when domain was last updated")
    
    class Config:
        """Pydantic configuration for Pydantic v2."""
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "domain_name": "example.com",
                "category": "tech",
                "price": 5000.00,
                "keyword_score": 85.5,
                "views": 150,
                "clicks": 42,
                "is_sold": False,
                "created_at": "2025-12-25T10:30:00",
                "updated_at": "2025-12-25T10:30:00"
            }
        }
