import requests
import base64
from bs4 import BeautifulSoup as bs
from core import toon, page
option='newtoki'
info=14530561
mytoon=toon(option,info)
print(mytoon.address)
print(mytoon.page_addresses)
print(mytoon.page_titles)
print(mytoon.title)
print(mytoon.description)
print(mytoon.thumb)
#firstpage=page(mytoon.page_titles[0],mytoon.page_addresses[0],0,option,mytoon.title)
#print(firstpage.toon_title)
#mytoon.download()
#mytoon.page_html()
#mytoon.index_html()
