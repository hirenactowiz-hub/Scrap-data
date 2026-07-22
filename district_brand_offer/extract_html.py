import os
import requests
import mysql.connector
from parsel import Selector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "actowiz",   
    "database": "district_offers",
}


def create_table():
    """Run once — creates the table in the schema you set up in MySQL Workbench."""
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS store_offers (
            id INT AUTO_INCREMENT PRIMARY KEY,
            url VARCHAR(500),
            brand_title VARCHAR(255),
            address VARCHAR(500),
            distance VARCHAR(50),
            category VARCHAR(100),
            sub_category VARCHAR(100),
            timing VARCHAR(100),
            district_pay_offers JSON,
            in_store_offers JSON,
            add_on_offers JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY unique_url (url)
        ) ROW_FORMAT=DYNAMIC;
        """
    )
    conn.commit()
    cursor.close()
    conn.close()
    print("Table ready: store_offers")


def save_to_db(store_list):
    """Insert one store's extracted data into MySQL."""
    import json as json_lib

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT IGNORE INTO store_offers
            (url, brand_title, address, distance, category, sub_category, timing,
             district_pay_offers, in_store_offers, add_on_offers)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            store_list["url"],
            store_list["brand_title"],
            store_list["address"],
            store_list["distance"],
            store_list["category"],
            store_list["sub_category"],
            store_list["timing"],
            json_lib.dumps(store_list["district_pay_offers"], ensure_ascii=False),
            json_lib.dumps(store_list["in_store_offers"], ensure_ascii=False),
            json_lib.dumps(store_list["add_on_offers"], ensure_ascii=False),
        ),
    )
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Saved to DB: {store_list['url']}")


def extract_html(all_store_urls, headers):
    output_dir = (
        r"C:\Users\hiren.chauhan\Desktop\HirenGit\district_brand_offer\source_code"
    )

    os.makedirs(output_dir, exist_ok=True)
    create_table()  # make sure the table exists before inserting

    for url in all_store_urls:
        payload = {}
        response = requests.request("GET", url, headers=headers, data=payload)

        slug = url.rstrip("/").split("/")[-1]
        file_name = f"{slug}.html"

        file_path = os.path.join(output_dir, file_name)

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(response.text)
            # print(f"Saved: {file_name}")

        data = store_data(response.text, url)
        save_to_db(data)


def store_data(response_data, url):

    parsel = Selector(text=response_data, encoding='utf-8')

    brand_title = parsel.xpath(
        "//*[self::h2 or self::h3][contains(@class,'dds-tracking-tight')]/text()"
    ).get()
    address = parsel.xpath(
        "//span[contains(@class,'dds-truncate')]/text()"
    ).get()
    distance = parsel.xpath(
        "//span[contains(text(),' km')]/text()"
    ).get()

    info_spans = parsel.xpath(
        "//div[contains(@class,'dds-flex-1')]"
        "[.//span[contains(text(),' km')]]"
        "//span[not(contains(text(),' km'))"
        " and not(contains(@class,'dds-truncate'))"
        " and text()!='|' and text()!='.']/text()"
    ).getall()
    info_spans = [t.strip() for t in info_spans if t.strip()]

    status_idx = next(
        (i for i, t in enumerate(info_spans) if t in ("Open", "Closed")),
        len(info_spans),
    )
    cat_chunk = info_spans[:status_idx]
    category = cat_chunk[0] if len(cat_chunk) >= 1 else None
    sub_category = cat_chunk[1] if len(cat_chunk) >= 2 else None
    timing = info_spans[status_idx + 1] if status_idx + 1 < len(info_spans) else None

    def extract_offer_section(heading_text):

        offers = []
        heading_spans = parsel.xpath(
            f"//span[contains(@class,'dds-font-semibold') and normalize-space(text())='{heading_text}']"
        )
        for h in heading_spans:
            block = h.xpath(
                "ancestor::div[.//div[contains(@class,'dds-rounded-[16px]') "
                "and contains(@class,'dds-border-solid')]][1]"
            )
            if not block:
                continue
            cards = block[0].xpath(
                ".//div[contains(@class,'dds-rounded-[16px]') and contains(@class,'dds-border-solid')]"
            )
            for card in cards:
                spans = card.xpath(".//span/text()").getall()
                spans = [s.strip() for s in spans if s.strip()]
                offer_type = spans[0] if len(spans) > 0 else None
                offer_detail = spans[1] if len(spans) > 1 else None
                if offer_type and offer_detail:
                    offers.append({"offer_type": offer_type, "detail": offer_detail})
        return offers

    district_pay_offers = extract_offer_section("District pay offers")
    in_store_offers = extract_offer_section("In Store Offers")
    add_on_offers = extract_offer_section("Add on offers")

    store_list = {
        'url': url,
        'brand_title': brand_title,
        'address': address,
        'distance': distance,
        'category': category,
        'sub_category': sub_category,
        'timing': timing,
        'district_pay_offers': district_pay_offers,
        'in_store_offers': in_store_offers,
        'add_on_offers': add_on_offers,
    }
    # print(store_list)
    return store_list