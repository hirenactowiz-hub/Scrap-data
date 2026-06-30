"""
Airbnb Listing Data Extractor
==============================
Reads the 3 raw JSON files Airbnb's page embeds (SSR data, GraphQL pricing
response, and page-init data) and extracts a clean, structured JSON.

Usage:
    Place your JSON files in the same folder as this script, then run:
    python extract.py
"""

import json
import os
import re
from datetime import date


# ---------------------------------------------------------------------------
# 0. SAFE GETTER (tiny helper used everywhere instead of obj["a"]["b"]["c"])
# ---------------------------------------------------------------------------

def safe_get(obj, *keys, default=None):
    """Walk a chain of dict/list keys without blowing up on None/missing keys."""
    current = obj
    for key in keys:
        if current is None:
            return default
        try:
            current = current[key]
        except (KeyError, IndexError, TypeError):
            return default
    return current if current is not None else default


def strip_html(html_text):
    """Turn Airbnb's <br />/<b> description HTML into clean plain text."""
    if not html_text:
        return ""
    text = re.sub(r"<br\s*/?>", "\n", html_text)
    text = re.sub(r"<[^>]+>", "", text)
    return text.strip()


# ---------------------------------------------------------------------------
# 1. LOADING + AUTO-DETECTING THE 3 INPUT FILES
# ---------------------------------------------------------------------------

def load_raw_file(filepath):
    with open(filepath, "r", encoding="utf-8") as fp:
        return json.load(fp)


def load_input_files(filepaths):
    """
    Auto-detects which uploaded file is which, so the order the user
    provides them in doesn't matter.
    """
    buckets = {"ssr": None, "pricing": None, "misc": None}

    for path in filepaths:
        raw = load_raw_file(path)
        if "niobeClientData" in raw:
            buckets["ssr"] = raw
        elif "data" in raw and "extensions" in raw:
            buckets["pricing"] = raw
        else:
            buckets["misc"] = raw

    return buckets


# ---------------------------------------------------------------------------
# 2. CONTEXT BUILDERS (internal helpers other extractors rely on)
# ---------------------------------------------------------------------------

def get_ssr_response(ssr_raw):
    """Digs out the actual GraphQL response from the niobeClientData wrapper."""
    return safe_get(ssr_raw, "niobeClientData", 0, 1, default={})


def get_node_and_pdp(ssr_raw):
    """Returns (node, pdpPresentation) — the two richest objects in the SSR data."""
    response = get_ssr_response(ssr_raw)
    node = safe_get(response, "data", "node", default={})
    pdp = safe_get(node, "pdpPresentation", default={})
    return node, pdp


def get_sections_map(raw_response_data):
    """Converts the sections list into a dict for O(1) lookup."""
    sections = safe_get(
        raw_response_data,
        "data", "presentation", "stayProductDetailPage", "sections", "sections",
        default=[],
    )
    return {s.get("sectionId"): s.get("section", {}) for s in sections if s.get("sectionId")}


def get_request_variables(ssr_raw):
    response = get_ssr_response(ssr_raw)
    return safe_get(response, "variables", "pdpSectionsRequest", default={})


# ---------------------------------------------------------------------------
# 3. INDIVIDUAL EXTRACTOR FUNCTIONS — ONE PER JSON SECTION
# ---------------------------------------------------------------------------

def extract_listing_identity(node, ssr_raw, listing_url_fallback=""):
    listing_id = ""

    encoded_id = safe_get(get_ssr_response(ssr_raw), "variables", "id", default="")
    if encoded_id:
        listing_id = _decode_id(encoded_id)

    if not listing_id and listing_url_fallback:
        match = re.search(r"/rooms/(\d+)", listing_url_fallback)
        listing_id = match.group(1) if match else ""

    listing_url = listing_url_fallback or (
        f"https://www.airbnb.co.in/rooms/{listing_id}" if listing_id else ""
    )

    return {
        "listing_id": str(listing_id),
        "listing_url": listing_url,
    }


def extract_neighborhood_from_description(description_text):
    if not description_text:
        return ""
    patterns = [
        r"heart of\s+([A-Z][\w\s\-]{1,30}?)[.,;\n]",
        r"located in\s+([A-Z][\w\s\-]{1,30}?)[.,;\n]",
        r"neighbo(?:u)?rhood (?:in|near|of)\s+([A-Z][\w\s\-]{1,30}?)[.,;\n]",
        r"in\s+([A-Z][\w\s\-]{1,30}?)\s+area",
    ]
    for pattern in patterns:
        match = re.search(pattern, description_text)
        if match:
            return match.group(1).strip()
    return ""


def extract_property(node, pdp, sections_map, description_text=""):
    location_section = sections_map.get("LOCATION_DEFAULT", {})
    overview = safe_get(pdp, "overview", default={})
    title = safe_get(pdp, "title", "content", "localizedString", default="")

    property_type = ""
    overview_title = safe_get(overview, "title", default="")
    if overview_title:
        property_type = overview_title.split(" in ")[0].strip()

    subtitle = safe_get(location_section, "subtitle", default="")
    parts = [p.strip() for p in subtitle.split(",")] if subtitle else []
    city = parts[0] if len(parts) > 0 else ""
    state = parts[1] if len(parts) > 1 else ""
    country = parts[2] if len(parts) > 2 else ""

    raw_address = safe_get(location_section, "address", default="")
    if not raw_address:
        neighborhood = extract_neighborhood_from_description(description_text)
        raw_address = ", ".join(p for p in [ city, state, country] if p)

    return {
        "property_name": title,
        "property_type": property_type,
        "city": city,
        "state": state,
        "country": country,
        "address": raw_address,
        "latitude": safe_get(location_section, "lat"),
        "longitude": safe_get(location_section, "lng"),
    }


def extract_property_details(pdp):
    overview_items = safe_get(pdp, "overview", "items", default=[])

    patterns = {
        "guest_capacity": r"(\d+)\s*guests?\b",
        "bedrooms": r"(\d+)\s*bedrooms?\b",
        "beds": r"(\d+)\s*beds?\b(?!room)",
        "bathrooms": r"(\d+)\s*(?:private\s+)?bathrooms?\b",
    }

    def grab_number(pattern):
        for item in overview_items:
            match = re.search(pattern, item, re.IGNORECASE)
            if match:
                return int(match.group(1))
        return 0

    return {
        "guest_capacity": safe_get(pdp, "personCapacity", default=grab_number(patterns["guest_capacity"])),
        "bedrooms": grab_number(patterns["bedrooms"]),
        "beds": grab_number(patterns["beds"]),
        "bathrooms": grab_number(patterns["bathrooms"]),
    }


def extract_ratings(node, pdp):
    quality = safe_get(pdp, "quality", default={})
    overall = safe_get(quality, "listingRatingStats", "overallRatingStats", default={})

    return {
        "rating": float(safe_get(overall, "ratingAverage", default=0.0) or 0.0),
        "review_count": int(safe_get(overall, "ratingCount", default=0) or 0),
        "guest_favourite": bool(safe_get(node, "contextualizedGuestFavorites", "isGuestFavorite", default=False)),
        "category_ratings": {
            r.get("label"): float(r.get("localizedRating"))
            for r in safe_get(quality, "categoryRatings", default=[])
            if r.get("label") and r.get("localizedRating")
        },
    }


def extract_host(sections_map):
    host_section = sections_map.get("MEET_YOUR_HOST", {})
    card = safe_get(host_section, "cardData", default={})
    time_as_host = safe_get(card, "timeAsHost", default={})
    highlights = safe_get(host_section, "hostHighlights", default=[])

    hosting_since = ""
    years = safe_get(time_as_host, "years")
    months = safe_get(time_as_host, "months")
    if years is not None:
        hosting_since = f"{years} years, {months} months hosting" if months else f"{years} years hosting"

    host_details_lines = safe_get(host_section, "hostDetails", default=[])

    return {
        "host_name": safe_get(card, "name", default=""),
        "host_type": "Professional/Co-hosted" if safe_get(host_section, "cohosts") else "Individual",
        "hosting_since": hosting_since,
        "superhost": bool(safe_get(card, "isSuperhost", default=False)),
        "host_profile_url": f"https://www.airbnb.co.in/users/show/{_decode_id(card.get('userId', ''))}" if card.get("userId") else "",
        "host_image": safe_get(card, "profilePictureUrl", default=""),
        "response_rate": next((l for l in host_details_lines if "rate" in l.lower()), ""),
        "response_time": next((l for l in host_details_lines if "responds" in l.lower()), ""),
        "host_highlights": [h.get("title") for h in highlights if h.get("title")],
        "co_hosts": [c.get("name") for c in safe_get(host_section, "cohosts", default=[])],
    }


def _decode_id(b64_id):
    import base64
    try:
        decoded = base64.b64decode(b64_id).decode("utf-8")
        match = re.search(r"(\d+)$", decoded)
        return match.group(1) if match else b64_id
    except Exception:
        return b64_id


def extract_pricing(pricing_raw, stay_nights):
    sections_map = get_sections_map(safe_get(pricing_raw, default={}))
    book_it = sections_map.get("BOOK_IT_SIDEBAR", {})
    primary_line = safe_get(book_it, "structuredDisplayPrice", "primaryLine", default={})
    explanation_items = safe_get(
        book_it, "structuredDisplayPrice", "explanationData", "priceDetails", 0, "items", 0, default={}
    )

    def parse_money(s):
        if not s:
            return 0.0
        cleaned = re.sub(r"[^\d.]", "", s)
        return float(cleaned) if cleaned else 0.0

    discounted_total = parse_money(primary_line.get("discountedPrice"))
    original_total = parse_money(primary_line.get("originalPrice"))
    precise_discounted = parse_money(explanation_items.get("priceString")) or discounted_total
    precise_original = parse_money(explanation_items.get("originalPriceString")) or original_total

    price_per_night = round(precise_discounted / stay_nights, 2) if stay_nights else 0.0

    return {
        "currency": "INR",
        "original_price": precise_original,
        "discounted_price": precise_discounted,
        "price_per_night": price_per_night,
        "total_price": precise_discounted,
        "stay_nights": stay_nights,
        "includes_fees": True,
    }


def extract_booking(ssr_raw):
    variables = get_request_variables(ssr_raw)
    check_in = variables.get("checkIn", "")
    check_out = variables.get("checkOut", "")
    guests = int(variables.get("adults") or 1)

    nights = 0
    if check_in and check_out:
        try:
            d1 = date.fromisoformat(check_in)
            d2 = date.fromisoformat(check_out)
            nights = (d2 - d1).days
        except ValueError:
            nights = 0

    return {
        "check_in": check_in,
        "check_out": check_out,
        "guests_selected": guests,
    }, nights


def extract_images(pdp):
    hero_edges = safe_get(pdp, "heroMedia", "edges", default=[])
    cover_image = safe_get(hero_edges, 0, "node", "image", "uri", default="") if hero_edges else ""

    stops = safe_get(pdp, "mediaTour", "stops", default=[])
    gallery_images = []
    total_images = 0

    for stop in stops:
        room_name = stop.get("name", "")
        image_urls = [
            safe_get(item, "image", "uri", default="")
            for item in stop.get("items", [])
            if item.get("__typename") == "ImageMediaTourItem"
        ]
        image_urls = [u for u in image_urls if u]
        if room_name and image_urls:
            gallery_images.append({
                "room": room_name,
                "images": image_urls,
                "count": len(image_urls),
            })
            total_images += len(image_urls)

    return {
        "cover_image": cover_image,
        "gallery_images": gallery_images,
        "total_images": total_images,
    }


def extract_amenities(pdp):
    groups = safe_get(pdp, "amenities", "seeAllAmenitiesGroups", default=[])
    available = []
    for group in groups:
        for item in group.get("amenities", []):
            if item.get("available", True) and item.get("title"):
                available.append(item["title"])
    return available


def extract_bedroom_details(sections_map):
    arrangement = sections_map.get("SLEEPING_ARRANGEMENT_WITH_IMAGES", {})
    items = safe_get(arrangement, "arrangementDetails", default=[])
    return [
        {"room": item.get("title", ""), "configuration": item.get("subtitle", "")}
        for item in items
    ]


def extract_description(pdp):
    html = safe_get(pdp, "descriptions", "longDescriptionHtml", "localizedStringWithTranslationPreference", default="")
    return strip_html(html)


def extract_house_rules(sections_map):
    policies = sections_map.get("POLICIES_DEFAULT", {})
    rule_lines = []
    for section in safe_get(policies, "houseRulesSections", default=[]):
        for item in section.get("items", []):
            if item.get("title"):
                rule_lines.append(item["title"].lower())

    checkin_time, checkout_time = "", ""
    for line in safe_get(policies, "houseRules", default=[]):
        title = line.get("title", "")
        if "check-in" in title.lower():
            checkin_time = title.split("after")[-1].strip() if "after" in title else title
        elif "checkout" in title.lower():
            checkout_time = title.split("before")[-1].strip() if "before" in title else title

    return {
        "checkin_time": checkin_time,
        "checkout_time": checkout_time,
        "pets_allowed": not any("no pets" in r for r in rule_lines),
        "smoking_allowed": not any("no smoking" in r for r in rule_lines),
        "parties_allowed": not any("no parties" in r for r in rule_lines),
    }


def extract_cancellation_policy(ssr_raw):
    """Extracts cancellation policy tooltip using the precise path from niobeClientData."""
    response = get_ssr_response(ssr_raw)
    policy_text = safe_get(
        response,
        "data", "presentation", "stayProductDetailPage", "sections", "metadata",
        "bookingPrefetchData", "cancellationPolicies", 0, "book_it_module_tooltip",
        default=""
    )
    return policy_text or ""


def extract_reviews(sections_map):
    return []


def extract_review_tags(pdp):
    tags = safe_get(pdp, "quality", "reviewTags", default=[])
    return {t.get("localizedName"): t.get("count") for t in tags if t.get("localizedName")}


def extract_nearby_places(sections_map, property_dict=None, google_places_api_key=None):
    location = sections_map.get("LOCATION_DEFAULT", {})
    places = safe_get(location, "nearbyPlaces", default=[]) or []
    if places:
        return [p.get("title") for p in places if isinstance(p, dict) and p.get("title")]
    return []


def extract_highlights(pdp):
    highlights = safe_get(pdp, "highlights", default=[])
    return [
        {
            "title": safe_get(h, "headline", "localizedContent", default=""),
            "description": safe_get(h, "body", "localizedContent", default=""),
        }
        for h in highlights
    ]


def extract_languages(description_text):
    match = re.search(r"familiar with ([\w,\s]+?) language", description_text, re.IGNORECASE)
    if not match:
        return []
    raw = match.group(1)
    raw = raw.replace(" and ", ",")
    return [lang.strip() for lang in raw.split(",") if lang.strip()]


def extract_property_features(pdp):
    return []


def extract_safety_features(sections_map):
    policies = sections_map.get("POLICIES_DEFAULT", {})
    items = safe_get(policies, "previewSafetyAndProperties", default=[])
    return [item.get("title") for item in items if item.get("title")]


def extract_availability(pricing_raw):
    sections_map = get_sections_map(safe_get(pricing_raw, default={}))
    book_it = sections_map.get("BOOK_IT_SIDEBAR", {})
    has_price = bool(safe_get(book_it, "structuredDisplayPrice", "primaryLine", "discountedPrice"))
    return {"available": has_price}


# ---------------------------------------------------------------------------
# 4. MAIN ASSEMBLER — combines every extractor into the final schema
# ---------------------------------------------------------------------------

def build_full_listing_json(filepaths):
    raw = load_input_files(filepaths)
    ssr_raw = raw["ssr"] or {}

    node, pdp = get_node_and_pdp(ssr_raw)
    sections_map = get_sections_map(get_ssr_response(ssr_raw))

    booking, nights = extract_booking(ssr_raw)
    description_text = extract_description(pdp)
    property_dict = extract_property(node, pdp, sections_map, description_text)

    result = {
        **extract_listing_identity(node, ssr_raw),
        "property": property_dict,
        "property_details": extract_property_details(pdp),
        "ratings": extract_ratings(node, pdp),
        "host": extract_host(sections_map),
        "pricing": extract_pricing(raw["pricing"] or {}, nights),
        "booking": booking,
        "images": extract_images(pdp),
        "amenities": extract_amenities(pdp),
        "bedroom_details": extract_bedroom_details(sections_map),
        "description": description_text,
        "house_rules": extract_house_rules(sections_map),
        "cancellation_policy": extract_cancellation_policy(ssr_raw),
        "reviews": extract_reviews(sections_map),
        "nearby_places": extract_nearby_places(sections_map, property_dict),
        "highlights": extract_highlights(pdp),
        "languages": extract_languages(description_text),
        "property_features": extract_property_features(pdp),
        "safety_features": extract_safety_features(sections_map),
        "availability": extract_availability(raw["pricing"] or {}),
        "review_tags": extract_review_tags(pdp),
    }
    return result


def auto_discover_input_files(search_dir):
    """Scan directory files for specific keys instead of expecting hardcoded filenames."""
    found_paths = []
    found = {"ssr": False, "pricing": False, "misc": False}

    for filename in os.listdir(search_dir):
        if not filename.endswith(".json") or filename == "airbnb_extracted.json":
            continue
        path = os.path.join(search_dir, filename)
        try:
            raw = load_raw_file(path)
        except Exception:
            continue
        
        if isinstance(raw, dict):
            if "niobeClientData" in raw and not found["ssr"]:
                found["ssr"] = True
                found_paths.append(path)
            elif "data" in raw and "extensions" in raw and not found["pricing"]:
                found["pricing"] = True
                found_paths.append(path)
            elif not found["misc"]:
                found["misc"] = True
                found_paths.append(path)

    return found_paths


def main():
    # Force script folder discovery context
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    files = auto_discover_input_files(script_dir)
    if len(files) < 2:
        print("Error: Could not find the necessary Airbnb JSON data dumps in this folder.")
        return

    print(f"Processing discovered files: {[os.path.basename(f) for f in files]}")
    result = build_full_listing_json(files)
    
    # Strictly outputting to the script's directory location
    output_path = os.path.join(script_dir, "airbnb_extracted.json")
    
    with open(output_path, "w", encoding="utf-8") as fp:
        json.dump(result, fp, indent=2, ensure_ascii=False)
        
    print(f"Extraction successful! Output created at: {output_path}")


if __name__ == "__main__":
    main()