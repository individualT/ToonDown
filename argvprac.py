import requests
import json
from bs4 import BeautifulSoup as bs
import itertools
import random
import difflib
azi_domain='https://agit74.com' 
def azi_image_domain():
    headers = {
        'authority': 'agit74.com',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'sec-ch-ua': '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36',
        'sec-ch-ua-platform': '"Windows"',
        'accept': '*/*',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'no-cors',
        'sec-fetch-dest': 'script',
        'referer': azi_domain,
        'accept-language': 'ko,ko-KR;q=0.9,en;q=0.8,zh-CN;q=0.7,zh-HK;q=0.6,zh-TW;q=0.5,zh;q=0.4',
        'cookie': '_gid=GA1.2.1318391845.1633283101; U8bep2A0AZhistory_2021_10_4=10079%2C279; _ga_M7RLCGQTYK=GS1.1.1633314724.2.1.1633316012.25; _ga=GA1.2.1870258245.1633283093',
    }
    params = (
        ('v',str(round(random.random(),16))),
    )
    response = requests.get('https://agit74.com/data/azitoon.js', headers=headers, params=params)
    return response.text.split('img_domain3 = "')[1].split('"')[0]
def soupmaker(url):
    return bs(requests.get(url).text,'html.parser')
def azitoondata(azi_domain):
    soup=soupmaker(azi_domain)
    a=soup.findAll('script')
    indexes=[]
    for i in a:
        if 'document.write' in str(i.string) and 'azi_webtoon' in str(i.string):
            splitted=i.string.strip().split("src='")
            indexes=[j.split("'")[0] for j in splitted[1:]]
    #{'x': '9671', 't': '홀인원', 'd': '1633191781', 'au': '드라마', 'tag': ',16,', 'pd': '7', 'tagj': '', 'pdj': '', 'c2': '100', 'c': '11', 'ag': '19', 'co': '0', 'nt': '0034 -  34화', 'up': '0', 'g': 1633191766, 'h': 371163, 'o2': 0, 'tj': '0', 'p': '2021/0425/202104251256512987206_x4.jpg'}
    toonDB=list(itertools.chain.from_iterable([json.loads(requests.get(azi_domain+index).text[12:-1]) for index in indexes]))
    toondata={i['t']:i['x'] for i in toonDB}
    return toondata
def querytoimages(query,toondata,azi_domain,pageindex):
    title=difflib.get_close_matches(query,toondata.keys())[0]
    page_address=azi_domain+f'/azi_toon/{toondata[title]}.html'
    soup=soupmaker(page_address)
    a=(soup.findAll('script'))
    for i in a:
        if 'document.write' in str(i.string) and 'toonlist' in str(i.string):
            indexjs=i.string.split("src='")[1].split('?')[0]
    headers = {
        'authority': azi_domain,
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'sec-ch-ua': '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36',
        'sec-ch-ua-platform': '"Windows"',
        'accept': '*/*',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'no-cors',
        'sec-fetch-dest': 'script',
        'referer': page_address,
        'accept-language': 'ko',
        'cookie': '_gid=GA1.2.1889689063.1633313954; _gat_gtag_UA_186192900_1=1; U8bep2A0AZhistory_2021_10_4=10079; _ga_M7RLCGQTYK=GS1.1.1633313952.1.1.1633313970.42; _ga=GA1.2.1245218660.1633313953',
    }
    params = (
        ('v', str(round(random.random(),16))),
    )
    pageDB=json.loads(requests.get(azi_domain+indexjs, headers=headers, params=params).text[12:-1])
    pagedata=[[i['t'],i['u'],i['s1'],i['id'],i['od'],i['d'],i['u3']] for i in pageDB]
    #print(pagedata[100])
    soup=soupmaker(azi_domain+pagedata[pageindex][1])
    imagedomain=azi_image_domain()
    return [imagedomain+i.split('"')[0] for i in str(soup.select_one('#toon_content_imgs')).split('<img o_src="')[1:]]
toondata=azitoondata(azi_domain)
images=querytoimages('나 혼자만 레벨업',toondata,azi_domain,0)
print(images)