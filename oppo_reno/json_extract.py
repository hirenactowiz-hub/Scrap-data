import requests
import json

def json_extract(url,headers,payload):

    response = requests.request("POST", url, headers=headers, data=payload)
    data = json.loads(response.text)
    with open(r"C:\Users\hiren.chauhan\Desktop\HirenGit\oppo_reno\price.json", "w") as file:
        json.dump(data, file, indent=4)
    
    return data

