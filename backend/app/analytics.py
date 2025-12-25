"""
Marketplace Analytics (read-only KPIs & insights).

SQL-first computations to keep results fresh and avoid storing derived metrics.
Pandas is avoided unless SQL becomes impractical; current analytics rely on SQL.
"""

from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from sqlalchemy.exc import OperationalError

from .models import Domain


def get_global_kpis(db: Session) -> Dict[str, Any]:
	"""Compute global KPIs: total domains, sold count, conversion rate, average price."""
	try:
		total_domains = db.query(func.count(Domain.id)).scalar() or 0
		sold_domains = db.query(func.count(Domain.id)).filter(Domain.is_sold == True).scalar() or 0

		conversion_rate = (sold_domains / total_domains * 100) if total_domains > 0 else 0.0

		avg_price = db.query(func.avg(Domain.price)).scalar()

		return {
			"total_domains": int(total_domains),
			"sold_domains": int(sold_domains),
			"conversion_rate": round(conversion_rate, 2),
			"average_price": round(float(avg_price), 2) if avg_price else 0.0,
		}
	except OperationalError:
		# Table may not exist yet; return safe defaults
		return {
			"total_domains": 0,
			"sold_domains": 0,
			"conversion_rate": 0.0,
			"average_price": 0.0,
		}


def get_category_stats(db: Session) -> List[Dict[str, Any]]:
	"""Compute per-category counts, average price, and conversion rate."""
	try:
		rows = (
			db.query(
				Domain.category.label("category"),
				func.count(Domain.id).label("count"),
				func.avg(Domain.price).label("average_price"),
				func.sum(case((Domain.is_sold == True, 1), else_=0)).label("sold_count"),
			)
			.group_by(Domain.category)
			.all()
		)

		results = []
		for row in rows:
			count = row.count or 0
			sold = row.sold_count or 0
			conversion_rate = (sold / count * 100) if count > 0 else 0.0
			results.append(
				{
					"category": row.category,
					"count": int(count),
					"sold_count": int(sold),
					"conversion_rate": round(conversion_rate, 2),
					"average_price": round(float(row.average_price), 2) if row.average_price else 0.0,
				}
			)
		return results
	except OperationalError:
		return []


def get_demand_indicators(db: Session, top_n: int = 10) -> Dict[str, Any]:
	"""
	Compute demand indicators:
	- High-interest domains: unsold domains with clicks above average.
	- Price vs engagement patterns: avg clicks/views by price band.
	"""
	try:
		# Average clicks across unsold domains to benchmark "high interest"
		avg_clicks_unsold = (
			db.query(func.avg(Domain.clicks))
			.filter(Domain.is_sold == False)
			.scalar()
		) or 0

		high_interest = (
			db.query(
				Domain.id,
				Domain.domain_name,
				Domain.category,
				Domain.price,
				Domain.views,
				Domain.clicks,
				Domain.keyword_score,
			)
			.filter(Domain.is_sold == False)
			.filter(Domain.clicks >= avg_clicks_unsold)
			.order_by(Domain.clicks.desc())
			.limit(top_n)
			.all()
		)

		high_interest_payload = [
			{
				"id": d.id,
				"domain_name": d.domain_name,
				"category": d.category,
				"price": d.price,
				"views": d.views,
				"clicks": d.clicks,
				"keyword_score": d.keyword_score,
			}
			for d in high_interest
		]

		# Price vs engagement patterns via price bands
		price_band = case(
			(Domain.price < 1000, "low"),
			(Domain.price < 10000, "mid"),
			else_="high",
		)

		band_rows = (
			db.query(
				price_band.label("band"),
				func.count(Domain.id).label("count"),
				func.avg(Domain.price).label("avg_price"),
				func.avg(Domain.views).label("avg_views"),
				func.avg(Domain.clicks).label("avg_clicks"),
			)
			.group_by(price_band)
			.all()
		)

		band_payload = []
		for row in band_rows:
			band_payload.append(
				{
					"price_band": row.band,
					"count": int(row.count or 0),
					"average_price": round(float(row.avg_price), 2) if row.avg_price else 0.0,
					"average_views": round(float(row.avg_views), 2) if row.avg_views else 0.0,
					"average_clicks": round(float(row.avg_clicks), 2) if row.avg_clicks else 0.0,
				}
			)

		return {
			"high_interest_domains": high_interest_payload,
			"price_engagement": band_payload,
			"benchmark_avg_clicks_unsold": round(float(avg_clicks_unsold), 2),
		}
	except OperationalError:
		return {
			"high_interest_domains": [],
			"price_engagement": [],
			"benchmark_avg_clicks_unsold": 0.0,
		}


def get_summary(db: Session) -> Dict[str, Any]:
	"""Aggregate summary combining global KPIs and category stats."""
	return {
		"global": get_global_kpis(db),
		"categories": get_category_stats(db),
	}
