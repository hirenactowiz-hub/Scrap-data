import requests
import os
def find_html(urls_list,headers):
  for url in urls_list:
    payload = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    slug = url.split("/")[-1]
    file_name = f"{slug}.html"

    output_dir = (
        r"C:\Users\hiren.chauhan\Desktop\HirenGit\district_brand_offer"
    )
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, file_name)

    # 3. Save the specific content to its own unique file
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(response.text)
    print(f"Successfully saved: {file_name}")
