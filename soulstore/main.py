from search_extract import search_list,find_page,listing_list,product_detail
headers = {
  'accept': 'application/json, text/plain, */*',
  'accept-language': 'en-US,en;q=0.9',
  'authorization': 'null',
  'cache-control': 'no-cache',
  'content-type': 'application/json',
  'device-memory': '16',
  'downlink': '10',
  'dpr': '1.5',
  'ect': '4g',
  'origin': 'https://www.thesouledstore.com',
  'pragma': 'no-cache',
  'priority': 'u=1, i',
  'referer': 'https://www.thesouledstore.com/',
  'rtt': '50',
  'sec-ch-device-memory': '16',
  'sec-ch-dpr': '1.5',
  'sec-ch-ua': '"Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'sec-ch-viewport-width': '1280',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-site',
  'u-device-type': '{"type":"Desktop","os":"Windows","source":"Browser"}',
  'u-user-id': 'uid-1785127329847-18157',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36',
  'viewport-width': '1280'
}
search_keyword = "hoodie"

search_all = search_list(
    search_keyword=search_keyword,
    headers=headers
)

page_number = find_page(
    search_keyword=search_keyword
)

product_urls = listing_list(
    search_all=search_keyword,
    page_number=page_number,
    headers=headers
)

product_detail(
    headers=headers,
    product_urls=product_urls
)