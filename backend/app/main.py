"""
FastAPI Application Entry Point

Initializes the DMARS backend with core configuration and health checks.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import router as domain_router, analytics_router, recommendations_router
from .database import Base, engine
from . import models

# Create FastAPI application
app = FastAPI(
    title="DMARS - Domain Marketplace Analytics & Recommendation System",
    description="Production-style backend for domain marketplace analytics",
    version="1.0.0"
)

# Initialize database tables at startup
Base.metadata.create_all(bind=engine)

# Add CORS middleware for localhost development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register domain CRUD routes
app.include_router(domain_router)
app.include_router(analytics_router)
app.include_router(recommendations_router)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "DMARS Backend API",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
