import mysql.connector
import requests
from urllib.parse import urljoin
from parsel import Selector

def extract_links(url, headers):
    payload = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    
    with open(r"C:\Users\hiren.chauhan\Desktop\HirenGit\book_to_scrap\all_product.html", 'w', encoding='utf-8') as f:
        f.write(response.text)

    return response.text

def extract_pages(html_page):
    sel = Selector(text=html_page)
    total_pages = sel.xpath('//li[@class="current"]/text()').re_first(r'of\s+(\d+)')
    return int(total_pages) if total_pages else 1

def extract_all_html_pages(headers, total_pages):
    base_url = "https://books.toscrape.com/catalogue/"
    
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'actowiz', 
        'database': 'book_to_scrap'
    }
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS book_links (
            id INT AUTO_INCREMENT PRIMARY KEY,
            url VARCHAR(512) UNIQUE,
            status VARCHAR(50) DEFAULT 'pending'
        )
    """)
    conn.commit()

    for page in range(1, total_pages + 1):
        url = f"https://books.toscrape.com/catalogue/page-{page}.html"
        response = requests.request("GET", url, headers=headers)
        sel = Selector(text=response.text)
        
        relative_links = sel.xpath('//article[@class="product_pod"]/h3/a/@href').getall()
        
        page_links = []
        for link in relative_links:
            absolute_url = urljoin(base_url, link)
            page_links.append((absolute_url,))
            
        if page_links:
            query = "INSERT IGNORE INTO book_links (url) VALUES (%s)"
            cursor.executemany(query, page_links)
            conn.commit()
        
        print(f"Page {page} processed. Sent {len(page_links)} links to MySQL.")

    cursor.close()
    conn.close()

