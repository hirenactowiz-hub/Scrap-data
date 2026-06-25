import json
import os

file = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(file, "lululemon.json")

with open(file_path ,'r') as f:
    data = json.load(f)
products = []


for variant in data.get("hasVariant",{}):
    for offer in variant.get('offers',[]):
        product_price = offer.get('price',0.0)
        if product_price:
            break
        
    product = {
        'url' : variant.get('url',''),
        'id' : variant.get('sku',),
        'name' : variant.get('name',''),
        'price' : product_price,
        'colour' : variant.get('color',''),
        'size' : variant.get('size',''),
        'image' : variant.get('image','')
    }
    products.append(product)

# print(json.dumps(products, indent=4))

output_path = os.path.join(file, "output_lululemon.json")
with open(output_path, "w") as f:
    json.dump(products, f, indent=4)