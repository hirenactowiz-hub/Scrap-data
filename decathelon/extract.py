import json
import os
from parsel import Selector

# =====================================================================
# INDIVIDUAL GRANULAR EXTRACTION FUNCTIONS
# If any data is wrong, update the specific function below.
# =====================================================================

def extract_title(card: Selector):
    """Extracts the product title string."""
    try:
        title = card.xpath('.//div[@data-test-id="product-card:product-card:title"]//text()').getall()
        if title:
            return "".join(title).strip()
    except Exception:
        pass
    return None

def extract_original_price(card: Selector):
    """Extracts the current original selling price."""
    try:
        price = card.xpath('.//div[@data-test-id="product-card-product-card:selling-price"]/text()').get()
        if price:
            return price.strip()
    except Exception:
        pass
    return None

def extract_mrp(card: Selector):
    """Extracts the Maximum Retail Price (MRP)."""
    try:
        mrp = card.xpath('.//div[@data-test-id="product-card-product-card:mrp"]/text()').get()
        if mrp:
            # Cleans up the 'MRP' prefix text if present
            return mrp.replace('MRP', '').strip()
    except Exception:
        pass
    return None

def extract_rating_count(card: Selector):
    """Extracts the count of ratings/reviews."""
    try:
        count = card.xpath('.//span[@data-test-id="product-card:review-count"]/text()').get()
        if count:
            return count.strip()
    except Exception:
        pass
    return None

def extract_product_url(card: Selector):
    """Extracts the product URL from the product card."""
    try:
        # Use OR to match the <a> tag whether it is the card itself or inside it
        url = card.xpath('.|.//a[@data-test-id="product-card-link"]').xpath('@href').get()
        
        # Alternative simpler approach if 'card' IS the <a> tag:
        # url = card.xpath('./@href').get() 
        
        if url:
            # Prepend the base domain if you need absolute URLs
            base_url = "https://www.decathlon.in"
            return base_url + url.strip() if url.startswith('/') else url.strip()
    except Exception as e:
        print(f"Error: {e}")
    return None

def extract_rating(card: Selector):
    """Extracts the numerical rating score (e.g., 4.7)."""
    try:
        # Tries to find numerical rating score embedded in the half-star defs id
        half_star_def = card.xpath('.//linearGradient[contains(@id, "half-fill-")]/@id').get()
        if half_star_def:
            return half_star_def.replace('half-fill-', '').strip()
        
        # Fallback: Count full stars if there's no fractional gradient layout
        full_stars = card.xpath('.//svg[contains(@data-test-id, "product-card:full-star-")]').getall()
        if full_stars:
            return str(float(len(full_stars)))
    except Exception:
        pass
    return None

def extract_image_url(card: Selector):
    """Extracts the main product image url, filtering out promotional stickers."""
    try:
        # Strictly matches the 'img' data-test-id format to avoid picking up overlay stickers
        img_src = card.xpath('.//img[@data-test-id="product-card-product-image:img"]/@src').get()
        if img_src:
            return img_src.strip()
    except Exception:
        pass
    return None

def extract_discount(card: Selector):
    """Extracts the percentage discount text."""
    try:
        discount = card.xpath('.//div[@data-test-id="product-card-product-card:discount"]/text()').get()
        if discount:
            return discount.strip()
    except Exception:
        pass
    return None


# =====================================================================
# MAIN PROCESSING ENGINE
# =====================================================================

def parse_html_to_json(input_file=r"C:\Users\hiren.chauhan\Desktop\HirenGit\decathelon\source_code2.html", output_file=r"C:\Users\hiren.chauhan\Desktop\HirenGit\decathelon\products2.json"):
    """Reads input HTML file, parses with parsel, and saves data to JSON."""
    if not os.path.exists(input_file):
        print(f"Error: The file '{input_file}' was not found. Please place it in this folder.")
        return

    print(f"Reading '{input_file}'...")
    with open(input_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
        
    # Instantiate Parsel Selector on the html content
    selector = Selector(text=html_content)
    
    # Locate all individual product link selector blocks
    product_cards = selector.xpath('//a[@data-test-id="product-card-link"]')
    print(f"Found {len(product_cards)} product cards. Starting extraction...")
    
    extracted_products = []
    
    for card in product_cards:
        # Building product items out of our single-responsibility functions
        product_data = {
            "title": extract_title(card),
            "original_price": extract_original_price(card),
            "mrp": extract_mrp(card),
            "ratingcount": extract_rating_count(card),
            "rating": extract_rating(card),
            "discount": extract_discount(card),
            "url": extract_product_url(card),
            "imageurl": extract_image_url(card),
            
        }
        extracted_products.append(product_data)
        
    # Writing the formatted JSON dictionary list to a file
    with open(output_file, 'w', encoding='utf-8') as out:
        json.dump(extracted_products, out, indent=4, ensure_ascii=False)
        
    print(f"Success! Data exported cleanly to '{output_file}'.")


if __name__ == "__main__":
    # To run this script, ensure you have run: pip install parsel
    parse_html_to_json()