from books_links import extract_all_html_pages, extract_links, extract_pages
from fetch_url import extract_detail_pages, fetch_links_by_status, setup_database_tables

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36'
}

setup_database_tables()

html_pages = extract_links(
    url="https://books.toscrape.com/",
    headers=headers
)

total_pages = extract_pages(
    html_page=html_pages
)

# extract_all_html_pages(
#     headers=headers,
#     total_pages=total_pages
# )

records = fetch_links_by_status("pending")

extract_detail_pages(
    headers=headers,
    records=records
)
