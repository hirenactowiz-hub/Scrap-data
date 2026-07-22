import json
def extract_slug(json_data):
    with open(json_data,'r',encoding='utf-8') as f:
        data = json.load(f)
    all_store_urls = []

    store = data['EDSResponse']
    for rail in store['rails']:
        for item in rail['items']:
            slug = item.get('ItemDetails').get('StoreData').get('slug')
            url = 'https://www.district.in/stores/'+slug
            all_store_urls.append(url)
    return all_store_urls



