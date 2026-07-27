import json

def product_extract():
    price_path = r'C:\Users\hiren.chauhan\Desktop\HirenGit\oppo_reno\price_detail.json'
    detail_path = r'C:\Users\hiren.chauhan\Desktop\HirenGit\oppo_reno\phone_detail.json'
    
    with open(price_path, 'r', encoding='utf-8') as f:
        price_detail = json.load(f)
    with open(detail_path, 'r', encoding='utf-8') as f:
        phone_detail = json.load(f)

    data_list = phone_detail.get('data', {}).get('mainSkuList', [])
    prices_map = price_detail.get('data', {}).get('prices', {})
    all_data = []

    for item in data_list:
        sku_code = item.get('skuCode')

        virtual_options = item.get('virtualOptions', [])
        label_one = virtual_options[0].get('optLabel') if len(virtual_options) > 0 else None
        label_two = virtual_options[1].get('optLabel') if len(virtual_options) > 1 else None

        sku_price_info = prices_map.get(sku_code, {})
        sale_price = sku_price_info.get('salePrice')
        original_price = sku_price_info.get('originalPrice')

        all_data.append({
            'sku_code': sku_code,
            'sku_name': item.get('skuName'),
            'color_or_spec': label_one,
            'storage_or_spec': label_two,
            'sale_price': sale_price,
            'original_price': original_price
        })

    print(all_data)
    print(len(all_data))
    return all_data




# import json

# def product_extract():
#     price_path = r'C:\Users\hiren.chauhan\Desktop\HirenGit\oppo_reno\price_detail.json'
#     detail_path = r'C:\Users\hiren.chauhan\Desktop\HirenGit\oppo_reno\phone_detail.json'

#     with open(price_path, 'r', encoding='utf-8') as f:
#         price_detail = json.load(f)
#     with open(detail_path, 'r', encoding='utf-8') as f:
#         phone_detail = json.load(f)

#     data_list = phone_detail.get('data', {}).get('mainSkuList', [])
#     prices_map = price_detail.get('data', {}).get('prices', {})
#     attr_map = phone_detail.get('data', {}).get('attrMap', [])
#     product_name = phone_detail.get('data', {}).get('productName')

#     all_data = []
#     seen_combos = set()

#     # 1) Extract real SKUs as before
#     for item in data_list:
#         sku_code = item.get('skuCode')
#         virtual_options = item.get('virtualOptions', [])
#         label_one = virtual_options[0].get('optLabel') if len(virtual_options) > 0 else None
#         label_two = virtual_options[1].get('optLabel') if len(virtual_options) > 1 else None

#         sku_price_info = prices_map.get(sku_code, {})
#         all_data.append({
#             'sku_code': sku_code,
#             'sku_name': item.get('skuName'),
#             'color_or_spec': label_one,
#             'storage_or_spec': label_two,
#             'sale_price': sku_price_info.get('salePrice'),
#             'original_price': sku_price_info.get('originalPrice')
#         })
#         seen_combos.add((label_one, label_two))

#     # 2) Fill in any color/storage combo that has no real SKU (not offered)
#     if len(attr_map) >= 2:
#         colors = [o['optLabel'] for o in attr_map[0].get('options', [])]
#         storages = [o['optLabel'] for o in attr_map[1].get('options', [])]
#         for color in colors:
#             for storage in storages:
#                 if (color, storage) not in seen_combos:
#                     all_data.append({
#                         'sku_code': None,
#                         'sku_name': product_name,
#                         'color_or_spec': color,
#                         'storage_or_spec': storage,
#                         'sale_price': None,
#                         'original_price': None
#                     })

#     print(all_data)
#     print(len(all_data))
#     return all_data
