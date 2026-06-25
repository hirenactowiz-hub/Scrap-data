import os
import json
import re


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
            json.dump(data, f, indent=4, ensure_ascii=False)

        print(f"Output written to: {output_path}")

def to_snake_case(text):
    text = text.strip()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", "_", text)
    return text.lower()

def get_discount_percent(price, original_price):
    if original_price and original_price > 0:
        return round(((original_price - price) / original_price) * 100)
    return 0

def get_data(data):
    product = data.get("product", {})
    product_detail = product.get("productDetails", {})

    rating_data = product_detail.get("ratingsResponse", {}).get("aggregateRating", {})
    price_data = product_detail.get("price", {})
    images = product_detail.get("images", [])
    variants = product_detail.get("variantOptions", [])
    prepaid_offers = product_detail.get("prepaidOffers", [])

    main_img = ""
    for img in images:
        if (img.get("imageType") == "PRIMARY"
            and img.get("format") == "product"
            ):
            main_img = img.get("url", "")
            break

    other_img = []
    for img in images:
        if (img.get("imageType") == "GALLERY" and img.get("format") == "product"): 
            other_img.append(img.get("url", ""))
    details = {}

    feature_data = product_detail.get("featureData")
    if not feature_data:
        feature_data = product_detail.get("sectionOne", {}).get("featureData", [])

    for feature in feature_data:
        values = [
            item.get("value", "")
            for item in feature.get("featureValues", [])
            if item.get("value")
        ]

        key = to_snake_case(feature.get("name", ""))
        details[key] = values[0] if len(values) == 1 else values

    for item in product_detail.get("mandatoryInfo", []):
        key = to_snake_case(item.get("key", ""))
        details[key] = item.get("title", "")

    if variants:
        details["product_code"] = variants[0].get("code", "")

        for item in variants[0].get("mandatoryInfo", []):
            if item.get("key") == "MRP":
                details["mrp"] = (item.get("title", "")+ item.get("subTitle", ""))
                break
    else:
        details["product_code"] = product_detail.get("baseProduct", "")
    size_list = []

    for variant in variants:
        price = variant.get("priceData", {}).get("value", 0)
        original_price = variant.get("wasPriceData", {}).get("value", 0)
        discount = get_discount_percent(price, original_price)

        size_list.append(
            {
                "size": variant.get("scDisplaySize", ""),
                "product_code": variant.get("code", ""),
                "price": price,
                "original_price": original_price,
                "discount_percent": f"{discount}%",
            }
        )

    offers = []
    # for offer in prepaid_offers:
    #     offers.append(
    #         {
    #             "bank_id": offer.get("bankId", ""),
    #             "bank_name": offer.get("bankName", ""),
    #             "description": offer.get(
    #                 "description", ""
    #             ),
    #             "offer_code": offer.get(
    #                 "offerCode", ""
    #             ),
    #             "offer_amount": offer.get(
    #                 "offerAmount", 0
    #             ),
    #         }
    #     )

    current_price = price_data.get("value", 0)
    original_price = price_data.get("wasPriceData", {}).get("value", 0)

    if not original_price and variants:
        original_price = variants[0].get("wasPriceData", {}).get("value", 0)

    discount = price_data.get("discountPercent", 0)

    if isinstance(discount, str):
        match = re.search(r"\d+", discount)
        discount = int(match.group()) if match else 0

    if not discount:
        discount = get_discount_percent(
            current_price, original_price
        )
    discount = f"{discount}%"

    product_info = {
        "brand_name": product_detail.get("brandName", ""),
        "product_id": product_detail.get("baseProduct", ""),
        "product_name": product_detail.get("name", ""),
        "url" : f"https://ajio.com{product_detail.get('url')}",
        "price": current_price,
        "mrp": original_price,
        "discount_percentage": discount,
        "rating": rating_data.get("averageRating", 0.0),
        "rated_count": rating_data.get("numUserRatings", 0),
        "main_img": main_img,
        "other_img": other_img,
        "size_list": size_list,
        "details": details,
        # "offers": offers,
    }
    return product_info

data = file_handler("AJIO-2.json")
products = get_data(data)
print(json.dumps(products, indent=4, ensure_ascii=False))
file_handler("AJIO-2.json",mode="w",data=products,)