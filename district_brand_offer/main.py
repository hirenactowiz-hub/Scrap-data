from store import find_html
from extract_slug import extract_slug
from extract_html import extract_html

headers = {
  'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
  'accept-language': 'en-US,en;q=0.9',
  'cache-control': 'no-cache',
  'pragma': 'no-cache',
  'priority': 'u=0, i',
  'referer': 'https://www.district.in/stores/',
  'sec-ch-ua': '"Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'sec-fetch-dest': 'document',
  'sec-fetch-mode': 'navigate',
  'sec-fetch-site': 'same-origin',
  'sec-fetch-user': '?1',
  'upgrade-insecure-requests': '1',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36',
  'Cookie': 'AKA_A2=A; ak_bmsc=3FDD69968366D6F1127B236ED0EA6C41~000000000000000000000000000000~YAAQg/zTFzF9UUufAQAA1ElrhABoh5Yi+5Z5ylZNOEqnpppTbPQ7ap5ZF4ntWDgR/l3YwzlxumXeFA/xiMOMxu1DxbN/uFadjNrsd1MztQwsufQDWnPuchBid9ujLJUf0O9A/R/b6tZSXWCENly9i2MNRkxnR+7G2clGjNsdJcv7XfFjumGXnBQjRmJnbpycKG1q5TpasmV6Z6Kg42ccwqXITiYEo7Ixm6Om4Il/0vXT+K89y1ji2w+n0+peNTYNGnitF4jaDaO9tjbBCuAELhM7IkMERrG54WRQIpKisiJgjkO3CaOp8Y7xjAtYEkYVGsiI7726o5S3AZzzqldakpN7eohZUQfiZ1+FMyMTx6yVyZ9JegCCZVa+DQL6UverTmz4XWW5cGNkmj3NxII=; x-device-id=0f4c566e-0525-4517-a761-282f8b85cbb1; userProfile=; _fbp=fb.1.1784633054445.651101691507043213; _ga=GA1.1.1833712009.1784633055; WZRK_G=ff39576e52e1402ca0d10c04d337a5ec; location=%7B%22distance%22%3A9742.969108469346%2C%22entity_type%22%3A%22LOCATION_ENTITY_TYPE_CITY%22%2C%22fullname%22%3A%22Gurugram%22%2C%22lat%22%3A28.4378221797652%2C%22long%22%3A77.02289976582408%2C%22subtitle%22%3A%22Gurugram%2C%20Haryana%22%2C%22title%22%3A%22Gurugram%22%2C%22id%22%3A1%2C%22cityId%22%3A1%2C%22cityName%22%3A%22Delhi%20NCR%22%2C%22pCityId%22%3A%2257%22%2C%22pCityKey%22%3A%22gurgaon%22%2C%22pCityName%22%3A%22Gurugram%22%2C%22pStateKey%22%3A%22haryana%22%2C%22pStateName%22%3A%22Haryana%22%2C%22placeType%22%3A%22GOOGLE_PLACE%22%2C%22placeId%22%3A%22ChIJN4MGtxAYDTkR-0Yk2TRlhLA%22%2C%22countryId%22%3A%221%22%2C%22subzoneId%22%3A%22645%22%2C%22zoneId%22%3A%222%22%2C%22availableTabsStr%22%3A%22movies%2Cevents%2Cdining%2Cshopping%2Cattraction%2Cplay%22%7D; bm_sv=B77AD693ADC8F49AE46BDADB55566B63~YAAQg/zTFyHNUUufAQAA1sKJhAA5zSINd9dCGj5/XP/MZ2VN0hdy/vnnvXIgKawpYUKQ5vs5Y3dT5F1cTDkz87YVCY8EdqENJ1BRhdOMyvC8ZPqsnNQ3vGJL6dWonEOkS7IBsH0VfqfDGh7d27MA/q+DVUp+IluGq/CYCNWJulSulhomLkHPFZcNfg8+F0r2ATPwlFy0a/Ql/pLRJv3T8tz9ZEkay8C48mNINJ+X7kPYf4FxCHhlEVSpw5LDvHUi0Nk=~1; WZRK_S_846-Z94-RR7Z=%7B%22p%22%3A15%2C%22s%22%3A1784633055%2C%22t%22%3A1784635050%7D; _ga_WDEHDQ2ZK7=GS2.1.s1784633054$o1$g1$t1784635050$j44$l0$h716026210; _gcl_au=1.1.256886571.1784633053.-.-.1784633053.1242654241.1784633054.1784635051; _ga_KHRD29M2W7=GS2.1.s1784633054$o1$g1$t1784635053$j41$l0$h1269097130; _dd_s=aid=edaf1190-eb97-4b6e-bf6a-158543c68748&rum=0&expire=1784635950154; RT="z=1&dm=www.district.in&si=1cee8da5-0500-4d18-809e-318027d79587&ss=mrukfuom&sl=f&tt=ntq&obo=a&rl=1&ld=178kj&r=46ow4ubx&ul=178kj"; bm_sv=B77AD693ADC8F49AE46BDADB55566B63~YAAQrPzTF5Ps7EqfAQAACdmKhAB8tSiH1bVqsGxcBCRkE/xhVYABsyKzztWSvAwSU0OqLo50dwL76GkXYglpzr+siqEPW8DQItFRmGQnOhNqEL0FaRVJ49jWHs9baJWRwaiEUcWIQVqR4TZeUGhz20+TPkZNV5q9au4AIb7lxQSKCgVXGFFlfyDeVEpfBAiQ3oW8CflR7VpYKj9oER50b+zvTl+EmXcRZJyZ1Ype1SUSSuCFy6BUJMIQNcc9ckezEXY=~1'
}

# find_html(
#     urls_list = "https://www.district.in/stores/all-stores-stores-in-gurgaon",
#     headers=headers
# )

urls = extract_slug(
    json_data=r'C:\Users\hiren.chauhan\Desktop\HirenGit\district_brand_offer\all_store_detail.json'
)

extract_html(
    all_store_urls=urls,
    headers=headers
)





