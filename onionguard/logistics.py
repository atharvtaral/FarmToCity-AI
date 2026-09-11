"""
logistics.py
------------
Turns a quality analysis into a transit / logistics advisory:
spoilage risk, optimal buyer radius, route recommendation, warnings.
This mirrors "STEP 2/3: AI Logistics Advisory" in the product diagram.
"""


def assess_transit_risk(freshness_percent, defect_percent):
    if freshness_percent >= 90 and defect_percent <= 10:
        return "LOW"
    elif freshness_percent >= 75:
        return "MEDIUM"
    else:
        return "HIGH"


def optimal_buyer_radius_km(freshness_percent, risk_level):
    base_by_risk = {
        "LOW": 60,
        "MEDIUM": 35,
        "HIGH": 15,
    }
    base = base_by_risk.get(risk_level, 20)
    adjustment = (freshness_percent - 80) * 0.3
    radius = max(5, round(base + adjustment))
    return radius


def build_logistics_advisory(analysis):
    freshness = analysis.get("freshness_percent", 70)
    defects = analysis.get("estimated_defect_percent", 20)

    risk = assess_transit_risk(freshness, defects)
    radius = optimal_buyer_radius_km(freshness, risk)

    warnings = []
    if risk in ("MEDIUM", "HIGH"):
        warnings.append("High humidity risk on route - use ventilated crates")
    if defects > 15:
        warnings.append("Sort out damaged units before dispatch to reduce spoilage spread")
    if risk == "HIGH":
        warnings.append("Recommend same-day local sale only, avoid long-haul transit")

    if risk == "HIGH":
        route = "Short-haul to nearest urban hub"
    elif risk == "MEDIUM":
        route = "Standard route to regional wholesale market"
    else:
        route = "Extended route to premium urban wholesale buyers viable"

    return {
        "transit_spoilage_risk": risk,
        "optimal_buyer_radius_km": radius,
        "warnings": warnings,
        "route_recommendation": route,
    }
