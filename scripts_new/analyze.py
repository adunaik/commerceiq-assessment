import pandas as pd
import logging
from ingest import load_data

# --------------------
# Logger setup
# --------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def analyze(catalog, inventory, performance, competitor, marketplace):
    insights = []

    # -------------------
    # 1. Stockouts
    # -------------------
    stockouts = inventory[inventory["current_fba_inventory"] <= 0]
    insights.append({
        "issue": "Stockouts detected",
        "count": len(stockouts),
        "examples": stockouts["sku"].head(3).tolist(),
        "recommendation": "Restock immediately to avoid lost sales."
    })
    logging.info("Stockouts check complete. Count = %d", len(stockouts))

    # -------------------
    # 2. Higher Prices vs Competitors
    # -------------------
    merged = pd.merge(catalog, performance, left_on="item_code", right_on="identifier", how="inner")
    higher_prices = merged[merged["competitor_price_index"] < 1]
    insights.append({
        "issue": "Higher prices vs competitors",
        "count": len(higher_prices),
        "examples": higher_prices["item_code"].head(3).tolist(),
        "recommendation": "Revisit pricing strategy or improve product differentiation."
    })
    logging.info("Higher price vs competitor check complete. Count = %d", len(higher_prices))

    # -------------------
    # 3. Low ROI Campaigns (relaxed threshold ROI < 1.2)
    # -------------------
    merged["roi"] = merged["revenue"] / merged["ad_spend"].replace(0, pd.NA)
    low_roi = merged[merged["roi"] < 1.2]
    insights.append({
        "issue": "Low return on marketing spend (ROI < 1.2)",
        "count": len(low_roi),
        "examples": low_roi["item_code"].head(3).tolist(),
        "recommendation": "Optimize ad targeting or pause underperforming campaigns."
    })
    logging.info("Low ROI campaigns check complete. Count = %d", len(low_roi))

    # -------------------
    # 4. Wasted Ad Spend (zero conversions)
    # -------------------
    wasted_spend = performance[(performance["ad_spend"] > 0) & (performance["conversions"] == 0)]
    insights.append({
        "issue": "Ad spend wasted on zero-conversion products",
        "count": len(wasted_spend),
        "examples": wasted_spend["identifier"].head(3).tolist(),
        "recommendation": "Pause or redirect budget to performing campaigns."
    })
    logging.info("Wasted ad spend check complete. Count = %d", len(wasted_spend))

    # -------------------
    # 5. Marketplace Stale Listings (relaxed threshold < 0.85)
    # -------------------
    if "data_quality_score" in marketplace.columns:
        stale_listings = marketplace[marketplace["data_quality_score"] < 0.85]
        insights.append({
            "issue": "Stale or poor-quality marketplace listings",
            "count": len(stale_listings),
            "examples": stale_listings["extraction_timestamp"].head(3).tolist(),
            "recommendation": "Refresh titles, images, and descriptions for better visibility."
        })
        logging.info("Marketplace stale listings check complete. Count = %d", len(stale_listings))

    # -------------------
    # 6. Amazon Content Quality Issues
    # -------------------
    if "platforms.amazon.products" in marketplace.columns:
        try:
            amazon_products = pd.json_normalize(marketplace["platforms.amazon.products"].iloc[0])
            content_issues = amazon_products[amazon_products["content_quality_flags"].notna()]
            insights.append({
                "issue": "Amazon listings with poor content quality",
                "count": len(content_issues),
                "examples": content_issues["title"].head(3).tolist(),
                "recommendation": "Fix bullets, add enhanced content, improve images."
            })
            logging.info("Amazon content quality issues check complete. Count = %d", len(content_issues))
        except Exception as e:
            logging.warning("Could not parse Amazon product content quality flags: %s", str(e))

    # -------------------
    # 7. Missing Product Descriptions
    # -------------------
    if "product_description" in catalog.columns:
        missing_desc = catalog[catalog["product_description"].isna()]
        insights.append({
            "issue": "Products missing descriptions",
            "count": len(missing_desc),
            "examples": missing_desc["item_code"].head(3).tolist(),
            "recommendation": "Add detailed descriptions to improve SEO and conversions."
        })
        logging.info("Missing product descriptions check complete. Count = %d", len(missing_desc))

    # -------------------
    # 8. High-Priority Products at Risk of Stockout
    # -------------------
    if "priority_tier" in catalog.columns:
        high_priority_low_stock = inventory.merge(
            catalog[["item_code", "priority_tier"]],
            left_on="sku", right_on="item_code"
        )
        high_priority_low_stock = high_priority_low_stock[
            (high_priority_low_stock["priority_tier"] == "A") &
            (high_priority_low_stock["current_fba_inventory"] < 50)
        ]
        insights.append({
            "issue": "High-priority products at risk of stockout",
            "count": len(high_priority_low_stock),
            "examples": high_priority_low_stock["sku"].head(3).tolist(),
            "recommendation": "Replenish Tier A SKUs to protect key revenue drivers."
        })
        logging.info("High-priority stockout risk check complete. Count = %d", len(high_priority_low_stock))

    # -------------------
    # 9. Competitor Promotions & Launches
    # -------------------
    if "competitor_activity" in competitor.columns:
        try:
            competitor_expanded = competitor.explode("competitor_activity")
            comp_activities = competitor_expanded["competitor_activity"].dropna().tolist()
            examples = []
            for c in comp_activities[:3]:
                if isinstance(c, dict):
                    examples.append(f"{c.get('competitor')} - {c.get('new_launches', c.get('competing_products'))}")
                else:
                    examples.append(str(c))
            insights.append({
                "issue": "Competitor promotions and new launches",
                "count": len(comp_activities),
                "examples": examples,
                "recommendation": "Prepare counter-promotions or highlight differentiators."
            })
            logging.info("Competitor activity check complete. Count = %d", len(comp_activities))
        except Exception as e:
            logging.warning("Could not parse competitor promotions: %s", str(e))

    logging.info("Analysis completed. Total insights generated = %d", len(insights))
    return insights

if __name__ == "__main__":
    catalog, inventory, performance, competitor, marketplace = load_data()
    insights = analyze(catalog, inventory, performance, competitor, marketplace)
    print("Generated Insights:\n")
    for i in insights:
        print(i)
