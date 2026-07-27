from json_extract import json_extract
import json
from product_extract import product_extract

payload = json.dumps({
  "productCode": "P1110157",
  "storeViewCode": "in",
  "configModule": 3,
  "settleChannel": 3
})
headers = {
  'accept': 'application/json, text/plain, */*',
  'accept-language': 'en-US,en;q=0.9',
  'cache-control': 'no-cache',
  'content-type': 'application/json',
  'origin': 'https://www.oppo.com',
  'pragma': 'no-cache',
  'priority': 'u=1, i',
  'referer': 'https://www.oppo.com/in/product/reno16c-5g.P.P1110157?utm_source=google&utm_medium=cpc&utm_campaign=OPPO-PHD-IN_EN-OPPO_Reno16-Sale-All_India-CPC-Brand_Kws-20260709-20260715-Traffic-Purchase&gad_source=1&gad_campaignid=22635990382&gbraid=0AAAAA_dMfGEc5er29m373yGYB-3xz0D2p&gclid=CjwKCAjw1IHTBhAaEiwA4AYNFonvQG84fi9B54oBACIwUMIK7LOxeNivIdZa4hq1gMWrUqtE1OuwGxoCzT4QAvD_BwE',
  'sec-ch-ua': '"Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-site',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36',
  'Cookie': '_gcl_au=1.1.49607510.1784708886; _gcl_gs=2.1.k1$i1784708885$u48011513; _ga=GA1.1.1058775767.1784708886; frontend=e3f4cb469fb0432a85b418cbe48d2abf; source_param=google; WEBSITE_URL=https://www.oppo.com/in/product/reno16c-5g.P.P1110157; utm_source=google; utm_medium=cpc; utm_campaign=OPPO-PHD-IN_EN-OPPO_Reno16-Sale-All_India-CPC-Brand_Kws-20260709-20260715-Traffic-Purchase; _hjSessionUser_2075538=eyJpZCI6IjgyNjFhMzNiLWM4ZjQtNWQ4OS1hYTMwLTAyOTI4YTEzOWMwOCIsImNyZWF0ZWQiOjE3ODQ3MDg4ODg1OTIsImV4aXN0aW5nIjpmYWxzZX0=; _hjSession_2075538=eyJpZCI6IjZhYzViYThmLTE3ZGUtNGM0YS05ODE5LWU5MjNiNDhkYThlZCIsImMiOjE3ODQ3MDg4ODg1OTUsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjoxLCJzcCI6MH0=; IR_gbd=oppo.com; _fbp=fb.1.1784708889994.389295733937788944; IR_15008=1784708890107%7C0%7C1784708890107%7C%7C; IR_PI=45a91f0e-85a7-11f1-ace9-41b94a4bb4cb%7C1784795290131; cookiesaccepted=true; _gcl_aw=GCL.1784709014.CjwKCAjw1IHTBhAaEiwA4AYNFonvQG84fi9B54oBACIwUMIK7LOxeNivIdZa4hq1gMWrUqtE1OuwGxoCzT4QAvD_BwE; _ga_DTXFPC1MML=GS2.1.s1784708885$o1$g1$t1784709013$j23$l0$h0; frontend=e3f4cb469fb0432a85b418cbe48d2abf'
}

# data = json_extract(
#     url="https://opsg-gateway-in.oppo.com/v2/api/rest/mall/product/page/fetch",
#     headers=headers,
#     payload=payload
# )

product_extract()