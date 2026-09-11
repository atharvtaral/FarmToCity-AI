"""
display.py
----------
Formats and prints the final OnionGuard report to the console.
"""


def print_report(image_path, analysis, logistics, market):
    provider = analysis.get("_provider_used", "unknown")

    print("\n" + "=" * 62)
    print("  ONIONGUARD AI  -  QUALITY & LOGISTICS REPORT")
    print("=" * 62)
    print(f"Image analyzed : {image_path}")
    print(f"AI provider    : {provider}")
    print("-" * 62)

    print("STEP 1-2: SMARTPHONE AI SCAN")
    print(f"  Quality Score       : {analysis.get('quality_score')} / 850  ({analysis.get('quality_label')})")
    print(f"  Freshness           : {analysis.get('freshness_percent')}%")
    print(f"  Estimated Defects   : {analysis.get('estimated_defect_percent')}%")
    print(f"  Size Grade          : {analysis.get('size_grade')}")
    issues = analysis.get("visible_issues") or []
    print(f"  Visible Issues      : {', '.join(issues) if issues else 'None detected'}")
    print(f"  Notes               : {analysis.get('notes')}")

    print("\nSTEP 3: AI LOGISTICS ADVISORY")
    print(f"  Transit Spoilage Risk : {logistics['transit_spoilage_risk']}")
    print(f"  Optimal Buyer Radius  : {logistics['optimal_buyer_radius_km']} km")
    print(f"  Route Recommendation  : {logistics['route_recommendation']}")
    if logistics["warnings"]:
        print("  Warnings:")
        for w in logistics["warnings"]:
            print(f"    - {w}")

    print("\nSTEP 4: URBAN WHOLESALE MARKETPLACE")
    print(f"  Matched Buyer  : {market['buyer_name']}")
    print(f"  Offer Price    : ${market['offer_price_per_kg']} / kg")
    print(f"  Status         : {market['match_status']}")
    print("=" * 62 + "\n")
