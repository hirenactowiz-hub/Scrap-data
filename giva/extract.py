import json
import requests
from parsel import Selector

# ==========================================
# 1. HTML Scraping Logic
# ==========================================

def extract_product_url(card: Selector) -> str | None:
    """Extracts the absolute hyperlink to the product."""
    url = card.xpath("//meta[@property='og:url']/@content").get("")
    if not url:
        return None
        
    if url.startswith("/"):
        return f"https://www.giva.co{url}"
    return url

def extract_all_gallery_images(card: Selector) -> list[str]:
    """Extracts a unique, ordered list of absolute URLs for all product gallery images."""
    xpath_query = (
        "//slider-component[contains(@id, 'GalleryThumbnails')]"
        "//ul[contains(@class, 'thumbnail-list')]"
        "//li[contains(@class, 'thumbnail-list__item')]"
        "//img/@src"
    )
    img_sources = card.xpath(xpath_query).getall()
    
    unique_images = []
    for src in img_sources:
        src = src.strip()
        if not src:
            continue
            
        # Clean relative protocols to make absolute secure URLs
        if src.startswith("//"):
            src = f"https:{src}"
        elif src.startswith("/"):
            src = f"https://www.giva.co{src}"
            
        # Add to list if not already present to filter duplicates
        if src not in unique_images:
            unique_images.append(src)
            
    return unique_images

def extract_product_title(card: Selector) -> str | None:
    """Extracts the main title/name of the product."""
    title = card.xpath("//*[@id='two-layer-ring-in-yellow-gold']/h1/text()").get("").strip()
    return title if title else None

def extract_category_type(card: Selector) -> str | None:
    """Extracts the category/type classification (e.g., product)."""
    category = card.xpath("//meta[@property='og:type']/@content").get("").strip()
    return category if category else None

def extract_price(card: Selector) -> str | None:
    """Extracts the current or discounted selling price."""
    price = card.xpath("//meta[@property='og:price:amount']/@content").get("").strip()
    if price:
        try:
            return f"₹{float(price.replace(',', '')):,.0f}"
        except ValueError:
            return f"₹{price}"
    return None

def extract_original_price(card: Selector) -> str | None:
    """Extracts the original/strike price (MRP before discount)."""
    xpath_query = "//*[@id='gold_card_regular_price']/span/text()"
    price_text = card.xpath(xpath_query).get("").strip()
    return price_text if price_text else None

def extract_rating(card: Selector) -> float | None:
    """Extracts the aggregate review score rating."""
    rating_text = card.xpath("//*[@id='prod-rating']/a/span[1]/text()").get("").strip()
    try:
        return float(rating_text) if rating_text else None
    except ValueError:
        return None

def extract_rating_count(card: Selector) -> int | None:
    """Extracts the overall total number of user ratings submitted."""
    count_text = card.xpath("//*[@id='prod-rating']/a/span[3]").re_first(r'\d+')
    try:
        return int(count_text) if count_text else None
    except ValueError:
        return None
    
def extract_offers(card: Selector) -> list[str]:
    """Extracts a list of available product promotional offers."""
    xpath_query = '//*[@id="first-2-offers"]/div/accordions-custom/div/div/h3/text() |' '//*[@id="rest-offers"]/div/accordions-custom/div/div/h3/text()'
    offers = card.xpath(xpath_query).getall()
    cleaned_offers = [offer.strip() for offer in offers if offer.strip()]
    return cleaned_offers if cleaned_offers else []

def extract_product_description(card: Selector) -> str | None:
    """Extracts the descriptive text copy summarizing design attributes and styling tips."""
    meta_desc = card.xpath("//meta[@name='description']/@content").get("").strip()
    return meta_desc if meta_desc else None

def extract_the_design(card: Selector) -> list[str]:
    """Extracts design specific product text attributes."""
    xpath_query = (
        "//div[contains(@id, 'non-gold-desc-content-full')]/div[position()=1]/span[position()=1]/span//text() | "
        "//div[contains(@id, 'non-gold-desc-content-full')]/div[position()=1]/ul/li/span//text() | "
        "//div[contains(@id, 'non-gold-desc-content-full')]/div[position()=1]/ul/li//text()"
    )
    design_elements = card.xpath(xpath_query).getall()
    cleaned_elements = []
    
    for element in design_elements:
        text = element.strip()
        if not text:
            continue
            
        if text.replace(" ", "").rstrip(":").lower() == "thedesign":
            continue
            
        if text.startswith("+") and cleaned_elements:
            cleaned_elements[-1] = f"{cleaned_elements[-1]} {text}".strip()
        else:
            cleaned_elements.append(text)
            
    return cleaned_elements if cleaned_elements else []


# ==========================================
# 2. Live Delivery API Integration
# ==========================================

def get_delivery_details(pincode: str, sku: str = "R0744") -> dict | None:
    """Fetches delivery and nearby store details for a given pincode and SKU."""
    url = "https://prod.giva-api.com/getDeliveryTime"
    params = {"pin": pincode, "sku": sku, "zippee": "false", "shopify": ""}
    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "no-cache",
        "origin": "https://www.giva.co",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "referer": "https://www.giva.co/",
        "sec-ch-ua": '"Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36",
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error: API responded with status code {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ API connection error: {e}")
        return None


def process_delivery_data(data: dict, user_pincode: str) -> dict:
    """Filters store matching context for the final output."""
    if not data:
        return {"available": False}

    stores = data.get("nearby_stores", [])
    matched_store = None

    # 1. Try an exact match
    for store in stores:
        if store.get("pincode") == user_pincode:
            matched_store = store
            break

    # 2. Fallback to index-0 store
    if not matched_store and stores:
        matched_store = stores[0]

    if matched_store:
        return {"available": True, "nearby_stores": matched_store.get('name')}
    
    return {"available": False}


# ==========================================
# 3. Main Workflow Orchestration
# ==========================================

def parse_giva_html(file_path: str, output_json_path: str, pincode: str):
    """Parses local file, fetches live store availability, and builds JSON payload."""
    with open(file_path, "r", encoding="utf-8") as f:
        html_content = f.read()
        
    selector = Selector(text=html_content)
    product_cards = selector.xpath("/html")
    
    extracted_products = []
    
    # Fetch delivery details once per block run
    print(f"📡 Requesting real-time delivery data for Pincode: {pincode}...")
    raw_delivery_data = get_delivery_details(pincode)
    delivery_status = process_delivery_data(raw_delivery_data, pincode)
    
    for card in product_cards:
        product_data = {
            "product_title": extract_product_title(card),
            "category_type": extract_category_type(card),
            "price": extract_price(card),
            "original_price": extract_original_price(card),
            "rating": extract_rating(card),
            "rating_count": extract_rating_count(card),
            "offers": extract_offers(card),
            "product_description": extract_product_description(card),
            "design": extract_the_design(card),
            "image_url": extract_all_gallery_images(card),
            "product_url": extract_product_url(card),
            "delivery_info": delivery_status  # Seamless injection of API response properties
        }
        
        if product_data["product_title"]:
            extracted_products.append(product_data)
            
    with open(output_json_path, "w", encoding="utf-8") as out_file:
        json.dump(extracted_products, out_file, indent=4, ensure_ascii=False)
        
    print(f"\n✅ Finished! Extracted {len(extracted_products)} items.")
    print(f"💾 Results saved directly to: {output_json_path}\n")


if __name__ == "__main__":
    print("--- GIVA Scraping & Location Verification Suite ---")
    
    source_path = r'C:\Users\hiren.chauhan\Desktop\HirenGit\giva\source_code.html'
    output_path = r'C:\Users\hiren.chauhan\Desktop\HirenGit\giva\products_output.json'
    
    while True:
        user_pincode = input("Enter Pincode to run parser (or type 'exit' to quit): ").strip()

        if user_pincode.lower() in ["exit", "quit"]:
            print("Exiting program. Goodbye!")
            break

        if not user_pincode:
            print("Please enter a valid pincode.\n")
            continue

        parse_giva_html(source_path, output_path, user_pincode)


