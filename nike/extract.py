import json
from parsel import Selector

# 1. Individual Small Functions for Every Data Point
def extract_product_url(card: Selector) -> str:
    """Extracts the absolute hyperlink to the product."""
    url = card.xpath("./@href").get("")
    
    # If the URL is relative, prepend the base domain to make it absolute
    if url.startswith("/"):
        return f"https://www.nike.in{url}"
        
    return url

def extract_image_url(card: Selector) -> str:
    """Extracts the source URL of the product display image."""
    return card.xpath(".//div[contains(@class, 'css-1sjxv95')]/img/@src").get("")

def extract_product_title(card: Selector) -> str:
    """Extracts the main title/name of the product."""
    # XPath 1.0 equivalent of ends-with(@id, '-1')
    xpath_query = (
        ".//div[contains(@id, 'aria-label-') and "
        "substring(@id, string-length(@id) - string-length('-1') + 1) = '-1']/text() "
        "| .//div[contains(@class, 'css-12xgt1')]/text()"
    )
    return card.xpath(xpath_query).get("").strip()

def extract_category_type(card: Selector) -> str:
    """Extracts the category/type classification (e.g., Men's Shoes)."""
    # XPath 1.0 equivalent of ends-with(@id, '-2')
    xpath_query = (
        ".//div[contains(@id, 'aria-label-') and "
        "substring(@id, string-length(@id) - string-length('-2') + 1) = '-2']/text() "
        "| .//div[contains(@class, 'css-k5ealy')]/text()"
    )
    return card.xpath(xpath_query).get("").strip()

def extract_price(card: Selector) -> str:
    """Extracts the current or discounted price text."""
    price_pieces = card.xpath(".//h3[contains(@class, 'css-1a142u8')]//text() | .//h3[contains(@class, 'css-6k8kzr')]//text()").getall()
    return "".join(price_pieces).strip()


# 2. Main Execution Function to Parse and Save to JSON
def parse_nike_html(file_path: str, output_json_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        html_content = f.read()
        
    selector = Selector(text=html_content)
    
    # Locate all individual product item cards
    product_cards = selector.xpath("//a[contains(@class, 'css-1o8jw7q')]")
    
    extracted_products = []
    
    for card in product_cards:
        product_data = {
            "product_title": extract_product_title(card),
            "category_type": extract_category_type(card),
            "price": extract_price(card),
            "image_url": extract_image_url(card),
            "product_url": extract_product_url(card)
        }
        
        if product_data["product_title"]:
            extracted_products.append(product_data)
            
    with open(output_json_path, "w", encoding="utf-8") as out_file:
        json.dump(extracted_products, out_file, indent=4, ensure_ascii=False)
        
    print(f"Successfully extracted {len(extracted_products)} products and saved to {output_json_path}")


# Run the parser (assuming the file is named source_code.html)
if __name__ == "__main__":
    source_path = r'C:\Users\hiren.chauhan\Desktop\HirenGit\nike\source_code2.html'
    output_path = r'C:\Users\hiren.chauhan\Desktop\HirenGit\nike\products_output2.json'
    parse_nike_html(source_path, output_path)