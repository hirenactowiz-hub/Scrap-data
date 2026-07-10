import json
import os
from parsel import Selector

def extract_product_title(card: Selector) -> str:
    """Extracts the product title string from the pdp-link header tag."""
    title = card.xpath('.//div[@class="pdp-link"]/a/h3/text()').get()
    return title.strip() if title else None


def extract_price(card: Selector) -> str:
    """Extracts and clean-normalizes the visible text of the original price."""
    # normalize-space() collapses all inner text nodes, spaces, and newlines into one clean string
    price = card.xpath('normalize-space(.//span[contains(@class, "strike-through")]//span[@class="value"])').get()
    
    if price:
        # Remove the hidden screen-reader texts if they got grouped in
        price = price.replace("Price reduced from", "").replace("to", "").strip()
        return price if price else None
    return None


def extract_sale_price(card: Selector) -> str:
    """Extracts the current promotional sale price and normalizes currency."""
    sale_price = card.xpath('.//span[contains(@class, "sales")]//span[@class="value"]/text()').get()
    if sale_price:
        sale_price = sale_price.strip()
        return f"₹{sale_price}" if not sale_price.startswith("₹") else sale_price
    return None


def extract_best_price(card: Selector) -> str:
    """Extracts the best offer price from the tag details, stripping any text prefix."""
    best_price_raw = card.xpath('string(.//*[contains(@class, "bestPrice-para")])').get()
    
    if best_price_raw:
        return best_price_raw.replace("Best price :", "").strip()
    return None


def extract_discount(card: Selector) -> str:
    """Extracts the discount percentage and strips outer structural brackets."""
    discount = card.xpath('.//div[@class="discount-percentage"]/text()').get()
    return discount.strip(" ()\n\t") if discount else None


def extract_img_url(card: Selector) -> str:
    """Extracts the image URL checking for lazy-loading attributes first, falling back to src."""
    img_url = card.xpath('.//div[@class="image-container"]//img[contains(@class, "tile-image")]/@data-src').get()
    if not img_url:
        img_url = card.xpath('.//div[@class="image-container"]//img[contains(@class, "tile-image")]/@src').get()
    return img_url.strip() if img_url else None


def extract_product_url(card: Selector, base_domain: str = "https://www.pepejeans.in") -> str:
    """Extracts the relative product link and resolves it against the absolute base domain."""
    product_href = card.xpath('.//div[@class="image-container"]/a/@href').get()
    if product_href:
        product_href = product_href.strip()
        return f"{base_domain}{product_href}" if product_href.startswith("/") else product_href
    return None


def parse_html_to_json(html_file_path: str, output_json_path: str):
    """
    Main orchestration function that reads the file, loops through product blocks
    using the mini extraction functions, and produces the final JSON output.
    """
    if not os.path.exists(html_file_path):
        print(f"Error: The input file '{html_file_path}' does not exist.")
        return

    with open(html_file_path, "r", encoding="utf-8") as file:
        html_content = file.read()

    # Create root level selector
    root_selector = Selector(text=html_content)
    
    # Locate all structural product tile wrappers
    product_cards = root_selector.xpath('//div[contains(@class, "product-tile")]')
    extracted_data = []

    for card in product_cards:
        product_info = {
            "product_title": extract_product_title(card),
            "price": extract_price(card),
            "sale_price": extract_sale_price(card),
            "best_price": extract_best_price(card),
            "discount": extract_discount(card),
            "img_url": extract_img_url(card),
            "product_url": extract_product_url(card)
        }
        
        # Ensure we don't save empty/ghost blocks if any exist in the source structure
        if product_info["product_title"] or product_info["product_url"]:
            extracted_data.append(product_info)

    # Save to json file
    with open(output_json_path, "w", encoding="utf-8") as json_file:
        json.dump(extracted_data, json_file, indent=4, ensure_ascii=False)

    print(f"Successfully compiled {len(extracted_data)} products into '{output_json_path}'.")


# --- Example Execution Block ---
if __name__ == "__main__":
    source_path = r'C:\Users\hiren.chauhan\Desktop\HirenGit\pepe\source_code3.html'
    output_path = r'C:\Users\hiren.chauhan\Desktop\HirenGit\pepe\product_output3.json'
    parse_html_to_json(source_path, output_path)