import sys
from core import *
import pandas as pd
option='tkor'
alreadytoons=direc()

queue=[i.replace('\n','') for i in open('waitlist.txt','r',encoding='utf-8').readlines()]
for i in range(len(queue)):
    if queue[i].replace(' ','_') in alreadytoons:
        info=queue[i]
    else:
        info=search(queue[i],option)
        queue[i]=info
        open('waitlist.txt','w').writelines([j+'\n' for j in queue])
    mytoon=toon(option,info)
    mytoon.download()
    mytoon.page_html()
    mytoon.index_html()
for info in alreadytoons:
    mytoon=toon(option,info)
    mytoon.download()
    mytoon.page_html()
    mytoon.index_html()
homepagemaker()