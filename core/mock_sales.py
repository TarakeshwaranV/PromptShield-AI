"""
Mock Sales Database for Educational Research Demonstration
Contains synthetic, fictional enterprise software sales records.
All operations are strictly read-only and in-memory.
"""

from typing import Dict, List, Any, Optional

# Synthetic fictional sales dataset
MOCK_SALES_RECORDS = [
    {"year": 2024, "month": 1, "quarter": 1, "region": "North America", "product": "Enterprise Cloud Suite", "units": 140, "revenue": 1400000, "margin_pct": 78},
    {"year": 2024, "month": 2, "quarter": 1, "region": "North America", "product": "DataShield AI Pro", "units": 210, "revenue": 840000, "margin_pct": 82},
    {"year": 2024, "month": 3, "quarter": 1, "region": "EMEA", "product": "ThreatMonitor Hub", "units": 95, "revenue": 570000, "margin_pct": 74},
    {"year": 2024, "month": 4, "quarter": 2, "region": "APAC", "product": "Enterprise Cloud Suite", "units": 110, "revenue": 1100000, "margin_pct": 77},
    {"year": 2024, "month": 5, "quarter": 2, "region": "North America", "product": "API Guard Appliance", "units": 320, "revenue": 640000, "margin_pct": 70},
    {"year": 2024, "month": 6, "quarter": 2, "region": "LATAM", "product": "Endpoint Sentinel", "units": 180, "revenue": 360000, "margin_pct": 69},
    {"year": 2024, "month": 7, "quarter": 3, "region": "North America", "product": "Enterprise Cloud Suite", "units": 160, "revenue": 1600000, "margin_pct": 80},
    {"year": 2024, "month": 8, "quarter": 3, "region": "EMEA", "product": "DataShield AI Pro", "units": 240, "revenue": 960000, "margin_pct": 83},
    {"year": 2024, "month": 9, "quarter": 3, "region": "APAC", "product": "ThreatMonitor Hub", "units": 130, "revenue": 780000, "margin_pct": 76},
    {"year": 2024, "month": 10, "quarter": 4, "region": "North America", "product": "Enterprise Cloud Suite", "units": 190, "revenue": 1900000, "margin_pct": 81},
    {"year": 2024, "month": 11, "quarter": 4, "region": "EMEA", "product": "Endpoint Sentinel", "units": 310, "revenue": 620000, "margin_pct": 71},
    {"year": 2024, "month": 12, "quarter": 4, "region": "North America", "product": "DataShield AI Pro", "units": 280, "revenue": 1120000, "margin_pct": 84},
    
    # 2025 records
    {"year": 2025, "month": 1, "quarter": 1, "region": "North America", "product": "Enterprise Cloud Suite", "units": 165, "revenue": 1650000, "margin_pct": 79},
    {"year": 2025, "month": 2, "quarter": 1, "region": "EMEA", "product": "DataShield AI Pro", "units": 230, "revenue": 920000, "margin_pct": 83},
    {"year": 2025, "month": 3, "quarter": 1, "region": "APAC", "product": "ThreatMonitor Hub", "units": 140, "revenue": 840000, "margin_pct": 75},
    {"year": 2025, "month": 4, "quarter": 2, "region": "North America", "product": "API Guard Appliance", "units": 350, "revenue": 700000, "margin_pct": 72},
]

def get_sales_summary(year: Optional[int] = None) -> Dict[str, Any]:
    """Retrieve aggregate sales summary across all regions."""
    records = MOCK_SALES_RECORDS
    if year is not None:
        records = [r for r in records if r["year"] == int(year)]
        
    if not records:
        return {"total_revenue": 0, "total_units": 0, "record_count": 0, "year_filtered": year}
        
    total_rev = sum(r["revenue"] for r in records)
    total_units = sum(r["units"] for r in records)
    avg_margin = sum(r["margin_pct"] for r in records) / len(records)
    
    return {
        "status": "success",
        "year_filter": year or "All Years",
        "total_revenue_usd": f"${total_rev:,.2f}",
        "total_units_sold": f"{total_units:,}",
        "average_margin_percent": f"{avg_margin:.1f}%",
        "total_transactions_analyzed": len(records),
    }

def get_sales_by_month(year: int, quarter: Optional[int] = None) -> Dict[str, Any]:
    """Retrieve monthly sales breakdown for a specific year and optional quarter."""
    records = [r for r in MOCK_SALES_RECORDS if r["year"] == int(year)]
    if quarter is not None:
        records = [r for r in records if r["quarter"] == int(quarter)]
        
    monthly = {}
    for r in records:
        m = r["month"]
        if m not in monthly:
            monthly[m] = {"month": m, "revenue": 0, "units": 0}
        monthly[m]["revenue"] += r["revenue"]
        monthly[m]["units"] += r["units"]
        
    sorted_months = sorted(monthly.values(), key=lambda x: x["month"])
    return {
        "status": "success",
        "year": int(year),
        "quarter": quarter,
        "monthly_breakdown": [
            {
                "month_num": m["month"],
                "revenue_usd": f"${m['revenue']:,.2f}",
                "units": m["units"]
            }
            for m in sorted_months
        ],
        "count": len(sorted_months)
    }

def get_top_products(limit: int = 5) -> Dict[str, Any]:
    """Retrieve top-selling products by revenue."""
    limit = max(1, min(int(limit), 20)) # Bound limit safely
    product_totals = {}
    for r in MOCK_SALES_RECORDS:
        p = r["product"]
        if p not in product_totals:
            product_totals[p] = {"product": p, "revenue": 0, "units": 0}
        product_totals[p]["revenue"] += r["revenue"]
        product_totals[p]["units"] += r["units"]
        
    sorted_prods = sorted(product_totals.values(), key=lambda x: x["revenue"], reverse=True)[:limit]
    return {
        "status": "success",
        "limit": limit,
        "top_products": [
            {
                "rank": idx + 1,
                "product_name": p["product"],
                "total_revenue_usd": f"${p['revenue']:,.2f}",
                "units_sold": p["units"]
            }
            for idx, p in enumerate(sorted_prods)
        ]
    }

def get_sales_by_region(region: str, year: Optional[int] = None) -> Dict[str, Any]:
    """Retrieve sales totals grouped by geographic region."""
    region_clean = str(region).strip()
    records = [r for r in MOCK_SALES_RECORDS if r["region"].lower() == region_clean.lower()]
    if year is not None:
        records = [r for r in records if r["year"] == int(year)]
        
    if not records:
        return {
            "status": "not_found",
            "message": f"No sales records found for region '{region_clean}'. Available regions: North America, EMEA, APAC, LATAM",
            "region": region_clean
        }
        
    total_rev = sum(r["revenue"] for r in records)
    total_units = sum(r["units"] for r in records)
    return {
        "status": "success",
        "region": records[0]["region"],
        "year": year or "All",
        "total_revenue_usd": f"${total_rev:,.2f}",
        "units_sold": total_units,
        "transaction_count": len(records)
    }
