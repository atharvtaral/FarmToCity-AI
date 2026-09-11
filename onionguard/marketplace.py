"""
marketplace.py
--------------
Simulates the "Urban Wholesale Marketplace" step: matches the scanned
batch to a buyer and computes an offer price based on quality score.

In a production version this would call a real marketplace / bidding
API instead of picking from a mock buyer list.
"""

import random

BASE_PRICE_PER_KG = 0.35  # base market reference price, USD/kg

MOCK_BUYERS = [
    "GreenBasket Urban Wholesale",
    "FreshHub B2B Market",
    "MetroGrocers Supply Co.",
    "CityFarm Distributors",
]


def compute_offer_price(quality_score):
    """Map a 300-850 quality score to a price multiplier of 0.6x-1.5x base price."""
    normalized = (quality_score - 300) / (850 - 300)
    normalized = max(0.0, min(1.0, normalized))
    multiplier = 0.6 + normalized * 0.9
    return round(BASE_PRICE_PER_KG * multiplier, 2)


def find_marketplace_match(analysis, logistics):
    quality_score = analysis.get("quality_score", 500)
    price = compute_offer_price(quality_score)

    if logistics["transit_spoilage_risk"] == "HIGH":
        buyer = random.choice(MOCK_BUYERS[:2])  # prefer closer, local buyers
    else:
        buyer = random.choice(MOCK_BUYERS)

    return {
        "buyer_name": buyer,
        "offer_price_per_kg": price,
        "currency": "USD",
        "match_status": "MATCH FOUND",
    }
