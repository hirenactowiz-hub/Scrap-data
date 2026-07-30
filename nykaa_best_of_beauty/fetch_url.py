import mysql.connector
import requests
from parsel import Selector
import re
import json

def fetch_url():
    db_config = {
        "host": "localhost",
        "user": "root",
        "password": "actowiz",
        "database": "nykaa",
        "auth_plugin": "mysql_native_password"
    }
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    query = "SELECT id, url FROM product_links"
    cursor.execute(query)
    records = cursor.fetchall()
    cursor.close()
    conn.close()
    # print(records)
    return records

def html_and_json(records,headers):
    for item in records:
        url = item.get('url')
        product_id = item.get("id")
        payload = {}
        response = requests.request("GET", url, headers=headers, data=payload)

        sel = Selector(text=response.text)

        script_xpath = "string(//script[contains(text(), 'window.__PRELOADED_STATE__')])"
        script_text = sel.xpath(script_xpath).get()

        if script_text:
            json_match = re.search(
                r"window\.__PRELOADED_STATE__\s*=\s*({.*?});?\s*$",
                script_text,
                re.MULTILINE | re.DOTALL,
            )

            if json_match:
                clean_json_string = json_match.group(1)
                json_data = json.loads(clean_json_string)

                file_name = f"product_{product_id}.json"
                with open(file_name, "w", encoding="utf-8") as f:
                    json.dump(json_data, f, indent=4, ensure_ascii=False)

                print(f"Successfully saved json data to {file_name}")
        print(response.text)
