import json

# --- Core Utility Function ---

def get_by_path(data, path, default=None):
    """Safely retrieves a value from a nested dict/list using a dot-separated path string."""
    if not data or not path:
        return default
    
    parts = path.split('.')
    current = data
    
    for part in parts:
        if isinstance(current, dict):
            current = current.get(part)
        elif isinstance(current, list):
            try:
                idx = int(part)
                current = current[idx] if 0 <= idx < len(current) else None
            except ValueError:
                return default
        else:
            return default
            
        if current is None:
            return default
            
    return current


# --- Micro-extraction Pipeline Functions ---

def clean_url(url):
    """Ensures image and asset links are absolute URLs."""
    if url and url.startswith("//"):
        return "https:" + url
    return url


def extract_images(modules):
    """Extracts, falls back, and sanitizes product image links."""
    skc_images = get_by_path(modules, "productInfo.currentSkcImgInfo.skcImages", [])
    main_image = skc_images[0] if skc_images else get_by_path(modules, "productInfo.goods_img")
    thumbnail = get_by_path(modules, "productInfo.goods_thumb")
    
    return {
        "main_image": clean_url(main_image),
        "thumbnail": clean_url(thumbnail),
        "images": [clean_url(img) for img in skc_images]
    }


def extract_prices(modules):
    """Extracts base pricing matrix structures for SAR and USD valuations."""
    sku_0_price = get_by_path(modules, "saleAttr.multiLevelSaleAttribute.sku_list.0.priceInfo.salePrice", {})
    price_sar = sku_0_price.get("amount")
    price_usd = sku_0_price.get("usdAmount")
    
    return {
        "sale_price_sar": price_sar,
        "sale_price_usd": price_usd,
        "retail_price_sar": price_sar
    }


def extract_skus(modules):
    """Iterates and builds available variations (SKUs) map."""
    skus_list = []
    raw_sku_list = get_by_path(modules, "saleAttr.multiLevelSaleAttribute.sku_list", [])
    
    for sku in raw_sku_list:
        sku_sale_attr = sku.get("sku_sale_attr", [{}])[0]
        skus_list.append({
            "sku_code": sku.get("sku_code"),
            "size": sku_sale_attr.get("attr_value_name") or sku_sale_attr.get("attr_value_name_en"),
            "stock": sku.get("stock"),
            "price_sar": get_by_path(sku, "priceInfo.salePrice.amount"),
            "price_usd": get_by_path(sku, "priceInfo.salePrice.usdAmount")
        })
    return skus_list


def extract_size_chart(modules):
    """Parses structural size-chart rows specifically for Arabic dimension keys."""
    size_chart_cm = []
    size_info_list = get_by_path(modules, "saleAttr.sizeInfo.sizeInfo", [])
    
    for entry in size_info_list:
        size_chart_cm.append({
            "size": entry.get("attr_value_name"),
            "shoulder_cm": entry.get("كتف "),
            "bust_cm": entry.get("قياس الصدر "),
            "length_cm": entry.get("الطول "),
            "sleeve_length_cm": entry.get("طول الأكمام "),
            "bicep_length_cm": entry.get("طول الذراع "),
            "cuff_cm": entry.get("كفة ")
        })
    return size_chart_cm


def extract_colors(modules, current_goods_id):
    """Extracts alternative product color groupings."""
    colors_list = []
    color_info = get_by_path(modules, "saleAttr.mainSaleAttribute.info", [])
    
    for item in color_info:
        goods_id = item.get("goods_id")
        colors_list.append({
            "color_name_ar": item.get("attr_value"),
            "goods_id": goods_id,
            "goods_sn": item.get("goods_sn"),
            "image": clean_url(item.get("goods_image")),
            "url_name": item.get("goods_url_name"),
            "is_current": goods_id == current_goods_id
        })
    return colors_list


def extract_attributes_and_materials(modules):
    """Combines explicit descriptive product parameters and raw material structures."""
    product_details = get_by_path(modules, "productInfo.productDescriptionInfo.productDetails", [])
    product_attributes = []
    for attr in product_details:
        product_attributes.append({
            "name_ar": attr.get("attr_name"),
            "value_ar": attr.get("attr_value"),
            "name_en": attr.get("attr_name_en"),
            "value_en": attr.get("attr_value_en")
        })
        
    material_info_list = get_by_path(modules, "productInfo.materialExposed.materialInfoList", [])
    materials = [{"name": m.get("attrName"), "value": m.get("attrValue")} for m in material_info_list]
    
    return product_attributes, materials


# --- Orchestration Controller ---

def extract_product_data(raw_json):
    """Main function that orchestrates smaller handlers to parse raw data."""
    if isinstance(raw_json, str):
        raw_json = json.loads(raw_json)
        
    modules = raw_json.get("modules", {})
    
    # Simple base field resolutions
    goods_id = get_by_path(modules, "productInfo.goods_id")
    is_on_sale = get_by_path(modules, "productInfo.is_on_sale")
    base_code_info = get_by_path(modules, "saleAttr.sizeInfo.basicAttribute.base_code_info", [])
    
    # Pull data using the micro extraction functions
    images_data = extract_images(modules)
    product_attributes, materials = extract_attributes_and_materials(modules)

    return {
        "goods_id": goods_id,
        "goods_sn": get_by_path(modules, "productInfo.goods_sn"),
        "title_ar": get_by_path(modules, "productInfo.goods_name"),
        "category": get_by_path(modules, "productInfo.cateInfos.2444.category_name"),
        "brand": get_by_path(modules, "brandDetailInfo.name", default="Manfinity"),
        "store_name": get_by_path(modules, "storeInfo.title", default="Sport MetroGents"),
        "in_stock": True if is_on_sale == "1" else False,
        "total_stock": get_by_path(modules, "productInfo.stock"),
        
        # Unpacked structural configurations
        **images_data,
        "price": extract_prices(modules),
        "sizes_available": [item.get("size") for item in base_code_info if "size" in item],
        "skus": extract_skus(modules),
        "size_chart_cm": extract_size_chart(modules),
        "colors": extract_colors(modules, current_goods_id=goods_id),
        "material": materials,
        "product_attributes": product_attributes,
        "canonical_url_name": get_by_path(modules, "saleAttr.mainSaleAttribute.info.0.goods_url_name")
    }

import json

# Load your local JSON file
file_path = r"C:\Users\hiren.chauhan\Desktop\data\shein\extracted_shein.json"
output_file = r'C:\Users\hiren.chauhan\Desktop\data\shein'
with open(file_path, "r", encoding="utf-8") as f:
    raw_data = json.load(f)


structured_data = extract_product_data(raw_data)
with open(r'C:\Users\hiren.chauhan\Desktop\data\shein\main_output.json','w',encoding='utf-8') as f:
    json.dump(structured_data,f,indent=4,ensure_ascii=False)

print(json.dumps(structured_data, indent=2, ensure_ascii=False))