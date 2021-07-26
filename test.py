from core import toon, page, homepagemaker
import pandas as pd
option='tkor'
info='qergee' #14530561 #10527973 #11237686 #14530561
mytoon=toon(option,info)
mytoon.download()
mytoon.page_html()
mytoon.index_html()
homepagemaker()