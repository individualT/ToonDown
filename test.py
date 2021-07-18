from core import toon, page, homepagemaker
option='newtoki'
info=11237686 #14530561
mytoon=toon(option,info)
print(mytoon.address)
print(mytoon.page_addresses)
print(mytoon.page_titles)
print(mytoon.title)
print(mytoon.description)
print(mytoon.thumb)
mytoon.download()
mytoon.page_html()
mytoon.index_html()
homepagemaker()