import requests


def get_delivery_details(pincode: str, sku: str = "R0744"):
    """Fetches delivery and nearby store details for a given pincode and SKU."""
    url = "https://prod.giva-api.com/getDeliveryTime"

    # Query parameters
    params = {"pin": pincode, "sku": sku, "zippee": "false", "shopify": ""}

    # Headers to mimic the browser request
    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "no-cache",
        "origin": "https://www.giva.co",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "referer": "https://www.giva.co/",
        "sec-ch-ua": '"Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36",
    }

    try:
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error: Server responded with status code {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ An error occurred: {e}")
        return None
    
    
# --- Dynamic User Input ---
if __name__ == "__main__":
    print("--- GIVA Exact Pincode Store Matcher ---")

    while True:
        user_pincode = input("Enter Pincode to search: ").strip()

        if user_pincode.lower() in ["exit", "quit"]:
            print("Exiting program. Goodbye!")
            break

        if not user_pincode:
            print("Please enter a valid pincode.\n")
            continue

        print(f"Fetching data for Pincode: {user_pincode}...")
        data = get_delivery_details(user_pincode)

        if data:
            stores = data.get("nearby_stores", [])

            matched_store = None
            # 1. First, try to find the EXACT pincode match
            for store in stores:
                if store.get("pincode") == user_pincode:
                    matched_store = store
                    break

            # 2. If no exact match, fall back to the 0-index store (if the list isn't empty)
            if not matched_store and stores:
                matched_store = stores[0]

            # 3. Format the output based on what we found
            if matched_store:
                result = {"available": True, "nearby_stores": matched_store['name']}
            else:
                result = {"available": False}

            # Print the exact format
            print("\nResult:")
            print(result)