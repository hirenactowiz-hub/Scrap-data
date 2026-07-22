import os
import re
import json
import requests
import time
# ==========================================
# 1. SETUP PATHS & CONFIGURATION
# ==========================================
# Root directory
base_dir = r"C:\Users\hiren.chauhan\Desktop\HirenGit\nykaa-foxtale"

# Target subfolders for organization
html_dir = os.path.join(base_dir, "source_code")
json_dir = os.path.join(base_dir, "extracted_json")

# Ensure directories exist
os.makedirs(html_dir, exist_ok=True)
os.makedirs(json_dir, exist_ok=True)

# URL configuration
url = "https://www.nykaa.com/brands/foxtale/c/27361"

headers = {
  'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
  'accept-language': 'en-US,en;q=0.9',
  'cache-control': 'no-cache',
  'pragma': 'no-cache',
  'priority': 'u=0, i',
  'sec-ch-ua': '"Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'sec-fetch-dest': 'document',
  'sec-fetch-mode': 'navigate',
  'sec-fetch-site': 'none',
  'sec-fetch-user': '?1',
  'upgrade-insecure-requests': '1',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36',
  'Cookie': 'run=5; EXP_REVIEW_COLLECTION=1; D_LST=1; D_PDP=1; bcookie=a6f4a3e7-2f4b-4884-89c3-2ab11c65b452; EXP_OL=DEFAULT; EXP_AB_NEW_SHOPPING_BAG=A; PHPSESSID=NfAo5dMTqwrRiXs1784007257066; PRIVE_TIER=null; head_data_react={"id":"","nykaa_pro":false,"group_id":""}; pro=false; EXP_H_F_M_M_S_P=1; EXP_C_W_P_M=1; EXP_H_F_M_W=1; EXP_H_F_M_S=1; EXP_H_F_M_P_S=1; _gcl_au=1.1.1246408184.1784007259; _gid=GA1.2.1184043147.1784007260; _pin_unauth=dWlkPU1UZzVZVEpoTW1ZdE5tSTFaQzAwWlROaExUbGlZbVF0TURNNFlqZ3hNRFpoTkdJMA; _clck=1fnwx7r%5E2%5Eg7q%5E0%5E2386; WZRK_G=14ad2e56bd074b20848a8daaeaf11b9f; storeId=nykaa; EXP_AB_CAB_VERTICAL=DEFAULT; EXP_AB_SAVINGS_SHELF=DEFAULT; EXP_AB_NYKAA_NOW_RAAP=A; EXP_AB_NYKAA_NOW_CART=A; EXP_AB_NYKAA_NOW_FILTER=DEFAULT; EXP_AB_CART_OFFERS=A; EXP_AB_PARTIAL_CHECKOUT=A; EXP_AB_EMAIL_VERIFICATION_REVAMP=A; EXP_AB_DWEB_SHOPPING_BAG_URL=A; EXP_NEW_SIGN_UP=DEFAULT; EXP_CART_GRATIFICATION_POPUP=B; EXP_ITEM_DISCOUNT=A; EXP_ORDERS_REVAMP=A; EXP_CART_LOGIN_SEGMENT=A; EXP_ADP_RV_REORDER=A; EXP_AB_CP_GAMES=A; EXP_ADP_RV_SEGMENT=A; EXP_AB_AUTOFILL=B; EXP_ADP_RV_VIEW_SIMILAR_HLP=A; EXP_ADP_RV_VIEW_SIMILAR=A; EXP_ADP_RV_PRODUCT_V3=CONTROL; EXP_AB_HLP_CARD_REVAMP=CONTROL; EXP_AB_WISHLIST=A; EXP_AB_PRICE_REVEAL_NEW=A; EXP_PLP_INLINE_FILTER=REVAMPED; EXP_EDD_DELIVERY_WIDGET=A; EXP_ADP_RV_MULTI_COUPONS=A; EXP_AB_DWEB_MULTICOUPON=A; EXP_ADP_RV_SEARCH_BAR_NEW=A; EXP_AB_AUTH_DWEB=A; EXP_PLP_INLINE_WIDGETS=A; EXP_PLP_PINKBOX_CTA=CONTROL; EXP_QUERY_PARAM_EXP=B; EXP_AB_PDP_IMAGE=DEFAULT; EXP_AB_CALLOUT_NUDGE=A; EXP_AB_TRUECALLER=DEFAULT; EXP_AB_GOOGLE_ONE_TAP=DEFAULT; EXP_AB_HLP_PAGE=A; EXP_AB_TOP_NAV_CONFIG=CONTROL; EXP_QUERY_PARAM_EXP_DWEB=CONTROL; EXP_AB_HP_SEARCH_ANIMATION=CONTROL; EXP_AB_PDP_HAMBURGER=CONTROL; EXP_AB_HLP_OFFERS=DEFAULT; EXP_AB_WEB_AUTOREAD_OTP=DEFAULT; EXP_AD_BRV=variant1; EXP_PDP_RELEVANT_CATEGORY=DEFAULT; EXP_AB_REMOVE_LOGIN_BOTTOMSHEET=DEFAULT; EXP_AB_ZENDESK_CHAT=A; EXP_AB_HORIZONTAL_WIDGET_TYPE=CONTROL; EXP_AB_IOC_CART_NUDGE=DEFAULT; EXP_APPSFLYER_DOWNLOAD_CTA=DEFAULT; EXP_AB_PDP_SIMILAR_PRODUCT_SHEET=DEFAULT; EXP_FULL_SCREEN_RECO_WIDGET=DEFAULT; EXP_AB_BEST_SELLER_PDP=A; EXP_AB_ENABLE_HLP_NEW_API=DEFAULT; EXP_SPECULATIVE_PRERENDERING=CONTROL; EXP_AB_TAGS_RATING_ON_LISTING=ONLY_TAGS; EXP_SEARCH_INP_ON_CART=A; EXP_AB_NEW_TAGS_ON_PDP=A; EXP_REVIEW_SUBMIT=A; EXP_AB_OFFER_DELTA_COMMUNICATION=A; EXP_AB_NEW_GC_PAGE=A; EXP_PLP_DNW_DWEB=A; EXP_ERROR_BOUNDARY=DEFAULT; EXP_PRIVE_CTA_DISABLE=DEFAULT; EXP_AB_GETAPP_DWEB=A; EXP_AB_HLP_EDD=DEFAULT; EXP_CTA_DISABLE_DWEB=DEFAULT; EXP_AB_GETAPPNUDGE_MWEB=DEFAULT; EXP_AB_MWEB_FILTERS_PLP=A; EXP_AB_VISUAL_FILTERS_PLP=DEFAULT; EXP_AB_NYKAA_NOW_PDP=A; EXP_AB_CONVENIENCE_FEE=A; EXP_SPECIAL_DEALS=A; EXP_CONVERSATION_ROUTE=A; EXP_AB_FREE_GIFT=A; EXP_AB_SALE_PRICE_TAG=DEFAULT; EXP_MINI_COUPONS_OFFERS=A; EXP_AB_DS_AUTH_FLOW=A; EXP_DWEB_MINI_COUPONS_OFFERS=DEFAULT; EXP_AB_PRODUCT_RACK_CS=A; EXP_CART_STEP_COUNTER=DEFAULT; EXP_AB_RATING_REVIEW=A; EXP_AB_SHOW_ASPECTS=CONTROL; EXP_AB_SEARCHCOUNT_MWEB=B; EXP_AB_BOTTOM_NAV=A; EXP_AB_BP_DN_PERS=A; EXP_PLP_DESIGN_PARITY=A; EXP_AB_STICKY_PRICE_V2=A; EXP_PRODUCT_IMG_V2=A; EXP_AB_EDD_DESIGN_V2=A; EXP_CART_GROUPING=A; EXP_DWEB_COLLAPSED_PRICE=A; EXP_COLLAPSED_PRICE_DETAILS=A; EXP_AB_HLP_AFFILIATE=A; EXP_STORE_SUGGESTION=A; EXP_CART_SAVINGS_SHELF=A; EXP_CATEGORY_NUDGE=CONTROL; EXP_TOP_BRAND_FILTERS=A; EXP_CART_MINI_PDP=CONTROL; EXP_AB_AGG_FOOTER_SSR=A; EXP_MAP_PICKER=DEFAULT; EXP_COUPON_OFFER_REORDER=A; EXP_AB_PDP_LITE_OFFERS_SSR=DEFAULT; EXP_HEADER_SUBSTORE_TABS=DEFAULT; EXP_VARIANT_SELECTOR_V2=A; EXP_LADDER_OFFERS=DEFAULT; EXP_AB_TOP_FILTERS_PLP=DEFAULT; EXP_FUTURE_COUPONS=DEFAULT; EXP_HLP_RECO_WIDGETS=CONTROL; EXP_UPDATED_AT=1783944471875; EXP_SSR_CACHE=d62dce4e4872e2206586f89754aed1d4; bm_ss=ab8e18ef4e; bm_sz=A623FE3E9E9C6C8973640341887A4F7E~YAAQjqInF8As2UmfAQAAXahWXwCvC4tnTArFL2OusLxsXGqoHm2yW4NCdAGT6uhTmzfaPFR6knm/mh5pircjlYEbHEnLpJ+YoAOzIglO48MCbvPKDOSwXMOsCq48vLLrcTYCI/e8O7dd6oxoA0rUqYnJU1Avyg3bKNzoTWG4S730deb9fOGZyymH2OCXHlgLLq83RoctNSECnKfj1LULBF0XEQJGvWPUjukJO/15l0HSVaY+iycRe79VZlrOuwifBF9mXoHQq45+aRdV5yrR5Vt+x1d/zPmMdSNR8vv8P8hy46R0rHdAvZIkk7yKGVn9NyDVMXb8E40FrNWaZoyAGbWMY4XMYllgJeHXT3RKF/di6u1AY39HeXnKU0rag2RGwgOzgXyAzxKMMwvZl4ONjDalR+hNB6csIuUnq3yZhW4jtN58oPJQNi04p+t5I4UWYfaC7RZsJ1YegvEQNP5gwJKAF1zkgk2lyQwk+PwVQczdq3ldS4Gjo30jej8/zg==~3224644~3356481; _abck=33495617BB0CB942B2934D9A97444775~0~YAAQjqInF/Us2UmfAQAAUalWXxDoGQbd1hZIjipjlMUURVIVrd9btiuR6yU/Ir8yfhY6nxCYnKLHDepEG7NnsaCrbCfWhtcEqjYEYK+qAyuyoTEXxBAGxyFLgPuEcJYhlCOSJZdYfC83Sv8N9hwkGHN9h1FebTQZZNMByedbP/0CJcG85OlS2v44kVuw1f0U+9xcDKpxjB5Ha69t4GcyzpAYvzN+YIUNq/bFQJYgQKZGHhf7Q124ZtnjysXLEIt1u7Ixr8W1INdhfhfK+aIcznXL8qbM8Ud53dW9gnH19IDSvswo2+E7FhRfNeAxhUaByBt/kzCke127a9dJAeWiFdoJH0w2DMsJ78dZhRV0vqx79CBeGdPnZqqY8MxP7odSO/VMVxOJVhW2JA5oYsw7L1Q4bpGLwePtmoaajBGVo+tDlbpsrBHPLfelfV56ILmanmhDNE+kEpBuzZIWy00D0qWhfVX+jL1yrRIAT29GeznkmEHs+wu5byYcfpXirq/4JsB0mOrTq2r5vjxezNw65Q7sExJ6UjEY6xdP3rCMU47pu5siX727Vyy8KyECRc/DXXrraTAK6F3Gm9GqNIv/Mwqs/wsSLexPBd+oo7RN+e/zYYepHLZMd3zcoUKc4B/h8zL/asMhsMfU9JhOkjlWe6Z/TERQ/jSASMaj1cJxYnXx9cZ+GavzXf3TpjZgambiHrpj7NTVBb9rCZx4onqrihs8VIb4Q4cRRZFpS9nyDubQrdwd/Kzkpy/AWMSOyY4icYy1RFZ/hjmIULB59mtLmltpY5i9tQLkZ/leMuE8p9WFu08IPh2T+CvgW+Xv4vUB7Et4~-1~-1~1784014457~AAQAAAAG%2f%2f%2f%2f%2fwfFWQ6bgM8E1Ba%2fMhClbFxoVFPBTcalkOUg1u59J26D026g31DJVDPHh7FMtSE6SNs14OhUBJn5YC7BHmpWB+RmCu55l6MKuz8W3BI68%2fpfVX09hXF5p6jnyczhJsgLMV2hUrxgkm9p9O3wIzRY1RF%2f7QN4v3kSMYD0LaIuaZ56hUelN%2fFSHSwrDO9wFkz8yuhjlh+wzpzNBr%2fX7SCptHGNA0mkx9He8rClt4IkYqN4NxE%3d~-1; SITE_VISIT_COUNT=11; _ga=GA1.2.1073079245.1784007260; _uetsid=a981cd107f4511f193431f2f254c096a; _uetvid=a98207307f4511f19ade6f479c11dd94; cto_bundle=ZaKyCF9KTjNScEV3ekROZlVpbVdzWDloZEFOVXI1RWpQS3pXMVM0b21yUkxyVzhHSzBFbXI5anplM0FyWk1ZalFpallqWVdwbmZCOWlDRUxrNXhTdjB5Nnl1NG5ScmFkdk1SZ1FBeHRjT0M3UVN6bmtKMjBobFdEcnI4WGhySlFWNm5BYUhNT1Q4ZzV6eXlEUEVOaUVVOGV0YlElM0QlM0Q; WZRK_S_656-WZ5-7K5Z=%7B%22p%22%3A14%2C%22s%22%3A1784007261%2C%22t%22%3A1784010946%7D; _derived_epik=dj0yJnU9Ym9oSU51ZGJLRVlIU0NsbzdaTFo5SW5fdXJYQUpVRnAmbj1UMXF2LXEyUDVUQ29DLS1Ea2VvVEVBJm09MSZ0PUFBQUFBR3BWMk1NJnJtPTEmcnQ9QUFBQUFHcFYyTU0mc3A9Mg; _ga_JQ1CQHSXRX=GS2.2.s1784007260$o1$g1$t1784010948$j60$l0$h0; _ga_LKNEBVRZRG=GS2.1.s1784007259$o1$g1$t1784011121$j60$l0$h0; bm_so=56B36921B700EC3EF9D4A183C1F0FE1385A1E5596F63A9058F86F1863DDA553D~YAAQhaInF2Nrl0WfAQAAO3BZXwi8cFVkyfqjT58HL4zPgB8IjKirpoB3p/HKgfkLbpcLYnsUMX9C8WLGpAa3DoNv7b30ZVa7sU3ZsARjDOYzY/jhyuXMy/kdmNBE6L9uHMRddeqx103pYVGKkvu2JuQww469dZaytQFkO+Ffu5aflIfW17QzBTPs7bacnhynb6K3YpV3uEFfWBaNNkRHcGOc6tYcE4dVzTRB3J7YCvEtrB7NRVyo3te2ZeXcnbFYrdhImuAMoisyBr7K+EDtfc7QZH54SspNHOb/dO65VyYjcwtdQrDBpD2qv1hSD4iMQTki15xDvEPB5onqsk29eSz+/cGvCNhGhfi5V1yiKwbswdmPN07PcfY0C1oXqHKfrs5DHyD1vqUOymkCofz/IK/J608VTIIYzfxRIHU61SKCcXWZRg44SHdUwHsjAjHooVSTxd8SBCCo2idV13z5Hk6Pt2ie; bm_lso=56B36921B700EC3EF9D4A183C1F0FE1385A1E5596F63A9058F86F1863DDA553D~YAAQhaInF2Nrl0WfAQAAO3BZXwi8cFVkyfqjT58HL4zPgB8IjKirpoB3p/HKgfkLbpcLYnsUMX9C8WLGpAa3DoNv7b30ZVa7sU3ZsARjDOYzY/jhyuXMy/kdmNBE6L9uHMRddeqx103pYVGKkvu2JuQww469dZaytQFkO+Ffu5aflIfW17QzBTPs7bacnhynb6K3YpV3uEFfWBaNNkRHcGOc6tYcE4dVzTRB3J7YCvEtrB7NRVyo3te2ZeXcnbFYrdhImuAMoisyBr7K+EDtfc7QZH54SspNHOb/dO65VyYjcwtdQrDBpD2qv1hSD4iMQTki15xDvEPB5onqsk29eSz+/cGvCNhGhfi5V1yiKwbswdmPN07PcfY0C1oXqHKfrs5DHyD1vqUOymkCofz/IK/J608VTIIYzfxRIHU61SKCcXWZRg44SHdUwHsjAjHooVSTxd8SBCCo2idV13z5Hk6Pt2ie~1784011124915; bm_s=YAAQhaInF/Ztl0WfAQAAK3dZXwWOB94HzCUJbia3s8qMdD44nzEIXG6ZD6lFOl00KH3rAS75Nh4stOkfTpctDtrnmikStG8gK1+qJ3KY39i6zaF0xVPPqkp99uwK1yqZxkMtc5LnImgZxdwWOwN5lCncM1VhQBfJnvagz96IHFHLif2c2D2h+alzlX4HtJTypgfx2kHEQxYlpEj9Ili7XdsUqfzSX66f0dG9EEduTZP6H+k1dv/E9bCLetdq2UfSztJxYpwZq2/fMWcgcG+ZQ3sPCeBv/D1y7PY4evaLIiwx33DFiF+Cbqho/2mX2fb5NGETtoDoaYlg3qqnfgOsUiBqyrKhzTbBunAJfBoyXNnG7I4CNK0MuVTNMq9mqCGWiUbk5MuBw9TV/DBYhnPQC38dW3+w2AzgY9FE42vY3hShldqetuNFYdELQYs8Mwdv8RSM+72klala2ekFJWCXjTFhOlnxSZw2hBHE/QRTnNidc6af26BMF4GLXn7PXW1zbKrtSJJQvfkCo/ES7DqxAChGgRmSffY6OtzJafFgtdxdF7D/Ctd012XsqcLe6V1eb3+rw9abGTcOBGiiYEgJzztSgtyjK1m8sKUm5CRq81L7BJQUOObyLl1ddtQQq0CGxJ9UbWEutFOkGqKOQzpV4X931jszmg1iDrswmgwVLl5NnmQFPE5MC98xfMPbZ4kwi2Xe2C2HWXcvk81yz3LCp0AX1t5nlIfmkkqNSP7PG+jFZcUpGeYR4yWgE+8mABMNZNTmPbREx9x20vE5Mg1QIIJWtYG46BrAk1/59i27c2J3dcpnI5xDtXO7hDno2AfuaBh7ASQubhloUkDNRf5Gg+AG+xrivADvuicAH0TtPA1nQNxOBgKWiLZafXuwsrfL7yW6FnGD5cDEkjasMkgRpHMKF72UVAi/mGMq86gyqmobyZfcfCeSL4m+tVrmpqA3eJwADCV/YPnzK5+XrY5R7Oz08q96fHkRC5DVMaO/aHFA9R3Z; _clsk=b0vfx7%5E1784011127410%5E17%5E1%5El.clarity.ms%2Fcollect; _abck=33495617BB0CB942B2934D9A97444775~-1~YAAQhaInF14zmEWfAQAAqEJcXxD/fTwhigjk2MRN/+EjjYiSDehCHRboFkllZj2r6+a3clyox3zsNtT/y764ouir+6HWh2ADaFQLF9c1UGzdg5KsgqZozxYx4p49N4acDbNW2b5VU9PDLN4+zAMx/fh47teh2g9pwdnhT+vI4X4nIaf+JiD4eRjguea1XWcqTuGo6+/1Qfun1tLQHFrclCBPwix3XhB74dxgn7+J9tXhGjG01GJ/qH/IZ+QkDwNz1EufLdPWsJvc3TeWNWqJFwpu2Hv0vjvwpCP+ACZf/qKZmKGYiWl4XL8N0NaaDrzLppYfTEHGGRT8WvHXI8Z7D/0NsxYbDpZHl/GeyeAmrc3kiv0oqdCXZ56xxKLYOZkKBbj7aEaePLjqyQlnN8JgUnWabzNJe1EPQ7oXKIu+P7nu6qB4sP27P4yFx0tC075yBCwQ2TgVXPjNf17EscYpGSnTIk35115swAtytMGFHUGdzVDI8PjGbsQ8EFzwkAzbdEuMnCGHBvrTjiV8NZK7kqhV+GGSgt+yORV+MHfeiS4ITJ5vRVlVPrhlickfWyI9PZc+QAaGilLTvvmQo6CDeImiYL7rFdelPG4QN7Ska7nkrocOoO2pTzF9p3Wztal6yRuiKki2U4JSvB7bO94ss7MH+lwewtNQMy0T7+kpowEDy1RnF9406MkJY8O22Osh+kKmsAUgI7/KAAE0ciBJ8pdtDuSRpiFFvL1JMHP3ala3FVknynBr7LN/PiAupySpFEAgG6/DfIujCxUmLamJkRG+WOEHHEXjpoMUOgAugssRRferYfLpwtB7gcfjWTRGt/Av~0~-1~1784014457~AAQAAAAG%2f%2f%2f%2f%2fwfFWQ6bgM8E1Ba%2fMhClbFxoVFPBTcalkOUg1u59J26D026g31DJVDPHh7FMtSE6SNs14OhUBJn5YC7BHmpWB+RmCu55l6MKuz8W3BI68%2fpfVX09hXF5p6jnyczhJsgLMV2hUrxgkm9p9O3wIzRY1RF%2f7QN4v3kSMYD0LaIuaZ56hUelN%2fFSHSwrDO9wFkz8yuhjlh+wzpzNBr%2fX7SCptHGNA0mkx9He8rClt4IkYqN4NxE%3d~-1; bm_s=YAAQhaInF18zmEWfAQAAqEJcXwUeUUmN+L4ByqvlH4bDkt8LcKElWIFn0MrdZhnKQKGev07FK0IWwFKqauqo0jIx/mrKEtGZIU0npuJT0WLHQtdADol6+gl0Bql4gKn0dwVOD4pPXZ2d64K/WRBSJJojgk6weD80mRvRi8VzxD8YxSWsxN+oWaSf3GyaOQ5LBv8mKQOTNGy+q00LOY6HYngLNYixzpZajKxge04HMR69uEt65evxhbHGClRmd/TUluYetY5/yUwHLqnZeG9YiE0caZ8l20v734z65DQX17mnInbF0MEj23y0KrOHRnSgVBmtHr9KJC7mM6rpHa+pSJvdXKhPrLZCwI3ykVvIRvYYTwI75ZiOD8g2MhUSoUkXYS8wcuYCItkMh6jcWmt245baFQJGCu+eBbyTYKrlDL0BttrqXyWLRnZTB01DjC/t2lXbWk2vANua95f+JNyOyv/PPt98UqomzS4WDIyNM/baPfrjX3G8DsdxERarBxEnPDuBwAEccWH8geS4aD/ZODr2fKOjU4Gr6cWlksKi63HLPXPGLYqOME05qBC4+dpl7X/1Gp413lc5RFD1WiJU0ZgBggyZ2/OYTO1+KJfliOwhLfVB0ejmsd+IH45MUZiBD9cbGBjkseJPEHD6Gk+SOfOJJ7Gn0J98vRZYs6nzKblhcEsL3c80DYjEyE2Y3GerNkKhg8izvAbH3cE=; bm_so=352E12C4085BE4B69C3AFB0CB464D3B21A35C75CC5A2E5469FD0426635FEEB52~YAAQNBzFFzGH/U2fAQAACnonXwjdj7TZh04UGup0kDHdqgvcA4yD7sz4559ELGxhrUFlADFEld5ZUySpSc4xuN1hOGi8zfeBfzXNc0tSGoUp4BGZSFiucU3zXjuW+1JCBP2qRpSn/U9PR/pXLsLizETelLhXic10tL7jJN6oTCzbrn6+pt7yw/YPyQvAUf//wLeA3yqejLVA9nqELKQUilsIZAKQ5GHACFu7yaE+mXVDa6jr4ncqCvYdLyAjjfEoCc2bB76lvQ34V+DpLGD6REKJzrboSLBfIYLBP2gxId3RAZjxci6/zwQVaegtZ9pZ9nsAX802PzLM5W/UifUH8cguLa7j+lJnI6evyT27Ucsk1McjhtVbAgD6t8wBbMzW4SvmT/hGUbVOGGQD0pZInrB35i1AkGdmQvBVItkLSqjjt26N298lfLLyxJ+NFli69gxPlo4FWmghKfjd5jPOOA8lftRb; bm_sz=A623FE3E9E9C6C8973640341887A4F7E~YAAQhaInF2AzmEWfAQAAqEJcXwAtPbSixQOhC71x5pgtMbtiq4Du4K6omgh6qO/53klCAFeZeZ0R6XiXrObe8dq+jNQ/Ch1ug+sN80xuOe8CQOP+WMz0pAqI/phlczUmJEdqpVfpHvyPE+5otKxs9lnhZuKHln26mIUDn0QLCjPfJ16jE02LOuzd8U7j25L5iUN4emWdUn/c6Kbyq+IRZW5UIB8svEe55hYXX373g1fwWNsHwOUTnXshRft7/xn9S4y0fvloo1MD2qQHP8oewnXvZ0pjkgnU8GfAXQfJqvezXM8Fv/HKui/HWfhOqnRBEZ8Jcw8sxxGKsFksq5ZdjKQl6rds+1kEDotKcJODdbfd8g5/F47J7TlnmkKDVthJbIhkQ4vVl3dqnD18mQrUKmh3EpWNvsMp+loT+3AIdxXzWCn/M/NM+RigvZXCou10an6iEeMtJ2Tb+FTwKYilkBeGtCmIbLGtlO4oOQ3GNa7DuiNbW8p3ADt0eEtzP4aKCjGHAQU=~3224644~3356481'
}
# ==========================================
# 2. DOWNLOADER FUNCTION
# ==========================================
def download_pages(start_page=1, end_page=6):
    print("=== Phase 1: Downloading HTML Files ===")
    for page_no in range(start_page, end_page + 1):
        print(f"\nFetching Page {page_no}...")
        params = {
            'page_no': page_no,
            'sort': 'popularity'
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                file_name = f"{page_no}_source_code.html"
                file_path = os.path.join(html_dir, file_name)
                
                with open(file_path, "w", encoding="utf-8") as out_file:
                    out_file.write(response.text)
                    
                print(f"-> Success! Saved to: {file_path}")
            else:
                print(f"-> Failed! HTTP Status: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"-> Error: {e}")
            
        # Polite rate-limiting
        time.sleep(2)

# ==========================================
# 3. EXTRACTION FUNCTION
# ==========================================
def extract_preloaded_state(html_file_path, output_json_path):
    try:
        with open(html_file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        
        # Look for __PRELOADED_STATE__
        match = re.search(r'__PRELOADED_STATE__\s*=\s*(\{.*)', html_content, re.DOTALL)
        
        if not match:
            print(f"Skipping: '__PRELOADED_STATE__' not found in {os.path.basename(html_file_path)}")
            return False

        potential_json = match.group(1)
        
        # Balance out the curly braces
        brace_count = 0
        json_chars = []
        started = False
        
        for char in potential_json:
            if char == '{':
                brace_count += 1
                started = True
            elif char == '}':
                brace_count -= 1
            
            if started:
                json_chars.append(char)
                
            if started and brace_count == 0:
                break
        
        refined_json_str = "".join(json_chars)
        state_data = json.loads(refined_json_str)
        
        with open(output_json_path, 'w', encoding='utf-8') as out_file:
            json.dump(state_data, out_file, indent=2, ensure_ascii=False)
            
        print(f"Processed: {os.path.basename(html_file_path)} -> {os.path.basename(output_json_path)}")
        return True

    except json.JSONDecodeError as je:
        print(f"Failed parsing JSON for {os.path.basename(html_file_path)}: {je}")
    except Exception as e:
        print(f"Error processing {os.path.basename(html_file_path)}: {e}")
    return False

# ==========================================
# 4. EXECUTION
# ==========================================
if __name__ == "__main__":
    # 1. Download pages 1 to 6
    download_pages(1, 6)
    
    print("\n" + "="*40)
    print("=== Phase 2: Extracting JSON Data ===")
    print("="*40 + "\n")
    
    # 2. Extract JSON for all downloaded pages dynamically
    for page_no in range(1, 7):
        html_file = os.path.join(html_dir, f"{page_no}_source_code.html")
        json_file = os.path.join(json_dir, f"{page_no}_preloaded_state.json")
        
        if os.path.exists(html_file):
            extract_preloaded_state(html_file, json_file)
        else:
            print(f"Missing file: {html_file}. Skipping.")