import os
import json


def file_handler(filename, mode="r", data=None):
    current_dir = os.path.dirname(os.path.abspath(__file__))

    if mode == "r":
        path = os.path.join(current_dir, filename)
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    elif mode == "w":
        name, _ = os.path.splitext(filename)
        output_path = os.path.join(current_dir, f"{name}_output.json")

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        print(f"Output written to: {output_path}")


def get_data(data):
    data_layer = data.get("dataLayer", {})
    product_page = data.get("productPage", {})
    product = product_page.get("product", {})
    variants = product.get("variants", [])

    product_info = []

    for variant in variants:
        info = {
            "Brand": variant.get("brandName", ""),
            "URL": f"https://www.nykaaman.com/{variant.get('slug')}",
            "Product Id": variant.get("sku", ""),
            "Name": variant.get("name", ""),
            "RATINGS": product.get("rating", 0.0),
            "RATED_COUNT": product.get("ratingCount", 0),
            "Main Image": product.get("imageUrl", ""),
            "Other Images": [
                img.get("url", "") for img in variant.get("media", [])
            ],
            "Price": variant.get("offerPrice", 0.0),
            "Discount PERCENTAGE": variant.get("discount", 0.0),
            "MRP": variant.get("mrp", 0.0),
            "COUPON OFFERS": data_layer.get("hasOffer", ""),
        }
        product_info.append(info)

    return product_info

data = file_handler("NYKAA.JSON", mode="r")
product_info = get_data(data)
print(json.dumps(product_info, indent=4))
file_handler("NYKAA.JSON", mode="w", data=product_info)