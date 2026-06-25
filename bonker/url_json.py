import json
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(current_dir, "bonker.json")

with open(json_path, "r") as f:
    data = json.load(f)

for product in data["products"]:
    for variant in product["variants"]:
        variant["url"] = ("https://www.bonkerscorner.com/products/" + product["handle"] + "?variant=" + str(variant["id"]))

output_path = os.path.join(current_dir, "output.json")
with open(output_path, "w") as f:
    json.dump(data, f, indent=4)