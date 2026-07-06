from email import message_from_binary_file
from parsel import Selector
import os,json

path = r"C:\Users\hiren.chauhan\Desktop\HirenGit\maggie\MAGGI® Special Masala, 2-Minute Spicy Maggi Masala Noodles (2).mhtml"

with open(path, "rb") as f:
    msg = message_from_binary_file(f)

html = None
for part in msg.walk():
    if part.get_content_type() == "text/html":
        html = part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", errors="ignore")
        break
data={}
if html:
    sel = Selector(text=html)
    head=sel.xpath('//table//th/text()').getall()
    
    rows = sel.xpath('//*[@id="panel-0"]/div/div/div/div[4]/div/div/table/tbody/tr')
    for row in rows:
        cells = [td.xpath('normalize-space()').get() for td in row.xpath('./td')]
        data[cells[0].lower().replace(' ','_')]={
                        key.lower().replace(' ','_'):('NA' if value == '-' else value)
                        for key,value in zip(head,cells[1:])}


path=os.path.join(r'C:\Users\hiren.chauhan\Desktop\HirenGit\maggie','table_data.json')


with open(path,'w')as f:
    json.dump(data,f,indent=4)



