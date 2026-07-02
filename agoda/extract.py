"""
extract_agoda_data.py

Extracts a clean, simplified hotel listing structure from a raw Agoda
search-results JSON dump (data.citySearch.properties[]).

Only uses standard library modules: os, json, datetime.

Usage:
    Set INPUT_PATH / OUTPUT_PATH below (or pass env vars) and run:
        python extract_agoda_data.py
"""

import os
import json
from datetime import datetime, timezone

INPUT_PATH = r"C:\Users\hiren.chauhan\Desktop\HirenGit\agoda\agoda.json.json"
OUTPUT_PATH = r"C:\Users\hiren.chauhan\Desktop\HirenGit\agoda\agoda_clean.json"


def safe_get(obj, *keys, default=None):
    """Safely walk nested dict/list keys, returning `default` on any failure."""
    cur = obj
    for k in keys:
        try:
            cur = cur[k]
        except (KeyError, IndexError, TypeError):
            return default
    return cur if cur is not None else default


def normalize_image_url(url):
    """Convert protocol-relative URLs (//pix8.agoda.net/...) to full https:// URLs."""
    if not url:
        return None
    if url.startswith("//"):
        return "https:" + url
    if url.startswith("http://") or url.startswith("https://"):
        return url
    return "https://" + url.lstrip("/")


def normalize_property_page(path):
    """Convert a relative property page path into a full agoda.com URL with locale prefix."""
    if not path:
        return None
    if path.startswith("http://") or path.startswith("https://"):
        return path
    return "https://www.agoda.com/en-in" + ("/" + path.lstrip("/"))


def extract_property(p):
    content = p.get("content", {}) or {}
    info = content.get("informationSummary", {}) or {}
    reviews = safe_get(content, "reviews", "cumulative", default={}) or {}
    pricing = p.get("pricing", {}) or {}
    enrichment = p.get("enrichment", {}) or {}

    # First offer / first room (the "cheapest"/displayed room on the card)
    room = safe_get(pricing, "offers", 0, "roomOffers", 0, "room", default={}) or {}
    rpn_inclusive = safe_get(
        room, "pricing", 0, "price", "perRoomPerNight", "inclusive", default={}
    ) or {}

    crossed_out = rpn_inclusive.get("crossedOutPrice")
    display_price = rpn_inclusive.get("display")

    discount_percent = None
    if crossed_out and display_price and crossed_out > 0:
        discount_percent = round((1 - (display_price / crossed_out)) * 100, 2)

    deals = safe_get(room, "discount", "deals", default=[]) or []
    amount_off = None
    if "CouponAmount" in deals and crossed_out and display_price:
        amount_off = round(crossed_out - display_price, 2)

    location_score = None
    grades = safe_get(content, "reviews", "contentReview", 0, "demographics", "groups", 0, "grades", default=[]) or []
    for g in grades:
        if g.get("id") == "location":
            location_score = g.get("score")
            break

    campaign = safe_get(pricing, "pulseCampaignMetadata", default={}) or {}
    pricing_badges = safe_get(enrichment, "pricingBadges", "badges", default=[]) or []

    cancellation_type = safe_get(pricing, "payment", "cancellation", "cancellationType")

    hotel_images = safe_get(content, "images", "hotelImages", default=[]) or []
    images = [
        normalize_image_url(safe_get(img, "urls", 0, "value"))
        for img in hotel_images
        if safe_get(img, "urls", 0, "value")
    ]

    return {
        "propertyId": p.get("propertyId"),
        "name": (info.get("displayName") or "").strip(),
        "starRating": info.get("rating"),
        "propertyType": info.get("propertyType"),
        "address": {
            "area": safe_get(info, "address", "area", "name"),
            "city": safe_get(info, "address", "city", "name"),
            "distanceFromCityCenter": safe_get(
                content, "highlight", "cityCenter", "distanceFromCityCenter"
            ),
        },
        "review": {
            "score": reviews.get("score"),
            "count": reviews.get("reviewCount"),
            "locationScore": location_score,
        },
        "images": images,
        "price": {
            "currency": safe_get(room, "pricing", 0, "currency"),
            "crossedOutPrice": crossed_out,
            "displayPrice": display_price,
            "discountPercent": discount_percent,
        },
        "coupon": {
            "code": None,  # not present as plain text in raw payload
            "amountOff": amount_off,
        },
        "badges": safe_get(pricing, "growthProgramInfo", "badges", default=[]),
        "pricingBadges": pricing_badges,
        "campaign": {
            "badgeText": campaign.get("campaignBadgeText"),
            "badgeDescription": campaign.get("campaignBadgeDescText"),
            "badgeType": campaign.get("campaignBadgeType"),
        },
        "soldOut": p.get("soldOut"),
        "onlyXLeft": room.get("availableRooms"),
        "bookingActivity": {
            "count": safe_get(enrichment, "bookingHistory", "bookingCount", "count"),
            "timeFrame": safe_get(
                enrichment, "bookingHistory", "bookingCount", "timeFrame"
            ),
        },
        "freeCancellation": cancellation_type == "FreeCancellation",
        "propertyPage": normalize_property_page(safe_get(info, "propertyLinks", "propertyPage")),
    }


def main():
    if not os.path.exists(INPUT_PATH):
        print(f"Input file not found: {INPUT_PATH}")
        return

    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        raw = json.load(f)

    properties = safe_get(raw, "data", "citySearch", "properties", default=[]) or []

    cleaned = [extract_property(p) for p in properties]

    output = {
        "totalProperties": len(cleaned),
        "properties": cleaned,
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Extracted {len(cleaned)} properties -> {OUTPUT_PATH}")


if __name__ == "__main__":
    main()