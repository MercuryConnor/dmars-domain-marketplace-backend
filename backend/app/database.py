"""
Database Configuration

Configures SQLAlchemy engine, sessions, and database connection.
Database URL is configurable via environment variables.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from typing import Generator

# Database URL configuration
# Default: SQLite
# Override via DATABASE_URL environment variable for PostgreSQL, MySQL, etc.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./dmars.db"
)

# Engine configuration
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ORM base for all models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function for FastAPI endpoints to get database session.
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
