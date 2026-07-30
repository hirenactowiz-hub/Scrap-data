import requests
import json
import math
from parsel import Selector
import re
import mysql.connector
from concurrent.futures import ThreadPoolExecutor

def total_page_found(url, headers):
    payload = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    data = json.loads(response.text)

    total_products = data.get('response').get('total_found')
    per_page_product = data.get('response').get('product_count')

    pages = math.ceil(total_products / per_page_product)
    print(f"API Reports: Total Products = {total_products}, Per Page = {per_page_product}, Total Pages = {pages}")
    return pages

def process_single_page(page, headers):
    url = f"https://www.nykaa.com/best-of-beauty/c/21447?page_no={page}&sort=popularity"
    page_urls = []
    
    try:
        response = requests.request("GET", url, headers=headers, data={}, timeout=10)
        sel = Selector(text=response.text)
        script_text = sel.xpath("string(//script[contains(text(), 'window.__PRELOADED_STATE__')])").get()
        
        if script_text:
            json_match = re.search(r'window\.__PRELOADED_STATE__\s*=\s*({.*?});?\s*$', script_text, re.MULTILINE | re.DOTALL)
            if json_match:
                clean_json_string = json_match.group(1)
                json_data = json.loads(clean_json_string)
                
                jsonldatas = json_data.get('jsonLdData', [])
                if len(jsonldatas) > 1:
                    target_data = jsonldatas[1]
                    item_list = target_data.get("itemListElement", [])
                    for element in item_list:
                        url_links = element.get("url")
                        if url_links:
                            page_urls.append(url_links)
    except Exception as e:
        print(f"Error scraping page {page}: {e}")
                        
    save_links_to_mysql(page_urls)
    print(f"Page {page}: Found {len(page_urls)} URLs.")
    return page_urls

def save_links_to_mysql(urls):
    if not urls:
        return
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="actowiz",
        database="nykaa"
    )
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS product_links (
            id INT AUTO_INCREMENT PRIMARY KEY,
            url VARCHAR(755) UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    url_tuples = [(url,) for url in urls]
    cursor.executemany("INSERT IGNORE INTO product_links (url) VALUES (%s)", url_tuples)
    conn.commit()
    cursor.close()
    conn.close()

def run_thread_pool(total_pages, headers):
    all_extracted_urls = []
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        pages_to_scrape = range(1, total_pages + 1)
        results = executor.map(lambda p: process_single_page(p, headers), pages_to_scrape)
        
        for page_urls in results:
            all_extracted_urls.extend(page_urls)
            
    # Calculate and display metrics
    unique_urls = list(set(all_extracted_urls))
    print("\n" + "="*40)
    print(f"Total Scraped URL instances: {len(all_extracted_urls)}")
    print(f"Total Unique URLs found: {len(unique_urls)}")
    print("="*40 + "\n")
            
    return all_extracted_urls


