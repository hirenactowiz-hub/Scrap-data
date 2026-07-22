import codecs
import json
import os
from parsel import Selector


def extract_default_snippet_data(html, output_file="defaultSnippetData.json"):
    selector = Selector(text=html)
    scripts = selector.xpath("//html/body//script/text()").getall()

    for script in scripts:
        if "defaultSnippetData" not in script:
            continue

        try:
            script = codecs.decode(script, "unicode_escape")
        except Exception:
            pass

        start = script.find('"defaultSnippetData":')
        if start == -1:
            continue

        start = script.find("{", start)
        if start == -1:
            continue

        braces = 0
        end = None

        for i in range(start, len(script)):
            if script[i] == "{":
                braces += 1
            elif script[i] == "}":
                braces -= 1
                if braces == 0:
                    end = i + 1
                    break

        if end is None:
            continue

        json_text = script[start:end]

        try:
            data = json.loads(json_text)

            if os.path.dirname(output_file):
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"Saved JSON to {output_file}")
            return data
        except json.JSONDecodeError as e:
            print("JSON Error:", e)

    print("Target data 'defaultSnippetData' not found in any script tags.")
    return None


html_path = r"C:\Users\hiren.chauhan\Desktop\HirenGit\district_brand_offer\index.html"
if os.path.exists(html_path):
    with open(html_path, "r", encoding="utf-8") as file:
        html_content = file.read()
    extract_default_snippet_data(html_content, r"C:\Users\hiren.chauhan\Desktop\HirenGit\district_brand_offer\all_store_detail.json")
else:
    print(f"Error: HTML file not found at {html_path}")
