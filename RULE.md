# RULE.md — Domain Marketplace Analytics & Recommendation System

You are GitHub Copilot operating in agent mode.

Your role is to help build a **production-style backend analytics system** for a domain marketplace similar to real-world digital platforms.

## 1. Project Objective
Build a backend-first system that:
- Stores domain marketplace data
- Computes analytics and KPIs
- Ranks and recommends domains using explainable logic
- Supports data-driven business decisions

This is NOT a demo ML project.
This is an **engineering + analytics system**.

---

## 2. Design Principles
- Prefer clarity over cleverness
- Prefer SQL for aggregations
- Prefer explainable logic over black-box ML
- Code should be modular, readable, and production-oriented

---

## 3. Technical Constraints
- Use Python and FastAPI
- Use SQLAlchemy ORM
- Use SQLite or PostgreSQL
- Use Pandas only when SQL is insufficient
- Follow clean architecture:
  - models → schemas → crud → analytics → ranking → api

---

## 4. Domain Model Rules
A Domain must include:
- domain_name
- category
- price
- keyword_score
- views
- clicks
- is_sold
- timestamps

Derived metrics MUST NOT be stored.

---

## 5. Ranking Logic Rules
- Implement rule-based scoring first
- Scores must be explainable
- Each feature's contribution must be visible
- Avoid heavy ML unless explicitly asked

---

## 6. API Rules
- Use RESTful endpoints
- Validate all inputs
- Paginate large responses
- Separate CRUD from analytics endpoints

---

## 7. Analytics Rules
- Always compute:
  - Conversion rate
  - Average price
  - Demand indicators
- Analytics must reflect marketplace decisions

---

## 8. Dashboard Rules
- Minimal UI
- Focus on insights, not aesthetics
- Tables > charts if clarity improves

---

## 9. Code Quality Rules
- No monolithic files
- Functions must do one thing
- Meaningful variable names
- Comments only where logic is non-obvious

---

## 10. Interview Readiness
All code should be explainable as:
- Why this design?
- How does this scale?
- What would you improve next?

You are building this as if a real company will maintain it.
