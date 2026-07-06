from parsel import Selector
import json

# Read HTML file
with open(r"C:\Users\hiren.chauhan\Desktop\HirenGit\buyplastick\abs_plastic_sheet.html","r",encoding="utf-8") as file:
    html = file.read()

data = Selector(text=html)

product = {
    "title": data.xpath('//div[@class="productView-product"]//h1/text()').get(),
    "price": data.xpath('//span[@class="price price--withoutTax"]/text()').get(),
    "sku": data.xpath('//dd[@class="productView-info-value"]/text()').get(),
}

# ---------------- Product Details -----------

details = {}

for field in data.xpath('//div[@data-product-attribute="set-rectangle"]'):
    key = field.xpath('normalize-space(label/text()[1])').get().replace(':', '').replace(' ', '_').lower()
    value = field.xpath('normalize-space(.//input[@checked]/following-sibling::label/span)').get()

    details[key] = value

product["product_details"] = details
# ---------------- Images ----------------

images = []
for img in data.xpath('//figure[@class = "productView-image"]/div/a/@href'):
    images.append(img.get())

product["img"] = images

# ---------------- Overview ----------------

product["description"] = data.xpath('//div[@id="tab-overview"]/div/p/text()').get()

# Advantages
advantages = []
for item in data.xpath('//div[@id="tab-overview"]/div/ul[1]/li/text()'):
    advantages.append(item.get())

product["advantage"] = advantages

# Applications
applications = []
for item in data.xpath('//div[@id="tab-overview"]/div/ul[2]/li/text()'):
    applications.append(item.get())

product["applications"] = applications

# ---------------- Final Result ----------------

result = {
    "product": product,
}

# Save to JSON
with open(
    r"C:\Users\hiren.chauhan\Desktop\HirenGit\buyplastick\buyplastick_output.json",
    "w",
    encoding="utf-8"
) as file:
    json.dump(result, file, indent=4, ensure_ascii=False)

print(json.dumps(result, indent=4, ensure_ascii=False))