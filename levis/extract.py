import json
import re
from parsel import Selector


def extract_title(card: Selector) -> str:
    """Extracts the product title text."""
    title = card.xpath(
        './/a[contains(@class, "product-card-2__title")]/text()'
    ).get()
    return title.strip() if title else None

def extract_sale_price(card: Selector) -> str:
    """Extracts the current promotional sale price using a robust, clean relative XPath."""

    # 1. Start with a dot '.' to make it relative to the current product card loop.
    # 2. Use contains(@class, ...) to match the unique wrapper and inner sale-price tags.
    price = card.xpath(
        '//span[contains(@class, "product-card-2__sale-price tw-text-black")]/text()'
    ).get()
    return price.strip() if price else None


def extract_original_price(card: Selector) -> str:
    """Extracts the structural strike-through / original retail price (MRP)."""
    orig_price = card.xpath(
        './/s[contains(@class, "product-card-2__original-price")]/text()'
    ).get()
    
    return orig_price.strip() if orig_price else None

def extract_discount(card: Selector) -> str:
    """Extracts the printed discount percentage badge label."""

    discount = card.xpath(
        './/span[@class[contains(., "product-card-2__discount") and not(contains(., "-wrapper"))]]/text()'
    ).get()

    return discount.strip() if discount else None

def extract_color(sel: Selector) -> str:
    """Extracts the color from the inner datalayer JSON fallback if available."""

    # 1. Safely extract the raw string inside the noscript tag
    json_str = sel.xpath(
        './/noscript[contains(@class, "datalayer-product-info")]/text()'
    ).get()

    if json_str:
        try:
            data = json.loads(json_str.strip())

            # 2. Extract the items list and check that it actually has content before accessing index 0
            items = data.get("items") if isinstance(data, dict) else None

            if items and isinstance(items, list):
                variant = items[0].get("item_variant", "")

                # Expecting "Color / Size / Length" format (e.g., "Blue / 30 / 32")
                if variant:
                    return variant.split("/")[0].strip()

        except (json.JSONDecodeError, IndexError, TypeError, AttributeError):
            # Added TypeError and AttributeError to safely ignore completely malformed JSON payloads
            pass

    return None


def extract_image_url(card: Selector) -> str:
    """Extracts the source URL of the main product thumbnail image,

    ensuring protocol completion and ignoring swatch buttons.
    """
    # Specifically query the main banner picture element via class identifier
    img_src = card.xpath(
        './/img[contains(@class, "product-card-2__image")]/@src'
    ).get()

    if img_src:
        img_src = img_src.strip()
        # Clean relative schema formats (e.g., '//levi.in/...') up into clear absolute hyperlinks
        if img_src.startswith("//"):
            img_src = f"https:{img_src}"
        return img_src
    return None

def extract_product_url(sel: Selector) -> str:
    """Extracts the product URL and prepends the domain if needed."""
    url = sel.xpath('.//h3/a[contains(@class, "product-card-2__title")]/@href').get()
    if url and url.startswith('/'):
        return f"https://levi.in{url}"
    return url or ""

def extract_product_details(data: Selector) -> list:
    """Iterates over the individual main product wrapper items and maps their parameters."""
    products = []

    # Target the product item layout wrappers
    cards = data.xpath('//div[contains(@class, "product-card-2__wrapper")]')

    for card in cards:
        title = extract_title(card)

        # Skip nodes missing title structures to protect sequence integrity
        if not title:
            continue

        products.append(
            {
                "title": title,
                "color": extract_color(card),
                "salePrice": extract_sale_price(card),
                "originalPrice": extract_original_price(card),
                "discount": extract_discount(card),
                "url": extract_product_url(card),
                "imageUrl": extract_image_url(card),
            }
        )

    return products


# ---------------- Final Execution ----------------

# ---------------- Final Execution ----------------

if __name__ == "__main__":
    # Corrected directory paths
    input_file = (
        r"C:\Users\hiren.chauhan\Desktop\HirenGit\levis\source_code.html"
    )
    output_filename = (
        r"C:\Users\hiren.chauhan\Desktop\HirenGit\levis\products_output.json"
    )

    try:
        with open(input_file, "r", encoding="utf-8") as file:
            html_content = file.read()

        selector_data = Selector(text=html_content)
        products_data = extract_product_details(selector_data)

        # Direct structural encapsulation wrapper
        result = {"product": products_data}

        # Export formatted structural objects directly into target JSON
        with open(output_filename, "w", encoding="utf-8") as json_file:
            json.dump(result, json_file, indent=4, ensure_ascii=False)

        print(
            f"Successfully compiled operations! Logged {len(products_data)} items directly inside '{output_filename}'."
        )

    except FileNotFoundError:
        print(f"Error: Target file reference not found at: {input_file}")