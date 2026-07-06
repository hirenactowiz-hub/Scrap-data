from parsel import Selector
import json

with open(
    r'C:\Users\hiren.chauhan\Desktop\HirenGit\book_xpath\all_book.html',
    'r',
    encoding='utf-8'
) as file:
    html = file.read()

data = Selector(text=html)

categories = []
base_url = "https://books.toscrape.com/"

for category in data.xpath('//aside//ul/li/ul/li/a'):
    categories.append({
        "name": category.xpath('normalize-space(text())').get(),
        "url": base_url + category.xpath('./@href').get()
    })

print(len(categories))
with open(r"C:\Users\hiren.chauhan\Desktop\HirenGit\book_xpath\links.json", "w", encoding="utf-8") as f:
    json.dump(categories, f, indent=4, ensure_ascii=False)