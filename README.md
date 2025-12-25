# DMARS — Domain Marketplace Analytics & Recommendation System

A production-style backend analytics system for managing and recommending domain marketplace listings.

## Project Description

DMARS is a backend-first analytics platform that stores domain marketplace data, computes key business metrics (KPIs), and provides explainable ranking and recommendation logic. Built with FastAPI, SQLAlchemy, and a focus on clean architecture and SQL-first analytics.

## Setup Instructions

### Prerequisites
- Python 3.9+
- pip

### Backend Setup

1. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Run the FastAPI server:**
   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000`
   - Interactive API docs: `http://localhost:8000/docs`
   - Health check: `http://localhost:8000/health`

### Dashboard Setup

1. **Install Streamlit (if not already installed):**
   ```bash
   pip install streamlit
   ```

2. **Run the dashboard:**
   ```bash
   streamlit run dashboard/app.py
   ```

   The dashboard will open at `http://localhost:8501`

## Project Structure

```
DMARS/
├── backend/
│   ├── app/
│   │   ├── __init__.py           # Package initialization
│   │   ├── main.py               # FastAPI app entry point
│   │   ├── database.py           # SQLAlchemy configuration
│   │   ├── models.py             # ORM models
│   │   ├── schemas.py            # Pydantic schemas
│   │   ├── crud.py               # Database operations
│   │   ├── analytics.py          # KPI calculations
│   │   ├── ranking.py            # Ranking/recommendation logic
│   │   └── seed.py               # Database seeding
│   └── requirements.txt          # Python dependencies
├── dashboard/
│   └── app.py                    # Streamlit dashboard
├── data/
│   └── sample_domains.csv        # Sample domain data
├── RULE.md                       # Design and development rules
└── README.md                     # This file
```

## Current Phase

**Phase 1: Repository & Environment Setup** ✓ Complete

Subsequent phases will include:
- Phase 2: Database models and schemas
- Phase 3: CRUD operations and basic endpoints
- Phase 4: Analytics computations
- Phase 5: Ranking and recommendation logic
- Phase 6: Dashboard integration

## Notes

- Database URL is configurable via `DATABASE_URL` environment variable
- Default: SQLite (`dmars.db`)
- Can be switched to PostgreSQL or other databases
