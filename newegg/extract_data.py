import re
import json

# ---------------------------
# PATH PARSER
# ---------------------------
def parse_path(path):
    tokens = []
    i = 0

    while i < len(path):

        # Skip dots
        if path[i] == ".":
            i += 1
            continue

        # Normal key
        if path[i] != "[":
            j = i
            while j < len(path) and path[j] not in ".[":
                j += 1
            tokens.append(path[i:j])
            i = j
            continue

        # Inside brackets
        if path[i] == "[":
            j = path.find("]", i)
            content = path[i + 1:j].strip()

            # ['key'] or ["key"]
            if (
                (content.startswith("'") and content.endswith("'"))
                or
                (content.startswith('"') and content.endswith('"'))
            ):
                tokens.append(content[1:-1])

            elif content == "*":
                tokens.append("*")

            else:
                tokens.append(int(content))

            i = j + 1

    return tokens
# ---------------------------
# CORE EXTRACTOR
# ---------------------------
def extract(data, path, safe=False):
    tokens = parse_path(path)

    def walk(obj, remaining):
        if not remaining:
            return obj

        token = remaining[0]
        rest = remaining[1:]

        # -----------------------
        # DICT HANDLING
        # -----------------------
        if isinstance(obj, dict):

            # allow numeric token as string fallback (important fix)
            if isinstance(token, int) and str(token) in obj:
                token = str(token)

            if not isinstance(token, (str, int)):
                raise TypeError(f"Invalid dict key: {token}")

            if token not in obj:
                if safe:
                    return None
                raise KeyError(f"Key not found: {token}")

            return walk(obj[token], rest)

        # -----------------------
        # LIST HANDLING
        # -----------------------
        elif isinstance(obj, list):

            if token == "*":
                return [walk(item, rest) for item in obj]

            if isinstance(token, int):
                if token >= len(obj):
                    if safe:
                        return None
                    raise IndexError(f"Index out of range: {token}")
                return walk(obj[token], rest)

            if safe:
                return None
            raise TypeError(f"Expected list index or '*', got {token}")

        # -----------------------
        # INVALID TYPE
        # -----------------------
        if safe:
            return None
        raise TypeError(f"Cannot traverse type: {type(obj)}")

    return walk(data, tokens)

# ---------------------------
# JSON LOADER
# ---------------------------
def read_json_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return None
    

data=read_json_file(r'C:\Users\hiren.chauhan\Desktop\HirenGit\newegg\cleaned_data.json')

title=extract(data,'__initialState__.ItemDetail.Description.Title')
rating_count=extract(data,'__initialState__.ItemDetail.Review.HumanRating')
fan_size=extract(data,'__initialState__.PropertyCollection.PropertyGroups[0].SelectedProperty.DisplayInfo')
price=extract(data,'__initialState__.ItemDetail.FinalPrice')
discount=extract(data,'__initialState__.ItemDetail.BlackFridaySavePercent')
color=extract(data,'__initialState__.PropertyCollection.PropertyGroups[1].SelectedProperty.DisplayInfo')

product_rating=extract(data,'__initialState__.ItemDetail.Review.RatingOneDecimal')
product_id=extract(data,'__pageInfo__.params.parentItem')

product_url=f'https://www.newegg.com/msi-aio-radiator-size-360-mm-intel-socket-lga-1700-1851-amd-socket-am5-am4/p/{product_id}'

images=[]
for i in extract(data,'__initialState__.ItemDetail.Image.Normal.ImageNameList').split(','):
    images.append(f'https://c1.neweggimages.com/productimage/nb1280/{i}')

BulletDescription=[i for i in extract(data,'__initialState__.ItemDetail.Description.BulletDescription').replace("\r\n", " ").strip().split('.')]


result={}
properties=extract(data,'__initialState__.ItemDetail.DetailSpecificationObject.Groups')
for group in properties:
    group_name = group.get("GroupName")
    properties = group.get("Properties", [])

    if group_name:
        result[group_name] = {
            prop.get("Key"): prop.get("Value")
            for prop in properties
            if prop.get("Key")
        }

data={"product_name": title,
  "product_url": product_url,
  "product_id": product_id,
  "images": images,
  "product_rating_count": rating_count,
  "product_rating": product_rating,
  "variant_type": fan_size,
  "offer_price": price,
  "discount_price": discount,
  "features":BulletDescription,
  "specifications":[result],
  }

with open(r'C:\Users\hiren.chauhan\Desktop\HirenGit\newegg\main_data.json','w')as f :
    json.dump(data,f,indent=4)
