from parsel import Selector
import json,os,re
from collections import OrderedDict
import gzip
from pathlib import Path

# with open(r"D:\Practice\plastic\abs_plastic_sheet.html", "r", encoding="utf-8") as file:
#     html = file.read()

# sel = Selector(text=html)

def title(sel):
    return sel.xpath('//div[@class="productView-product"]/h1/text()').get(default=None)

def price(sel):
    return sel.xpath('//span[@class="price price--withoutTax"]/text()').get(default=None)

def sku(sel):
    return sel.xpath('//div[@class="productView-info--wrap productView-info--sku"]//dd[@class="productView-info-value"]/text()').get(default=None)

def attribute(sel):
    attributes = {}

    for field in sel.xpath('//div[contains(@class,"form-field")]'):

        key = field.xpath('./label/text()[normalize-space()]').get('')
        key = key.strip().rstrip(':')

    # Selected radio button
        value = field.xpath(
            './/input[@checked]/following-sibling::label//span[contains(@class,"form-option-variant") or contains(@class,"swatch-label")]/text()'
        ).get()

        if value:
            attributes[key] = value.strip()
    return attributes if attributes else None

def clean_text(text):
    text = re.sub(r"\s+", " ", text)

    text = re.sub(r"Cut\s*Tolerance.*?(?=\.|$)", "", text, flags=re.I)

    # Remove tolerance values - inch/quote symbol ab OPTIONAL hai
    # matches: -0.010", +.030, 1.5", .25, -0.0, 1/4" etc.
    text = re.sub(r"[+\-−±]?\s*\d*\.\d+\s*[\"″]?", "", text)
    text = re.sub(r"[+\-−±]?\s*\d+\s*[\"″]", "", text)

    # Remove "/ number" style leftovers (e.g. "/ -0.010", "/.25")
    text = re.sub(r"/\s*[+\-−±]?\s*\d*\.?\d*", "", text)

    # Ab bache hue standalone symbols (+, -, ±, /) jo kisi word se attached nahi hain, hata do
    text = re.sub(r"(?<!\w)[+\-−±/](?!\w)", "", text)

    # Beech mein bache stray "." ya "," jo akela token hai (spaces ke beech), hata do
    text = re.sub(r"\s+[.,]\s+", " ", text)

    # Extra spaces collapse
    text = re.sub(r"\s{2,}", " ", text)

    return text.strip(" :,/.\n\t")

def overview(sel):
    root = sel.xpath('//div[@id="tab-overview"]/div')

    if not root:
        return None

    data = {}

    description = []
    current_title = None
    current_content = []

    def save_section():
        """Save collected content for current section."""

        nonlocal current_title, current_content

        if not current_title or not current_content:
            return

        # -------- key/value -------- #

        if all(isinstance(i, tuple) for i in current_content):
            data[current_title] = {k: v for k, v in current_content}
            return

        # -------- list -------- #

        if len(current_content) > 1:
            data[current_title] = current_content
        else:
            data[current_title] = current_content[0]

    # ------------------------------------------------------------ #

    for node in root.xpath('./*'):

        tag = node.root.tag.lower()

        # ---------------- Heading ---------------- #

        if tag in ("h1", "h2", "h3", "h4", "h5"):

            save_section()

            current_title = clean_text(
                " ".join(node.xpath(".//text()").getall())
            ).lower()

            current_content = []

            continue

        # ---------------- Paragraph ---------------- #

        if tag == "p":

            txt = clean_text(
                " ".join(node.xpath(".//text()").getall())
            )

            if not txt:
                continue

            if current_title is None:
                description.append(txt)
            else:
                current_content.append(txt)

        # ---------------- UL / OL ---------------- #

        elif tag in ("ul", "ol"):

            for li in node.xpath("./li"):

                txt = clean_text(
                    " ".join(li.xpath(".//text()").getall())
                )

                if txt:
                    current_content.append(txt)

        # ---------------- TABLE ---------------- #

        elif tag == "table":

            for tr in node.xpath(".//tr"):

                cells = tr.xpath("./th|./td")

                if len(cells) >= 2:

                    key = clean_text(
                        " ".join(cells[0].xpath(".//text()").getall())
                    )

                    value = clean_text(
                        " ".join(cells[1].xpath(".//text()").getall())
                    )

                    if key and value:
                        current_content.append((key, value))

        # ---------------- DL ---------------- #

        elif tag == "dl":

            keys = node.xpath("./dt")
            vals = node.xpath("./dd")

            for k, v in zip(keys, vals):

                key = clean_text(
                    " ".join(k.xpath(".//text()").getall())
                )

                value = clean_text(
                    " ".join(v.xpath(".//text()").getall())
                )

                if key and value:
                    current_content.append((key, value))
    if description:
        data["description"] = (
            description[0]
            if len(description) == 1
            else description
        )


    save_section()

    result = OrderedDict()

    if description:
        result["description"] = (
            description[0] if len(description) == 1 else description
        )

    result.update(data)

    return dict(result)

def image(sel):
    images = sel.xpath('//a[@class="productView-thumbnail-link"]/@href').getall()
    return images if images else None

def product(html, file_path):
    sel = Selector(text=html)

    return {
        'title': title(sel),
        'price': price(sel),
        'sku': sku(sel),
        'attributes': attribute(sel),
        'overview': overview(sel),
        'images': image(sel)
    }

# path=os.path.join(r'D:\Practice\plastic','product_detail.json')

# with open(path,'w',encoding='utf-8')as f:
#     json.dump(product,f,indent=4,ensure_ascii=False)

def process_gz_folder(folder_path, process_function, output_folder):
    folder = Path(folder_path)
    output_dir = Path(output_folder)
    output_dir.mkdir(parents=True, exist_ok=True)

    for gz_file in folder.rglob("*.gz"):
        try:
            with gzip.open(gz_file, "rt", encoding="utf-8", errors="ignore") as f:
                html = f.read()

            result = process_function(html, gz_file)

            output_file = output_dir / f"{gz_file.stem}.json"

            with open(output_file, "w", encoding="utf-8") as out:
                json.dump(result, out, ensure_ascii=False, indent=4)

            print(f"✓ Saved: {output_file}")

        except Exception as e:
            print(f"✗ {gz_file.name}: {e}")

folder=r"C:\Users\hiren.chauhan\Desktop\HirenGit\buyplastick\buplastic"
func=product
output=r'C:\Users\hiren.chauhan\Desktop\HirenGit\buyplastick\buplastic_output'

process_gz_folder(folder,func,output)