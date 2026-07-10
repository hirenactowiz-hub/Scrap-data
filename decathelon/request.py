import requests
import json

r = requests.get('https://www.decathlon.in/c/flipflops-sandals-721529?inStock=1')
# print(r.json())
# print(r.text)

with open(r'C:\Users\hiren.chauhan\Desktop\HirenGit\decathelon\output_json_path.html', "w", encoding="utf-8") as out_file:
    json.dump(r.text, out_file, indent=4, ensure_ascii=False)
