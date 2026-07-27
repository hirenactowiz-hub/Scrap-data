import requests
import json
import re
from parsel import Selector
import math
import urllib3

urllib3.disable_warnings()

def search_list(headers, search_keyword):
    url = f"https://api.thesouledstore.com/api/v2/pre-order/products/search/auto-suggest?keyword={search_keyword}&is_exclusive=0&show_upgrade=0&is_ab_visible=true&gender_type=1"
    response = requests.request("GET", url, headers=headers, data={},verify=False)
    data = json.loads(response.text)
    search_all = []
    for item in data:
        if item.get('doctype') != 'POPULAR_PRODUCTS':
            search_item = item.get('autosuggest')
            if search_item:  
                search_all.append(search_item)
    return search_all

def find_page(search_keyword):
    url = "https://api.thesouledstore.com/api/v2/pre-order/products/search"

    payload = json.dumps({
        "filters": {},
        "keyword": f"{search_keyword}",
        "page": 1,
        "offset": 52,
        "is_exclusive": 0,
        "show_upgrade": 0,
        "is_ab_visible": True,
        "showSelectedFiltersData": {
            "agegroup": True
        },
        "isKids": False,
        "gender_type": 1,
        "gender_filter_removed": False
    })
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'authorization': 'null',
        'content-type': 'application/json',
        'device-memory': '8',
        'downlink': '10',
        'dpr': '1.5',
        'ect': '4g',
        'origin': 'https://www.thesouledstore.com',
        'priority': 'u=1, i',
        'referer': 'https://www.thesouledstore.com/',
        'rtt': '50',
        'sec-ch-device-memory': '8',
        'sec-ch-dpr': '1.5',
        'sec-ch-ua': '"Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-ch-viewport-width': '1280',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'u-device-type': '{"type":"Desktop","os":"Windows","source":"Browser"}',
        'u-user-id': 'uid-1785127328951-8701',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36',
        'viewport-width': '1280'
    }

    response = requests.request("POST", url, headers=headers, data=payload,verify=False)
    print(response.status_code)

    data=json.loads(response.text)

    page_number=math.ceil(data.get('numberOfProducts')/52)

    return page_number

def listing_list(search_all,page_number, headers):
    url = "https://api.thesouledstore.com/api/v2/pre-order/products/search"
    
    collected_urls = []
    for i in range(1,page_number+1):
        payload = json.dumps({
            "filters": {},
            "keyword": search_all, 
            "page": int(f"{i}"),
            "offset": 52,
            "is_exclusive": 0,
            "show_upgrade": 0,
            "is_ab_visible": True,
            "showSelectedFiltersData": {"agegroup": True},
            "isKids": False,
            "gender_type": 1,
            "gender_filter_removed": False
        })
        response = requests.request("POST", url, headers=headers, data=payload,verify=False)
        if response.status_code == 200:
            response_data = json.loads(response.text)
            products = response_data.get('products', [])
            for product in products:
                slug = product.get('product_slug')
                if slug:
                    product_url = f"https://www.thesouledstore.com/product/{slug}?get=1"
                    product['web_url'] = product_url
                    collected_urls.append(product_url)
                    print(f"[URL] {product_url}") 
    print(len(collected_urls))
    return collected_urls

def parse_add_desc(html_content: str) -> dict:
    # 1. Clean HTML tags and standardize line breaks
    cleaned = html_content.replace("&nbsp;", " ").replace("\xa0", " ")
    cleaned = re.sub(r"<br\s*/?>", "\n", cleaned, flags=re.IGNORECASE)

    selector = Selector(text=cleaned)
    lines = [line.strip() for line in selector.xpath("//text()").getall() if line.strip()]
    full_text = "\n".join(lines)

    # 2. Extract specific metadata before section splitting
    email_match = re.search(r"[\w\.-]+@[\w\.-]+", full_text)
    phone_match = re.search(r"\+?91\s*\d{2,4}[-\s]?\d{6,8}", full_text)

    email = email_match.group(0) if email_match else None
    phone = phone_match.group(0) if phone_match else None

    # 3. Clean full text by removing email/phone lines to keep sections distinct
    clean_lines = []
    for line in lines:
        # Skip lines that are just contact details
        if (email and email in line) or "Customer care" in line or "tel:" in line:
            continue
        clean_lines.append(line)

    cleaned_text = "\n".join(clean_lines)

    # 4. Split by section headers
    keys = ["Material & Care", "Country of Origin", "Manufactured & Sold By"]
    pattern = rf"({'|'.join(re.escape(k) for k in keys)}):?"

    parts = re.split(pattern, cleaned_text, flags=re.IGNORECASE)

    result = {}
    i = 1
    while i < len(parts):
        key = parts[i].strip().rstrip(":")
        val = parts[i + 1].strip() if i + 1 < len(parts) else ""

        # Format multi-line values cleanly
        section_lines = [l.strip() for l in val.split("\n") if l.strip()]
        result[key] = " ".join(section_lines)
        i += 2

    # 5. Attach clean standalone contact fields
    if email:
        result["Email"] = email
    if phone:
        result["Customer Care"] = phone

    return result

def get_product_details(slug, headers):
    
    url = f"https://api.thesouledstore.com/api/v2/static/product/{slug}?gender_type=1"

    response = requests.get(url, headers=headers,verify=False)
    if response.status_code == 200:
        detail_data = response.json()
        product_title = detail_data.get("product", {})
        product_category = detail_data.get("category")
        imges = detail_data.get("images")

        img_link = []
        for img in imges:
            base_img_url = f"https://prod-img.thesouledstore.com/public/theSoul/uploads/catalog/product/{img}?w=480&dpr=2"
            img_link.append(base_img_url)
        
        html_data = detail_data.get("add_desc", {})
        
        
        output = {
            'title': product_title,
            'category': product_category,
            'img_link':img_link,
            'product_detail':parse_add_desc(html_data)
        }
        return output


def get_product_price(slug):
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'device-memory': '16',
        'downlink': '10',
        'dpr': '1.5',
        'ect': '4g',
        'origin': 'https://www.thesouledstore.com',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': 'https://www.thesouledstore.com/',
        'rtt': '0',
        'sec-ch-device-memory': '16',
        'sec-ch-dpr': '1.5',
        'sec-ch-ua': '"Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-ch-viewport-width': '1280',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36',
        'viewport-width': '1280',
        'Cookie': '_scid=Waym8TVMFdxSX6A1goe0Ao-xYnjja8hg; unbxd.userId=uid-1785127329847-18157; _gcl_au=1.1.1947181253.1785127331; _ga=GA1.1.1795366617.1785127331; _clck=1b907rr%5E2%5Eg83%5E0%5E2399; _fbp=fb.1.1785127330967.637834645524538577; _sctr=1%7C1785090600000; unbxd.visitId=visitId-1785134705826-60578; unbxd.visit=repeat; _uetsid=88453a30897511f1a81d71fd971b3b74; _uetvid=884536b0897511f1876f013157cb0627; _clsk=1tjzg3r%5E1785136978995%5E27%5E1%5El.clarity.ms%2Fcollect; _ga_NXPBDLCSFK=GS2.1.s1785134705$o3$g1$t1785137034$j3$l0$h0; _ga_4W6E0TYD2Y=GS2.1.s1785134705$o3$g1$t1785137034$j3$l0$h0; _scid_r=fSym8TVMFdxSX6A1goe0Ao-xYnjja8hgTX_BTA; __tr_luptv=1785137034689'
        }
    url = f"https://api.thesouledstore.com/api/v2/product/{slug}/pricing"

    try:
        response = requests.get(url, headers=headers,verify=False)

        if response.status_code == 200:
            price_data = response.json()
            return price_data.get("price")
    except requests.RequestException as e:
        print(f"Price API error: {e}")

    return None

def get_product_inventory(slug):
    url = f"https://api.thesouledstore.com/api/v2/product/{slug}/inventory"
    headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'device-memory': '16',
    'downlink': '10',
    'dpr': '1.5',
    'ect': '4g',
    'origin': 'https://www.thesouledstore.com',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://www.thesouledstore.com/',
    'rtt': '150',
    'sec-ch-device-memory': '16',
    'sec-ch-dpr': '1.5',
    'sec-ch-ua': '"Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-ch-viewport-width': '1280',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36',
    'viewport-width': '1280',
    'Cookie': '_scid=Waym8TVMFdxSX6A1goe0Ao-xYnjja8hg; unbxd.userId=uid-1785127329847-18157; _gcl_au=1.1.1947181253.1785127331; _ga=GA1.1.1795366617.1785127331; _clck=1b907rr%5E2%5Eg83%5E0%5E2399; _fbp=fb.1.1785127330967.637834645524538577; _sctr=1%7C1785090600000; _uetsid=88453a30897511f1a81d71fd971b3b74; _uetvid=884536b0897511f1876f013157cb0627; _clsk=199qcm3%5E1785144810559%5E2%5E1%5El.clarity.ms%2Fcollect; _ga_4W6E0TYD2Y=GS2.1.s1785144835$o4$g0$t1785144835$j60$l0$h0; _ga_NXPBDLCSFK=GS2.1.s1785144835$o4$g0$t1785144835$j60$l0$h0; _scid_r=fiym8TVMFdxSX6A1goe0Ao-xYnjja8hgTX_BTQ; __tr_luptv=1785144839195'
    }

    
    response = requests.get(url, headers=headers,verify=False)
    sizes = []
    if response.status_code == 200:
        size_data = response.json()
        for variant in size_data.get('variant', []):
            for attribute in variant.get('attributes', []):
                name = attribute.get('name')
                if name == 'size':
                    value = attribute.get('value')
                    if value and str(value).strip():
                        sizes.append(value)
        return sizes



def product_detail(headers, product_urls):
    product_data = []

    for item_url in product_urls:
        match = re.search(r"/product/([^?#/]+)", item_url)
        if match:
            slug = match.group(1)

            details = get_product_details(slug, headers)
            product_price = get_product_price(slug)
            product_size = get_product_inventory(slug)

            if details:
                product_item = {
                    **details,
                    "url":item_url,
                    "price": product_price,
                    "size": product_size
                }
                product_data.append(product_item)
                print(f"Sucessfull Url :{item_url}")
            
            # print(product_data)

    with open(r"C:\Users\hiren.chauhan\Desktop\HirenGit\soulstore\products.json", "w", encoding="utf-8") as f:
        json.dump(product_data, f, indent=4, ensure_ascii=False)

    return product_data
