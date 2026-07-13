import requests

url = "https://www.giva.co/products/two-layer-ring-in-yellow-gold"

payload = {}
headers = {
  'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
  'accept-language': 'en-US,en;q=0.9',
  'cache-control': 'no-cache',
  'pragma': 'no-cache',
  'priority': 'u=0, i',
  'referer': 'https://www.giva.co/collections/rings',
  'sec-ch-ua': '"Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'sec-fetch-dest': 'document',
  'sec-fetch-mode': 'navigate',
  'sec-fetch-site': 'same-origin',
  'sec-fetch-user': '?1',
  'upgrade-insecure-requests': '1',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36',
  'Cookie': 'localization=IN; _shopify_y=4b500619-9027-41de-96d5-c1609c7c5f55; _conv_r=s%3Awww.google.com*m%3Aorganic*t%3Aundefined*c%3A; _gcl_au=1.1.472373772.1783935951; _shopify_analytics=:AZ9a3lPGAAEA8vXQOGFEGhZKFTJ_nitfG9VBauAUSFaqQnKFgGiOnUw0m0WRl-uojbTeS4C68u8h7Ks4p0Q5z9nQtzbQMSfnjKTzjf_0AqFI2fU3INgIf5-rn425OhdNc6vEADljwAaBmvBk9V6uPgM-UuoxridDJqLF9ulSJqrT5kbd:; cart=hWNEQU1CusTy8wN0f8hzrdbg%3Fkey%3D4d88f294432a61c806893537888cb411; _ga=GA1.1.1535273439.1783935952; _clck=1f59xv2%5E2%5Eg7p%5E0%5E2385; WZRK_G=2124e1ff33554a44b0e06b9593a42a4a; _twpid=tw.1783935953284.340471543950421495; nitrox=61864a94-e748-409a-9c22-ea5dae7d6069; _cnt_first_visit_time=1783935958.812; _cnt_last_visit_time=1783935958.812; _cnt_current_visit_time=1783935958.812; _cnt_num_of_vists=1; _cnt_event_user_id=mkzywyo5n7hbpczg0h14r; _cnt_geo_country=India; _cnt_forms_status=%7B%7D; _fbp=fb.1.1783935958882.9983776358; biscuit-id=biscuit_229a99b7-cee9-4e9d-83af-913d7cb668a0; _cnt_is_custom=false; firstProductEvent_285118562466_2026-07-13=1; _cnt_user_push_consent=true; _cnt_ext_user_id=c3f886434c001c28495e6db234987663; _cnt_user_email=undefined; _cnl_push_optin=1; _shopify_marketing=:AZ9a3lPGAAEAZiiu5-WTym6TwmGSGpnaIGM7AUv5Z1f2t7mQPsjDJjJF2RiGLczLrIY7DXzo7biFUPZuE15zkCQzvSeDp77cbpGGAwMbXMy8iwY-darpOH7_emWAEtXmtPSs1vVmioWYlGthspt_iGYuhs0:; _shopify_s=d985be43-6091-4ea4-8d07-b49a6f451c34; entaice_pses.0714=*; WZRK_G=2124e1ff33554a44b0e06b9593a42a4a; _conv_v=vi%3A1*sc%3A1*cs%3A1783935950*fs%3A1783935950*pv%3A14*exp%3A%7B%7D*seg%3A%7B%7D; _conv_s=sh%3A1783935950263-0.056166034512962204*si%3A1*pv%3A14; givaPageCount=12; _ga_T0WFKEH1CF=GS2.1.s1783940046$o2$g1$t1783941025$j58$l0$h0$d5cH34whGhPYazi6wa6rXMByuRurKwT0jPA; _clsk=jci9tu%5E1783941026151%5E14%5E1%5El.clarity.ms%2Fcollect; _ga_F1NJ1E2HJ2=GS2.1.s1783940049$o2$g1$t1783941034$j60$l0$h0; _shopify_essential=:AZ9a3lO2AAEAIqdKdS5CD4sazuTvoTtH9VMlZKRaoFSryrA79OjJGflc4gmm7bjhJizlKmr2aqzY6YeK9YFwDtAcU0PbbhQE-xYWdnaivYpFZkeYnY0wiBNh4JLsaKqnuk8pyGb0i_CP8LaucuwlVuR8fevlTbVmj9zGFLyaMVQSiF_3lhrFeD9MZgn9haRpjDVAi2fGMEes0OPykQjmc6SaTWs4TRlhJ0oOLcyIhdzy4R_2XHSuzkraxTiLggs89D5SFKVum1rHQcl4boQCEYoIhMXjtfpRvRv0dkp38-YNxoS0beABDfIxAYzPS2ZVAL4xcl3lJ9IDwCFYo49birxznNjmSLZP_V1mtoVU0Xccj7TPzJJ84b_w_OFdnqOpfyRdp-pa2EBAmPQrKPi5KogXo4OppD8g_LUZpn9BwDK7hcekY3qfyRRjngY3hUW-S2hpd6sk1ax6SrnT_Macjt1LYc4ojbQF01VbdtrNliVRViLIBIu_h7CjLbXSE524RgL2tTC-Y_7Q9Zvdh57LJXEJe034byH3sn98vRGJSSyt1GjyDOxii2nYE6Mf6I1-MOIs6G1zHKa3PVjuEF4VBUrBWw8kCmmOOQSFgyzDMKRa09bq9Z1EYV5ijSKFEMWg-VBH1QXXZsHA:; cf_clearance=BZpKSMsunc0lroBd9vmkbr2EZOmcaqBSxnwBfo97SB0-1783941034-1.2.1.1-FdPkcFshfNUIZFIzhnBhxtOMwqRrGhoHPpo1R0A7YZCBlAru0.uD4KhFL7kIUEfroey14b3dx14H6go5t.aZtX_Llo1eW08UBf7crcTn6Y9vuSWBKPTvaSg6VGDHHzEaXRvCh_mHVqjQdhGtnBesQSIHX_CdABiLCvhL7t323.3vHVAatmXn0STRSnOnXPw9db2GFQ2am0TTzKkqKr4AKvaauOsYNC_2_FQqIb5_YsmRwzWcR66Grk76YoqxeafJg9VwGPNHildIXPFzBuvAhwrKn6WMJlo4sISaSI7.WTGIwMaL24PX6aMGw_D0ZH_Fu2ovR0252ktW5HCKGRj7SQ; _uetsid=a66126007e9f11f19e34c1c5133d309c; _uetvid=a66152607e9f11f1bfa55b8f570faa98; entaice_pid.0714=94b779a1-7817-4391-9219-67b210b0c86f.1783935958.2.1783941039.1783936317.cdc582c5-4983-48a9-ab08-c1cb90b1aaba; _cnt_cart_json=%7B%22item_count%22%3A0%2C%22total_price%22%3A0%2C%22item_ids_%22%3A%22%22%2C%22variant_ids_%22%3A%22%22%2C%22abandoned_time%22%3A1783941041.362%7D; WZRK_S_R78-Z5K-847Z=%7B%22p%22%3A4%2C%22s%22%3A1783940050%2C%22t%22%3A1783941142%7D; _ga_34LM183QM4=GS2.1.s1783935954$o1$g1$t1783941180$j46$l1$h144093526$dQYL7gmACjERpug4-fCYkFPukawT4mXfCRw; _dd_s=rum=1&id=01611bc3-de27-4c08-b7c7-655bf5f84a92&created=1783939627109&expire=1783942106628; _shopify_s=d985be43-6091-4ea4-8d07-b49a6f451c34; _shopify_y=4b500619-9027-41de-96d5-c1609c7c5f55; _shopify_essential=:AZ9a3lO2AAEAz3QSRCAsafQsW0v_dWQwEtnzLMYKwJr0Mpk5LXDR4zg1Fvs-Ky40KilXcNMwPsY-d1Pb5nxJCLqrKqF04if1M9hPtiM0dxIeddfrwbVY9x1_BUspwbHDJ-_QiyfuoB2hxl3C-1ZhFr5vCmEMTozULHtOVw58agFnGH_paW9I0n7M7k8pwEczvUbCFDdUKyh92cXkKsjBiIwjCxbLUPje1f4alDK-v4ICmfgPtUTI2y2-fSQuLDReSHPvMO_ECCykXhXI5fgqc1yhT8eJiG19QuFAzMr45N_bOLBiKT0T2qNZpJi2-ee3-EEd_ewpylrTgWd7OzXJ7ollSVgAWvV80ck_Vpi2Yo9cV1dMmTGe2EDjKrlE0GRXOzb6Y4LTZmiZ7pXzAjuNIvRLNEdcpsoqyqNFg2CVnoaz1FnFgAhzvNisc3qfvlvItKmLJ2CuFfGzuIaED7jaOSFtH9WM5_ZHrsBZhkOx1iL2lIBnZpFb3XX8qKXx0wxExzLQtr2cjTco2OeZcCzaoUXboVfc6qgMFTqnXE_7WavtNOSJ-dYBfAF1lbcgSd3mSvOdbYfyRsEYcyx_1sJtBKqkYPAHYNtlUMy6CpxEbHGbgHlw8fbQlQe-Uo859sKfwmpQ7RUJS_Vb:; localization=IN'
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)
with open(r'C:\Users\hiren.chauhan\Desktop\HirenGit\giva\source_code.html', "w", encoding="utf-8") as out_file:
    out_file.write(response.text)

