import os
import re

resultjfif = [os.path.join(dp, f) for dp, dn, filenames in os.walk("../") for f in filenames if (os.path.splitext(f)[1] == '.jfif')]

for i in resultjfif:
    pre, ext = os.path.splitext(i)
    os.rename(i, pre + 'jpg')
resultjpg = [os.path.join(dp, f) for dp, dn, filenames in os.walk("../") for f in filenames if (os.path.splitext(f)[0].endswith('jpg'))]
for i in resultjpg:
    os.rename(i,i[:-3]+'.'+i[-3:])

