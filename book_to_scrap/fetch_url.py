from concurrent.futures import ThreadPoolExecutor
import mysql.connector
from parsel import Selector
import requests
import time


def setup_database_tables():
    db_config = {
        "host": "localhost",
        "user": "root",
        "password": "actowiz",
        "database": "book_to_scrap",
        "auth_plugin": "mysql_native_password"
    }
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS book_links (
            id INT AUTO_INCREMENT PRIMARY KEY,
            url TEXT NOT NULL,
            status VARCHAR(50) DEFAULT 'pending'
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS book_details (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255),
            price VARCHAR(50),
            stock VARCHAR(100),
            description TEXT,
            book_img TEXT,
            upc VARCHAR(100),
            product_type VARCHAR(100),
            tax VARCHAR(50),
            reviews VARCHAR(50)
        );
    """)

    conn.commit()
    cursor.close()
    conn.close()


def fetch_links_by_status(status_filter="pending"):
    db_config = {
        "host": "localhost",
        "user": "root",
        "password": "actowiz",
        "database": "book_to_scrap",
        "auth_plugin": "mysql_native_password"
    }
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    query = "SELECT id, url, status FROM book_links WHERE status = %s"
    cursor.execute(query, (status_filter,))
    records = cursor.fetchall()
    cursor.close()
    conn.close()
    return records


def save_book_details_and_update_status(data, link_id):
    db_config = {
        "host": "localhost",
        "user": "root",
        "password": "actowiz",
        "database": "book_to_scrap",
        "auth_plugin": "mysql_native_password"
    }
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    insert_query = """
        INSERT INTO book_details (title, price, stock, description, book_img, upc, product_type, tax, reviews)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    insert_values = (
        data["title"],
        data["price"],
        data["stock"],
        data["description"],
        data["book_img"],
        data["upc"],
        data["product_type"],
        data["tax"],
        data["reviews"]
    )
    cursor.execute(insert_query, insert_values)

    update_query = "UPDATE book_links SET status = 'success' WHERE id = %s"
    cursor.execute(update_query, (link_id,))

    conn.commit()
    cursor.close()
    conn.close()


def fetch_single_page(record, headers):
    url = record["url"]
    link_id = record["id"]

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return None

    sel = Selector(text=response.text)

    title = sel.xpath('//div[contains(@class, "product_main")]/h1/text()').get(default="")
    price = sel.xpath('//p[contains(@class, "price_color")]/text()').get(default="")
    stock = sel.xpath('normalize-space(//p[contains(@class, "availability")])').get(default="")
    description = sel.xpath('//div[@id="product_description"]/following-sibling::p/text()').get(default="")
    book_img = sel.xpath('//div[@id="product_gallery"]//div[contains(@class, "item")]/img/@src').get(default="")

    upc = sel.xpath('//table[contains(@class, "table-striped")]//tr[th[text()="UPC"]]/td/text()').get(default="")
    product_type = sel.xpath('//table[contains(@class, "table-striped")]//tr[th[text()="Product Type"]]/td/text()').get(
        default="")
    tax = sel.xpath('//table[contains(@class, "table-striped")]//tr[th[text()="Tax"]]/td/text()').get(default="")
    reviews = sel.xpath('//table[contains(@class, "table-striped")]//tr[th[text()="Number of reviews"]]/td/text()').get(
        default="")

    data = {
        "title": title.strip(),
        "price": price.strip(),
        "stock": stock.strip(),
        "description": description.strip(),
        "book_img": book_img.strip(),
        "upc": upc.strip(),
        "product_type": product_type.strip(),
        "tax": tax.strip(),
        "reviews": reviews.strip()
    }

    save_book_details_and_update_status(data, link_id)
    print(f"Success saved -> {url}")
    return data


def extract_detail_pages(records, headers):
    start_time = time.perf_counter()
    max_workers = 20

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        list(executor.map(lambda r: fetch_single_page(r, headers), records))

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"\nTask completed in: {elapsed_time:.4f} seconds")
