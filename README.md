# Domain Marketplace Analytics & Recommendation System (DMARS)

DMARS is a **production-style backend system** that simulates how a real **domain marketplace** analyzes performance, measures demand, and ranks listings using **explainable, data-driven logic**.

The project is intentionally built with an **engineering-first approach**, focusing on clean architecture, SQL-driven analytics, and deterministic ranking instead of black-box machine learning.

## Why This Project Exists

Many student projects jump directly to machine learning models without understanding how **real marketplaces actually operate**.

In real product teams, systems are built in stages:
1. Data is modeled correctly
2. Clean APIs are exposed
3. Business KPIs are measured
4. Ranking logic is introduced
5. Machine learning comes later, if justified

DMARS follows this **real-world progression**, mirroring how marketplace platforms evolve in production.

## What This System Does

DMARS models a domain marketplace similar to platforms that sell brandable domain names.

It is designed to answer questions such as:
- How is the marketplace performing overall?
- Which categories convert better?
- Which domains should be shown first, and why?
- How do price, engagement, and relevance affect ranking?

All insights are computed **dynamically** and are **fully explainable**.

## High-Level Architecture

```
┌─────────────────────────┐
│        FastAPI           │
│  REST APIs (Read/Write)  │
└────────────┬────────────┘
             │
┌────────────▼────────────┐
│        CRUD Layer        │
│   Safe DB operations     │
└────────────┬────────────┘
             │
┌────────────▼────────────┐
│     Analytics Layer      │
│  KPIs & marketplace data │
└────────────┬────────────┘
             │
┌────────────▼────────────┐
│ Ranking & Recommendation │
│  Explainable scoring     │
└────────────┬────────────┘
             │
┌────────────▼────────────┐
│     SQLite Database      │
│   (No derived metrics)   │
└─────────────────────────┘
```

The system is intentionally layered to maintain separation of concerns and long-term maintainability.

## Core Features

### Clean Data Modeling
- Single normalized `Domain` entity
- No derived metrics stored in the database
- Analytics computed on demand

### CRUD APIs
- Create, read, update, and delete domain listings
- Pagination and filtering support
- Proper HTTP status codes and error handling

### Marketplace Analytics

**Global KPIs:**
- Total domains
- Sold domains
- Conversion rate
- Average domain price

**Category-level analytics:**
- Conversion rate per category
- Pricing trends
- Volume distribution

**Demand indicators:**
- High-interest unsold domains
- Price versus engagement patterns

### Explainable Ranking Engine

Domains are ranked using deterministic, rule-based logic.

Ranking signals include:
- Keyword relevance
- Engagement (click-through rate)
- Price competitiveness within category
- Conversion signals

Each recommendation includes:
- Final score (0–100)
- Component-wise score breakdown
- Human-readable explanation

## API Overview

### Domain APIs
```
POST   /domains
GET    /domains
GET    /domains/{id}
PATCH  /domains/{id}
DELETE /domains/{id}
```

### Analytics APIs (Read-only)
```
GET /analytics/summary
GET /analytics/categories
GET /analytics/demand
```

### Recommendation APIs (Read-only)
```
GET /recommendations/top
GET /recommendations/category/{category}
```

## Tech Stack

```
- Language: Python
- Framework: FastAPI
- Database: SQLite
- ORM: SQLAlchemy
- Validation: Pydantic
- Architecture: Layered (Models → CRUD → Analytics → Ranking → API)
```

## How to Run Locally

```bash
git clone https://github.com/MercuryConnor/dmars-domain-marketplace-backend.git
cd dmars-domain-marketplace-backend

pip install -r backend/requirements.txt

cd backend
uvicorn app.main:app --reload
```

API documentation is available at:
```
- http://localhost:8000/docs
```

Health check endpoint:
```
- http://localhost:8000/health
```

## Engineering Decisions

### Why no machine learning?
- Real marketplaces begin with rules and analytics
- Deterministic ranking is easier to debug and trust
- Machine learning is useful only after sufficient behavioral data exists

### Why SQL-first analytics?
- Aggregations are easier to reason about in SQL
- Avoids storing inconsistent derived metrics
- Improves correctness and transparency

### Why phased development?

The project was built in explicit phases:
1. Infrastructure setup
2. Data contracts
3. CRUD APIs
4. Analytics
5. Ranking and recommendations

This mirrors real engineering workflows.

## Future Improvements

- A/B testing of ranking strategies
- Offline evaluation metrics
- Machine-learning-based ranking once sufficient data is available
- Caching for high-traffic endpoints

## Final Note

DMARS is not a demo or tutorial project.

It is designed to reflect how **backend and data systems are actually built, evaluated, and evolved in production marketplace environments**.
