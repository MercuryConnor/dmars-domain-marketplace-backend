"""
CRUD Operations for Domain entities.

This module contains database access helpers used by API routes.
Business logic stays out of CRUD; functions focus on persistence only.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from .models import Domain
from .schemas import DomainCreate, DomainUpdate


def create_domain(db: Session, domain_create: DomainCreate) -> Domain:
	"""Create a new domain listing."""
	domain = Domain(**domain_create.model_dump())
	db.add(domain)
	db.commit()
	db.refresh(domain)
	return domain


def get_domain(db: Session, domain_id: int) -> Optional[Domain]:
	"""Retrieve a domain by its ID."""
	return db.query(Domain).filter(Domain.id == domain_id).first()


def get_domains(
	db: Session,
	skip: int = 0,
	limit: int = 50,
	category: Optional[str] = None,
	is_sold: Optional[bool] = None,
) -> List[Domain]:
	"""List domains with optional filtering and pagination."""
	query = db.query(Domain)

	if category:
		query = query.filter(Domain.category == category)

	if is_sold is not None:
		query = query.filter(Domain.is_sold == is_sold)

	return query.offset(skip).limit(limit).all()


def update_domain(db: Session, domain_id: int, domain_update: DomainUpdate) -> Optional[Domain]:
	"""Update an existing domain listing with partial fields."""
	domain = get_domain(db, domain_id)
	if not domain:
		return None

	update_data = domain_update.model_dump(exclude_unset=True)
	for key, value in update_data.items():
		setattr(domain, key, value)

	db.add(domain)
	db.commit()
	db.refresh(domain)
	return domain


def delete_domain(db: Session, domain_id: int) -> bool:
	"""Delete a domain listing by ID. Returns True if deleted, False if not found."""
	domain = get_domain(db, domain_id)
	if not domain:
		return False

	db.delete(domain)
	db.commit()
	return True
