import json
import os
from parsel import Selector


def extract_gb_raw_data(selector):
    script_content = selector.xpath(
        '//script[contains(text(), "window.gbRawData")]/text()'
    ).get()

    if script_content:
        try:
            right_side = script_content.split("window.gbRawData =", 1)[1].strip()

            extracted_json, _ = json.JSONDecoder().raw_decode(right_side)
            return extracted_json

        except (IndexError, ValueError) as e:
            print(f"Extraction or parsing split error: {e}")
            return None

    return None


def main():

    file_path = r"C:\Users\hiren.chauhan\Desktop\data\shein\shein.html"

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            html_content = file.read()
    except FileNotFoundError:
        print(f"Error: The target resource at {file_path} was not found.")
        return

    selector = Selector(text=html_content)

    view_source_lines = selector.xpath('//td[@class="line-content"]')
    if view_source_lines:
        reconstructed_html = ""
        for line in view_source_lines:
            reconstructed_html += "".join(line.xpath('.//text()').getall()) + "\n"
        selector = Selector(text=reconstructed_html)

    extracted_json = extract_gb_raw_data(selector)

    if extracted_json:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_file_path = os.path.join(script_dir, "extracted_shein.json")

        with open(output_file_path, "w", encoding="utf-8") as json_file:
            json.dump(extracted_json, json_file, indent=4, ensure_ascii=False)

        print(f"Success! Perfect extraction using raw_decode. File saved to:")
        print(output_file_path)
    else:
        print("Failed to isolate or parse the target JSON data.")


if __name__ == "__main__":
    main()







