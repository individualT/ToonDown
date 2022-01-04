#토스에서 사용되는 어투를 사용해보았어요. 이렇게하면 UX가 좋아진다고 해서요.
import errno
import requests
import base64
from bs4 import BeautifulSoup as bs
import os
from tqdm import tqdm
from datetime import datetime as dt
import re
from multiprocessing.pool import ThreadPool
from multiprocessing import cpu_count
from time import time as timer
from shutil import copyfile
from PIL import Image
from tqdm import tqdm
from PIL import ImageFile
import argparse
ImageFile.LOAD_TRUNCATED_IMAGES = True
cpunum=cpu_count()
measurepop='as_good' #'as_view' , 아무것도 안하면 최신순
overwrite = False #각 회차의 각 이미지가 존재하는지 일일히 다 체크해요. False라면 이미지가 없는 가장 오래된 회차의 직전 회차부터 체크를 시작하고, 이전은 생략해요.
loggin = False
domains = {i[0]:i[1] for i in [j.replace('\n','').split(' ') for j in open('domain.txt', 'r').readlines()]}
newtoki_domain = domains['newtoki_domain'] #requests.get('https://newtoki13.org').url[:-1]
tkor_domain = domains['tkor_domain']
def imageparse(imagename):
    spli=imagename.replace('.jpg','').split('_')
    if len(spli)!=2 or not (spli[0].isnumeric() and spli[1].isnumeric()):
        return False
    return int(spli[0]),int(spli[1])
def soupmaker(url):
    return bs(requests.get(url).text,'html.parser')
def popnewtoki(measurepop,nsfw,count=30):
    
    page=int(count/96)+1
    if nsfw:
        urls=[newtoki_domain+f'/webtoon/p{i}?sst={measurepop}&sod=desc&toon=성인웹툰' for i in range(1,page+1)] #&tag=성인
    else:
        urls=[newtoki_domain+f'/webtoon/p{i}?sst={measurepop}&sod=desc&tag=성인' for i in range(1,page+1)]
    results=[]
    for url in urls:
        soup=soupmaker(url)
        for i in range(1,97):
            results.append([soup.select_one(f'#webtoon-list-all > li:nth-child({i}) > div > div > div > div.img-wrap > div > a')['href'].split('/')[4],soup.select_one(f'#webtoon-list-all > li:nth-child({i}) > div > div > div > div.img-wrap > div > div > a > span').text])
    return results[:count]
def daytkor(filter,day,countperday=10):
    filters =['인기','최신','제목']
    days = ['일','월','화','수','목','금','토','열흘']
    if not filter in filters:
        assert False
    link=tkor_domain+'/웹툰/연재?fil='+filter
    soup=soupmaker(link)
    week=soup.select('ul.homelist')
    if not day in days:
        da=week[day]
    else:
        da=week[days.index(day)]
    results=[[i['href'][1:],i['alt']] for i in da.select('#title')]
    return results[:countperday]

def poptkor(now,genre,count=30):
    nows=['연재','완결']
    filters =['인기','최신','제목']
    genres=['성인','드라마','판타지','액션','로맨스','일상','개그','미스터리','순정','스포츠','BL','스릴러','무협','학원','공포','스토리']
    if (not now in nows) or (not genre in genres and now=='연재') or (not (genre in genres or genre in filters)):
        assert False
    # 완결 이라면 genre로 인기, 최신, 제목 가능
    link=tkor_domain+'/웹툰/'+now+'?fil='+genre
    soup=soupmaker(link)
    results=[[i['href'][1:],i['alt']] for i in soup.select('#title')]
    return results[:count]
def downloadpopulartkor(opt1,opt2,count,muzisungYes=False):
    nows=['연재','완결']
    filters =['인기','최신','제목']
    days = ['일','월','화','수','목','금','토','열흘']
    genres=['성인','드라마','판타지','액션','로맨스','일상','개그','미스터리','순정','스포츠','BL','스릴러','무협','학원','공포','스토리']
    if opt1 in nows:
        pops=poptkor(opt1,opt2,count)
    elif opt1 in filters:
        pops=daytkor(opt1,opt2,count)
    else:
        assert False
    src=srcftn()
    alreadywebtoons=[i[0] for i in src]
    alreadywebtoonstitle=[i[2] for i in src]
    for inf in pops:
        if not inf[1] in alreadywebtoons:
            mytoon=toon('tkor',inf[1]) #뉴토끼는 inf가 [id, 실제 제목] 형식이고 툰코는 [제목, 실제 제목] 형식이라 inf[1] 검색 요함
            if not mytoon.title in alreadywebtoonstitle:
                if muzisungYes:
                    proceed='Y'
                    print(f'툰코에서 웹툰 {inf[1]} ({inf[0]})를 다운받아요.')
                else:
                    proceed=input(f'툰코에서 웹툰 {inf[1]} ({inf[0]})를 다운받아요. 진행할까요? [Y/n]')
                if not proceed.lower()=='n':
                    print(mytoon.title,mytoon.real_title)
                    assert mytoon.real_title==inf[1]
                    src=srcftn()
                    src.append([mytoon.real_title,'tkor',mytoon.title])
                    srcwriter(src)
                    homepagemaker()
                    searchindex()
                    mytoon.download()
                    mytoon.page_html()
                    mytoon.index_html()

                else:
                    print(f'{inf[1]} 웹툰 다운로드가 취소되었어요')
            else:
                print(f'{inf[1]} 웹툰은 이미 있어요')
        else:
            print(f'{inf[1]} 웹툰은 이미 있어요')
def downloadpopularnewtoki(measurepop,nsfw,count=30,muzisungYes=False):
    src=srcftn()
    alreadywebtoons=[i[0] for i in src]
    alreadywebtoonstitle=[i[2] for i in src]
    pops=popnewtoki(measurepop,nsfw,count)
    for inf in pops:
        if not inf[1] in alreadywebtoons:
            mytoon=toon('newtoki',inf[0])
            
            if not mytoon.title in alreadywebtoonstitle:
                if muzisungYes:
                    proceed='Y'
                    print(f'뉴토끼에서 웹툰 {inf[1]} ({inf[0]})를 다운받아요.')
                else:
                    proceed=input(f'뉴토끼에서 웹툰 {inf[1]} ({inf[0]})를 다운받아요. 진행할까요? [Y/n]')
                if not proceed.lower()=='n':
                    print(mytoon.title,mytoon.real_title)
                    assert mytoon.real_title==inf[1]
                    src=srcftn()
                    src.append([mytoon.real_title,'newtoki',mytoon.title])
                    srcwriter(src)
                    homepagemaker()
                    searchindex()
                    mytoon.download()
                    mytoon.page_html()
                    mytoon.index_html()

                else:
                    print(f'{inf[1]} 웹툰 다운로드가 취소되었어요')
            else:
                print(f'{inf[1]} 웹툰은 이미 있어요')
        else:
            print(f'{inf[1]} 웹툰은 이미 있어요')



def req(url):
    return requests.get(url)
    tr=0
    maxtr=10
    while tr<maxtr:
        try:
            resp=requests.get(url)
            return resp
        except:
            tr+=1
    print('max try exceeded',maxtr,url)
    assert False
def searchnewtoki(query):
    soup = soupmaker(newtoki_domain + '/webtoon?stx=' + query.replace(' ', '+').replace('/',' ').replace('(',' ').replace(')',' '))
    lis = soup.find('ul', {'id': 'webtoon-list-all'}).findAll('li')
    results = {}
    for li in lis:
        results[li['date-title'].strip()] = int((li.find('a')['href'].split('/')[4].split('?')[0]))
    if query in results.keys():
        return query, results[query]
    if results == {}:
        print(f'{query}에 대한 검색결과가 없어요. 다른 검색어로 검색해보세요.')
        a = searchnewtoki(input('검색어 : '))
        return a
    print('추천 : ', [f"{i+1}. {list(results.keys())[i]}" for i in range(len(list(results.keys())))])
    inp=input((f'{query}에 대한 검색결과가 없어요. 위중 하나의 번호 혹은 이름을 골라 입력하거나, 다른 검색어를 입력해보세요.'))
    if inp=='' and len(results)==1:
        return list(results.keys())[0],results[list(results.keys())[0]]
    elif inp.isnumeric():
        return list(results.keys())[int(inp)-1],results[list(results.keys())[int(inp)-1]]
    elif inp in results.keys():
        return inp,results[inp]
    else:
        return searchnewtoki(inp)

def searchtkor(query):
    soup = soupmaker(tkor_domain + '/bbs/search.php?stx=' + query.replace(' ', '+').replace('/',' ').replace('(',' ').replace(')',' ').replace(':',' '))
    results={i.find('h3').text:i['href'][1:] for i in soup.findAll('a',{'id':'title'})}
    if query in results.keys():
        return query, results[query]
    if results == {}:
        print(f'{query}에 대한 검색결과가 없어요. 다른 검색어로 검색해보세요.')
        a = searchtkor(input('검색어 : '))
        return a
    print('추천 : ', [f"{i+1}. {list(results.keys())[i]}" for i in range(len(list(results.keys())))])
    inp=input((f'{query}에 대한 검색결과가 없어요. 위중 하나의 번호 혹은 이름을 골라 입력하거나, 다른 검색어를 입력해보세요.'))
    if inp=='' and len(results)==1:
        return list(results.keys())[0],results[list(results.keys())[0]]
    elif inp.isnumeric():
        return list(results.keys())[int(inp)-1],results[list(results.keys())[int(inp)-1]]
    elif inp in results.keys():
        return inp,results[inp]
    else:
        return searchtkor(inp)
def search(query,opt):

    if opt=='newtoki':
        return searchnewtoki(query)
    elif opt=='tkor':
        return searchtkor(query)
    else:
        print('opt error')
    assert False
def log(message):
    with open('log.txt', 'a') as logfile:
        logfile.write(str(dt.now()) + "\t" + message + '\n')
def combineImage(full_width,full_height,page_title,image_list,index,toon_title):
    canvas = Image.new('RGB', (full_width, full_height), 'white')
    output_height = 0
    for im in image_list:
        width, height = im.size
        if width<0.9*full_width:
            wpercent = (full_width/float(width))
            hsize = int((float(height)*float(wpercent)))
            im = im.resize((full_width,hsize), Image.ANTIALIAS)
        width, height = im.size
        canvas.paste(im, (0, output_height))
        output_height += height
    canvas.save(toon_title+'/out/'+page_title+"_combined_"+str(index)+'.jpg')
    #print(page_title+'_병합됨_'+str(index)+'.jpg')
def listImage(page_title,image_value,q,toon_title):
    full_width, full_height,index = 0, 0, 1
    image_list = []
    for i in image_value:
        im = Image.open(os.path.join('.',toon_title,'out',page_title+"_"+str(i)+'.jpg'))
        #print(page_title+"_"+str(i)+'.jpg 병합중')
        width, height = im.size
        if full_height+height > 65000:
            combineImage(full_width,full_height,page_title,image_list,index,toon_title)
            index = index + 1
            image_list = []
            full_width, full_height = 0, 0
        image_list.append(im)
        full_width = max(full_width, width)
        full_height += height
    combineImage(full_width,full_height,page_title,image_list,index,toon_title)
    # for i in image_value:
    #     os.remove(os.path.join(toon_title+'/out/'+page_title+"_"+str(i)+'.jpg'))
    #print(page_title+' 삭제중')
def filenamer(filename):
    return re.sub('[\*?|]','',filename).replace(' ', '_').replace('/','-').replace(':','-').replace('"',"'").replace('<','[').replace('>',']')
hdr = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_3_2 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13F69 Safari/601.1', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3', 'Accept-Encoding': 'none', 'Accept-Language': 'en-US,en;q=0.8', 'Connection': 'keep-alive'}
def download(url, file_name):
    if not os.path.isfile(file_name):
        with open(file_name, "wb") as file:
            response = req(url)
            file.write(response.content)


def every_already_counter(toon_title, page_titles_len):
    file_list = os.listdir(toon_title + '/out')
    alreadys = [0] * page_titles_len
    for i in file_list:
        imageparsed=imageparse(i)
        assert imageparsed
        alreadys[imageparsed[0]-1]+=1
    return alreadys


def already_counter(toon_title, page_index):
    file_list = os.listdir(toon_title + '/out')
    already = 0
    for i in file_list:
        imageparsed=imageparse(i)
        assert imageparsed
        if imageparsed[0]-1==page_index:
            already += 1
    return already


def direc():
    toons = []
    rootdir = '.'
    for toon in os.listdir(rootdir):
        d = os.path.join(rootdir, toon)
        if os.path.isdir(d):
            toons.append(toon)
    if 'info' in toons:
        toons.remove('info')
    if '__pycache__' in toons:
        toons.remove('__pycache__')
    if '.idea' in toons:
        toons.remove('.idea')
    if 'fontawesome' in toons:
        toons.remove('fontawesome')
    return toons


def homepagemaker():
    src=srcftn()
    #toons = direc()
    menus = ""
    ind = ""
    for i in src:
        try:
            auth = open("info/%s.txt" % i[2], mode="r", encoding='UTF-8').read()
        except:
            print(i)
            raise
        ind += '"%s",' % i[2]
        toonname = i[0] #i.replace("-", " ").replace('_',' ')
        menus += """
                <div class="column-xs-12 column-md-4" id="%s" onclick='location.href ="./%s"'>
    <figure class="img-container">
        <img src="%s" />
        <figcaption class="img-content">
        <h2  id="%s" class="title">%s</h2>
        <h3 class="category">%s</h3>
        </figcaption>
        <span class="img-content-hover">
        <h2  id="%s" class="title">%s</h2>
        <h3 class="category">%s</h3>
        </span>
    </figure>
    </div>""" % (i[2], i[2], "./info/%s.jpg" % i[2], i[2] + 'a', toonname, auth, i[2] + 'b', toonname, auth)
    ind = ind[:-1]
    temp = open("index_template.html", "r", encoding='UTF-8').read() % (menus, ind)
    with open("photo.html", mode='w', encoding='UTF-8') as indexhtml:
        indexhtml.write(temp)
        indexhtml.close()


def foldermaker(folder):
    global logging
    try:
        if not (os.path.isdir(folder)):
            os.makedirs(os.path.join(folder))
    except OSError as e:
        if e.errno != errno.EEXIST:
            print('could not make folder %s- maybe due to permission; use chmod' % folder)
            if logging: log('could not make folder %s- maybe due to permission; use chmod' % folder)
            raise
def srcftn():
    return [i.replace('\n','').split('\t') for i in open('src.txt','r',encoding='utf-8').readlines()]

def srcwriter(src):
    open('src.txt','w',encoding='utf-8').writelines(['\t'.join(i)+'\n' for i in src])
def update(opt='all'):
    src=srcftn()
    #print(src)
    pbar=tqdm(src)
    for info in pbar:
        if opt=='all' or opt==info[1]:
            mytoon=toon(info[1],info[0])
            pbar.set_description(f"<{info[0]}> 웹툰을 {info[1]}에서 업데이트 중이에요")
            mytoon.download()
            mytoon.page_html()
            mytoon.index_html()
            homepagemaker()
            searchindex()
        # except: 
        #     pbar.set_description(f"<{info[0]}> 웹툰은 {info[1]}에서 캡챠가 걸려있는것 같아요")
        
def updatehtml(opt="all"):
    src=[i for i in srcftn() if (opt==i[1] or opt=='all')]
    #print(src)
    pbar=tqdm(src)
    for info in pbar:

        mytoon=toon(info[1],info[0])
        pbar.set_description(f"<{info[0]}> 웹툰을 {info[1]}에서 html만 업데이트 중이에요")
        mytoon.page_html()
        mytoon.index_html()
        homepagemaker()
        searchindex()
        # except: 
        #     pbar.set_description(f"<{info[0]}> 웹툰은 {info[1]}에서 캡챠가 걸려있는것 같아요")
        
def pagenumcounter(title):
    pages=os.listdir(title)
    res=0
    for i in pages:
        if not i in ['out','index.html']:
            res+=1
    return res
def appendtoon(query,option):
    mytoon=toon(option,query)
    src=srcftn()
    alreadytoons={j[0]:j[1] for j in src}
    if not mytoon.real_title in alreadytoons:
        src=srcftn()
        src.append([mytoon.real_title,option,mytoon.title])
        srcwriter(src)
        print(f'{mytoon.real_title} 웹툰을 추가했어요')
    else:
        print(f'{mytoon.real_title} 웹툰은 이미 있어요. 업데이트 할게요')
        mytoon=toon(alreadytoons[mytoon.real_title],mytoon.real_title)    
        print(every_already_counter(mytoon.title,len(mytoon.page_titles)))
    mytoon.download()
    mytoon.page_html()
    mytoon.index_html()
    homepagemaker()
    searchindex()
def searchindex():
    buttons=""
    toons=''
    src=srcftn()
    colordict={'newtoki':'red','tkor':'blue'}
    for info in src:
        #mytoon=toon(info[1],info[0])
        toons+='''<div onclick='location.href="%s"' class="element-item %s" data-isotope-sort-name="%s"><span>%d</span>%s</div>'''%('/'+info[2],colordict[info[1]],info[0],pagenumcounter(info[2]),info[0])
    for color in colordict:
        buttons+='''<button class="button" data-filter=".%s">%s</button>'''%(colordict[color],color)
    open('index.html','w',encoding='utf-8').write(open('searchtemplate.html','r',encoding='utf-8').read()%(buttons,toons))

class toon:
    def __init__(self, option, query):
        self.option = option
        if not query.isnumeric():

            res=search(query,option)
            self.real_title=res[0]
            info=res[1]

            if option == 'newtoki':
                self.address, self.page_addresses, self.page_titles, self.title, self.thumb, self.description, self.like,self.real_title = self.newtoki_toontopages(
                    info)
                #print(self.title,self.option,self.address,f'총 {len(self.page_titles)}화')
            if option == 'tkor':
                # valid = not "존재하지 않는 게시판입니다." in req(tkor_domain + "/" + query.replace(' ', '_')).text
                # while not valid:
                #     query = input('웹툰 제목이 잘못되었거나 특수문자 등의 이유로 주소 상 제목이 잘못되었습니다. 다시 시도해보세요 : ')
                #     valid = not "존재하지 않는 게시판입니다." in req(tkor_domain + "/" + query.replace(' ', '_')).text
                self.title = info
                self.address, self.page_addresses, self.page_titles, self.thumb, self.authors, self.description = self.tkor_toontopages(
                    info)
                #print(self.title,self.option,self.address,self.authors,f'총 {len(self.page_titles)}화')
        else:
            self.address, self.page_addresses, self.page_titles, self.title, self.thumb, self.description, self.like,self.real_title = self.newtoki_toontopages(query)
        # print(repr(self.title))

        foldermaker('info')
        foldermaker(self.title)
        foldermaker(os.path.join(self.title, 'out'))
        download(self.thumb, "info/%s.jpg" % self.title)
        with open("info/%s.txt" % self.title, mode="w", encoding='UTF-8') as intro:
            if self.option == 'tkor':
                intro.write(self.authors + ' ')
            intro.write("총 %d화" % len(self.page_titles))
            intro.write(" ")
            intro.write(self.description)
            intro.close()
    def intro(self):
        with open("info/%s.txt" % self.title, mode="r", encoding='UTF-8') as intro:
            return intro.read()

    def newtoki_toontopages(self, toon_id):
        toon_address = newtoki_domain + '/webtoon/' + str(toon_id)
        soup = soupmaker(toon_address)
        toons = soup.select('form div ul li div a')
        page_addresses = [newtoki_domain + '/webtoon/' + i['href'].split('/')[4] for i in toons]
        page_addresses.reverse()
        page_titles = [filenamer(' '.join(i.text.strip().split('\n')[-1].split(' ')[:-1]).strip()) for i in toons]
        page_titles.reverse()
        real_title=soup.select(
            '#content_wrapper > div.content > div > div.view-wrap > section > article > div.view-title > div > div > div.col-sm-8 > div:nth-child(1) > span > b')[0].text.strip()
        toon_title = filenamer(real_title)
        try:
            des = soup.select('#content_wrapper > div.content > div > div.view-wrap > section > article > div.view- title > div > div > div.col-sm-8 > div:nth-child(2) > p')[0].text
        except:
            des=''
        likes = int(soup.find('b', {'id': 'wr_good'}).text.replace(',',''))
        thumb = soup.select(
            '#content_wrapper > div.content > div > div.view-wrap > section > article > div.view-title > div > div > div.col-sm-4 > div > div > img')[
            0]['src']
        #print(toon_address, toon_title, des, thumb)
        return toon_address, page_addresses, page_titles, toon_title, thumb, des, likes,real_title

    def tkor_toontopages(self, toon_title):
        toon_address = tkor_domain + "/" + toon_title  # if it doesnt work, replace space with _ in toon_title
        soup = soupmaker(toon_address)
        page_addresses = [tkor_domain + i['data-role'] for i in
                          soup.find_all("td", {"class": "episode__index", 'name': 'view_list'})]
        page_titles = [filenamer(i['data-role'][1:-5]) for i in
                       soup.find_all("td", {"class": "episode__index", 'name': 'view_list'})]
        page_titles.reverse()
        page_addresses.reverse()
        thumb = tkor_domain + soup.select_one("#containerCol > table.bt_view1 > tbody > tr > td.bt_thumb > a > img")[
            'src']
        auth = soup.find("span", "bt_data").text
        des = soup.find("td", "bt_over").text
        #print(toon_address, toon_title, des, thumb)
        return toon_address, page_addresses, page_titles, thumb, auth, des

    def index_html(self):
        toon_title = self.title
        page_titles = self.page_titles
        with open(toon_title + "/index.html", mode="w", encoding='UTF-8') as file:
            tempa = ""
            for j in range(len(page_titles)):
                tempa += """  <a href="./%d.html">
                <article class="site">
                        <h2 class="name">%s</h2>
    <input class="checkbox" type="checkbox" id="%d" onclick='changecookie(this);'/>
    <label for="%d" style="position: absolute; right: 0px; top: 0px;">
    </label>
    </article>
        </a>""" % (j + 1, page_titles[j], j + 1, j + 1)
            try:
                auth = open("info/%s.txt" % toon_title, mode="r", encoding='UTF-8').read()
            except ValueError:
                print(toon_title)
                raise
            temp = open("page_index_template.html", mode="r", encoding='UTF-8').read() % (
                toon_title, '../info/%s.jpg' % toon_title, auth, tempa, toon_title, len(page_titles))
            file.write(temp)
            file.close()

    def page_html(self):
        toon_title = self.title
        page_titles = self.page_titles
        page_addresses = self.page_addresses
        option = self.option
        for page_index in range(len(page_titles)):
            self.html(toon_title, page_titles[page_index], page_index)

    def download(self, *args, **kwargs):
        toon_title = self.title
        page_titles = self.page_titles
        page_addresses = self.page_addresses
        option = self.option
        start = kwargs.get('start', 1)
        end = kwargs.get('end', len(page_addresses))
        already = every_already_counter(toon_title, len(page_titles))
        #print(already)
        start -= 1  # in list's index
        # this part can cause error, so if something happends remove this part
        if not overwrite:
            if not 0 in already:
                start = end
            else:
                start = min(max(start, already.index(0) - 1), end)
        for page_index in range(start, end):
            temppage = page(page_titles[page_index], page_addresses[page_index], page_index, option, toon_title)
            if not temppage.image_addresses==[]:
                temppage.download()
            else:
                copyfile(f'info/{self.title}.jpg',os.path.join('.', toon_title, 'out', f'{page_index+1}_1.jpg'))
                print('이미지가 없어서 썸네일로 대신했어요.',os.path.join('.', toon_title, 'out', f'{page_index+1}_1.jpg'))
            self.html(toon_title, page_titles[page_index], page_index)

    def html(self, toon_title, page_title, page_index):
        mp3filename = ''
        for mp3 in os.listdir('.'):
            if mp3.endswith('.mp3'):
                mp3filename = mp3
        with open(toon_title + '/' + str(page_index + 1) + ".html", mode="w", encoding='UTF-8') as file:
            tempa = ""
            for j in range(1, already_counter(toon_title, page_index) + 1):
                tempa += f'<div style="font-size:0;"><img src="./out/{page_index+1}_{j}.jpg" style="border:0px;margin:0px; width: 40%; height: auto;" alt="" ' \
                         'style="vertical-align: top;"></div> '
            temp = open("page_template.html", "r", encoding='UTF-8').read() % (
                page_title, page_index + 1, page_title, page_index, page_index + 2, mp3filename, tempa, toon_title,
                page_index + 1, page_index, page_index + 2)
            file.write(temp)
            file.close()


class page:
    def __init__(self, page_title, page_address, page_index, option, toon_title):
        self.option = option
        self.title = page_title
        self.address = page_address
        self.index = page_index
        self.toon_title = toon_title
        if option == 'tkor':
            self.image_addresses, self.image_titles = self.tkor_pagetoimages(page_address, page_title,page_index)
        if option == 'newtoki':
            self.image_addresses, self.image_titles = self.newtoki_pagetoimages(page_address, page_title,page_index)

    def tkor_pagetoimages(self, page_address, page_title,page_index):
        soup = soupmaker(page_address)
        scripts = soup.find_all('script')
        matching = [str(s) for s in scripts if "toon_img" in str(s)]
        encryptedtext = matching[0].split("toon_img = '")[1].split("'")[0]
        address = base64.b64decode(encryptedtext).decode('UTF-8').split('src="')
        #a = address[1].split('"')[0][0] != "h"

        image_addresses = []
        for add in address[1:]:
            realadd=add.split('"')[0]
            if realadd.startswith('/'):
                realadd=tkor_domain+realadd
            if 'toonkor.com' in realadd:
                realadd=realadd.replace('https://www.toonkor.com',tkor_domain)
            if realadd.endswith('.gif'):
                print(realadd,' 는 광고 이미지였어요')
            else:
                image_addresses.append(realadd)
        image_titles = [str(page_index+1) + '_' + str(j) + '.jpg' for j in range(1, len(image_addresses) + 1)]
        return image_addresses, image_titles
    def tkr_pagetoimages(self, page_address, page_title):
        image_addresses=[i.split('"')[0] for i in base64.b64decode(requests.get(page_address).text.split('tnimg')[2].split("'")[1]).decode('UTF-8').split('src="')[1:]]
        image_titles = [page_title + '_' + str(j) + '.jpg' for j in range(1, len(image_addresses) + 1)]
        return image_addresses, image_titles
    def newtoki_pagetoimages(self, page_address, page_title,page_index):
        soup=soupmaker(page_address)
        script = soup.select('section article div script')[0]
        encrypted = (''.join(str(script).split("';\nhtml_data+=\'")[1:-1])).split('.')[:-1]
        temp = ''
        for j in encrypted:
            try: temp += bytearray.fromhex(j).decode(errors='replace')
            except: print(page_address,page_title,script,'페이지에 에러가 있는 것 같아요'); open('script.html','w').write(str(script)); return [],[]

        soup = bs(temp, 'html.parser')
        images = soup.find_all('img', {'src': "/img/loading-image.gif"})
        try:
            attrkeys = list(images[0].attrs.keys())
            for ke in attrkeys:
                if ke.startswith('data'):
                    attrkey=ke
            temp_image_addresses = [k[attrkey] for k in images]
            image_addresses=[]
            for k in temp_image_addresses:
                if k.startswith('/'):
                    k=newtoki_domain+k
                if not k.endswith('.gif'):
                    image_addresses.append(k)
                else:
                    print(k,'는 광고 이미지였어요')
            #print(image_addresses)
            image_titles = [str(page_index+1) + '_' + str(j) + '.jpg' for j in range(1, len(image_addresses) + 1)]
            return image_addresses, image_titles
        except:
            print(soup.find_all('img'))
            print(f'{page_title}({page_address})에 이미지가 없어요. 아마 휴재회차거나 그럴거에요')
            return [],[]

    def download(self):
        global cpunum
        image_addresses, image_titles, toon_title = self.image_addresses, self.image_titles, self.toon_title
        def fetch_url(entry):
            path, uri = entry
            if not os.path.exists(path):
                try: r = requests.get(uri, stream=True)
                except: print(uri); raise
                
                if r.status_code == 200:
                    with open(path, 'wb') as f:
                        for chunk in r:
                            f.write(chunk)
            return path
        start=timer()
        urls=[(os.path.join('.', toon_title, 'out', image_titles[i]),image_addresses[i]) for i in range(len(image_titles))]
        results = ThreadPool(cpunum).imap_unordered(fetch_url, urls)
        pbar=tqdm(results)
        for pa in pbar:
            pbar.set_description(f"{self.title} 다운로드 중이에요")
        print(f"{round(timer() - start,2)} 초가 걸렸어요")
        #old versions
        # print(image_titles)
        # for i in tqdm(range(len(image_titles)), desc="%s is being downloaded" % self.title):
        #     file_name = os.path.join('.', toon_title, 'out', image_titles[i])
        #     if not os.path.isfile(file_name):
        #         with open(file_name, "wb") as file:
        #             response = req(image_addresses[i])
        #             file.write(response.content)
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--newtoki", help="뉴토끼",action="store_true")
    parser.add_argument("-t", "--tkor", help="툰코",action="store_true")
    parser.add_argument("-l", "--list", help="전체 리스트",action="store_true")
    parser.add_argument("-u", "--update", help="src.txt의 모든 웹툰을 업데이트해요",action="store_true")
    parser.add_argument("-ht", "--html", help="src.txt의 모든 웹툰을 html만 업데이트해요",action="store_true")
    parser.add_argument("-a", "--append",help="하나의 웹툰을 다운받아요. 띄어쓰기가 있다면 따옴표로 감싸세요")
    parser.add_argument('-al', '--appendlist', nargs='+', default=[],help='여러개의 웹툰을 다운받아요. 여러개를 띄어쓰기로 구분해 나열하세요.')
    parser.add_argument("-hp", "--homepage", help="액자식 홈페이지를 만들어요",action="store_true")
    parser.add_argument("-si", "--searchindex", help="목록식 홈페이지를 만들어요",action="store_true")
    parser.add_argument("-o", "--overwrite", help="이미지 하나씩 확인해요",action="store_true")
    parser.add_argument("-Y", "--yestoall", help="무지성으로 확인절차 없이 다운해요",action="store_true")
    parser.add_argument("-good", "--goodnewtoki", help="좋아요가 많은 뉴토끼 웹툰을 다운받을 개수를 정해요",type=int)
    parser.add_argument("-goodnsfw", "--goodnewtokinsfw", help="좋아요가 많은 뉴토끼 NSFW 웹툰을 다운받을 개수를 정해요",type=int)
    parser.add_argument("-view", "--viewnewtoki", help="조회수가 많은 뉴토끼 웹툰을 다운받을 개수를 정해요",type=int)
    parser.add_argument("-viewnsfw", "--viewnewtokinsfw", help="조회수가 많은 뉴토끼 NSFW 웹툰을 다운받을 개수를 정해요",type=int)
    parser.add_argument("-new", "--newnewtoki", help="최근에 나온 뉴토끼 웹툰을 다운받을 개수를 정해요",type=int)
    parser.add_argument("-newnsfw", "--newnewtokinsfw", help="최근에 나온 뉴토끼 NSFW 웹툰을 다운받을 개수를 정해요",type=int)
    parser.add_argument("-i", "--intro",help="소개말을 출력해요")
    parser.add_argument("-s", "--sensitive", help="자극적인 정보를 모두 숨깁니다",action="store_true")
    parser.add_argument("-er", "--error", help="에러를 보여줘요",action="store_true")
    parser.add_argument('-pt', '--populartkor', nargs='+', default=[],help='툰코에서 옵션으로 웹툰을 다운받아요')
    args = parser.parse_args()
    overwrite=args.overwrite
    if args.error:
        src=set([i[2] for i in srcftn()])
        dir=set(direc())
        print('폴더는 있는데 src에 없는 것')
        print(dir-src)
        print('src는 있는데 실제로 없는 것')
        print(src-dir)
    if args.populartkor!=[]:
        lenofopts=len(args.populartkor)
        if lenofopts==2:
            downloadpopulartkor(args.populartkor[0],args.populartkor[1],10,args.yestoall)
        elif lenofopts==3:
            downloadpopulartkor(args.populartkor[0],args.populartkor[1],int(args.populartkor[2]),args.yestoall)
        else:
            assert False
    if args.intro!=None:
        src=srcftn()
        realtitle=False
        if (not (args.newtoki or args.tkor)) or (args.newtoki and args.tkor):
            realtitle=True
            orig_titles=[i[0] for i in src]
            underbared_titles=[i[2] for i in src]
            if args.intro in orig_titles:
                title={i[0]:i[2] for i in src}[args.intro]
                with open("info/%s.txt" % title, mode="r", encoding='UTF-8') as intr:
                    print(intr.read())
            elif args.intro in underbared_titles:
                with open("info/%s.txt" % args.intro, mode="r", encoding='UTF-8') as intr:
                    print(intr.read())
            else:
                realtitle=False
                inp=input('이미 다운 받은 목록에 없습니다.  n 또는 t 옵션을 입력해주세요')
                if inp in ['n','newtoki']:
                    opt='newtoki'
                elif inp in ['t','tkor']:
                    opt='tkor'
                else:
                    print('옵션이 틀렸어요')
                    raise
        elif args.newtoki:
            opt='newtoki'
        else:
            opt='tkor'
        if  not realtitle:
            mytoon=toon(opt,args.intro)
            with open("info/%s.txt" % mytoon.title, mode="r", encoding='UTF-8') as intr:
                print(intr.read())
        

        print()
    if args.append!=None or args.appendlist!=[]:
        if (not (args.newtoki or args.tkor)) or (args.newtoki and args.tkor):
            inp=input('n 또는 t 옵션을 입력해주세요')
            if inp in ['n','newtoki']:
                opt='newtoki'
            elif inp in ['t','tkor']:
                opt='tkor'
            else:
                print('옵션이 틀렸어요')
                raise
        elif args.newtoki:
            opt='newtoki'
        else:
            opt='tkor'
        if args.append!=None:
            ag=args.append
            if ag.startswith('.\\'):
                ag=ag[2:-1]
            appendtoon(ag,opt)
        if args.appendlist!=[]:
            for i in args.appendlist:
                appendtoon(i,opt)
    if args.list:
        print(srcftn())
    if args.update:
        if (args.newtoki and args.tkor):
            raise
        elif args.newtoki:
            update('newtoki')
        elif args.tkor:
            update('tkor')
        else:
            update()
    if args.html:
        if (args.newtoki and args.tkor):
            raise
        elif args.newtoki:
            updatehtml('newtoki')
        elif args.tkor:
            updatehtml('tkor')
        else:
            updatehtml()
    if args.homepage:
        homepagemaker()
    if args.searchindex:
        searchindex()
    if args.goodnewtoki!=None:
        downloadpopularnewtoki('as_good',False,args.goodnewtoki,args.yestoall)
    if args.goodnewtokinsfw!=None:
        downloadpopularnewtoki('as_good',True,args.goodnewtokinsfw,args.yestoall)
    if args.viewnewtoki!=None:
        downloadpopularnewtoki('as_view',False,args.viewnewtoki,args.yestoall)
    if args.viewnewtokinsfw!=None:
        downloadpopularnewtoki('as_view',True,args.viewnewtokinsfw,args.yestoall)
    if args.newnewtoki!=None:
        downloadpopularnewtoki('',False,args.newnewtoki,args.yestoall)
    if args.newnewtokinsfw!=None:
        downloadpopularnewtoki('',True,args.newnewtokinsfw,args.yestoall)

    # src=srcftn()
    # for too in src:

    #     mytoon=toon(too[1],too[0])
    #     pagetitle=mytoon.page_titles
    #     for j in range(len(pagetitle)):
    #         print(pagetitle[j])
    #         images=os.listdir(os.path.join('.',too[2],'out'))
    #         for image in images:
    #             if pagetitle[j] in image and image.replace(pagetitle[j]+'_','')[:-4].isnumeric():
    #                 os.rename(os.path.join('.',too[2],'out',image),os.path.join('.',too[2],'out',image.replace(pagetitle[j],str(j+1))))
        


