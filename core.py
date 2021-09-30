import errno
import requests
import base64
from bs4 import BeautifulSoup as bs
import os
from tqdm import tqdm
from datetime import datetime as dt
import re

overwrite = False
loggin = False
domains = {i[0]:i[1] for i in [j.replace('\n','').split(' ') for j in open('domain.txt', 'r').readlines()]}
newtoki_domain = domains['newtoki_domain'] #requests.get('https://newtoki13.org').url[:-1] 
tkor_domain = domains['tkor_domain']
def req(url):
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
    soup = bs(req(newtoki_domain + '/webtoon?stx=' + query.replace(' ', '+')).text, 'html.parser')
    lis = soup.find('ul', {'id': 'webtoon-list-all'}).findAll('li')
    results = {}
    for li in lis:
        results[li['date-title'].strip()] = int((li.find('a')['href'].split('/')[4].split('?')[0]))
    if query in results.keys():
        return query, results[query]
    if results == {}:
        print(f'{query}에 대한 검색결과가 없습니다. 다른 검색어로 검색해보세요.')
        a = searchnewtoki(input('검색어 : '))
        return a
    print(results)
    print('추천 : ', list(results.keys()))
    inp=input((f'{query}에 대한 검색결과가 없습니다. 위중 하나의 번호 혹은 이름을 골라 입력하거나, 다른 검색어를 입력해보세요.'))
    if inp.isnumeric():
        return list(results.keys())[int(inp)-1],results[list(results.keys())[int(inp)-1]]
    elif inp in results.keys():
        return inp,results[inp]
    else:
        return searchnewtoki(inp)
def searchtkor(query):
    soup = bs(req(tkor_domain + '/bbs/search.php?stx=' + query.replace(' ', '+')).text, 'html.parser')
    results={i.find('h3').text:i['href'][1:] for i in soup.findAll('a',{'id':'title'})}
    if query in results.keys():
        return query, results[query]
    if results == {}:
        print(f'{query}에 대한 검색결과가 없습니다. 다른 검색어로 검색해보세요.')
        a = searchtkor(input('검색어 : '))
        return a
    print(results)
    print('추천 : ', list(results.keys()))
    inp=input((f'{query}에 대한 검색결과가 없습니다. 위중 하나의 번호 혹은 이름을 골라 입력하거나, 다른 검색어를 입력해보세요.'))
    if inp.isnumeric():
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

def filenamer(filename):
    return re.sub('[\*?|]','',filename).replace(' ', '_').replace('/','-').replace(':','-').replace('"',"'").replace('<','[').replace('>',']')
hdr = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_3_2 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13F69 Safari/601.1', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3', 'Accept-Encoding': 'none', 'Accept-Language': 'en-US,en;q=0.8', 'Connection': 'keep-alive'}
def download(url, file_name):
    if not os.path.isfile(file_name):
        with open(file_name, "wb") as file:
            response = req(url)
            file.write(response.content)


def every_already_counter(toon_title, page_titles):
    file_list = os.listdir(toon_title + '/out')
    alreadys = [0] * len(page_titles)
    for i in file_list:
        for j in range(len(page_titles)):
            if i.startswith(page_titles[j]):
                alreadys[j] += 1
    return alreadys


def already_counter(toon_title, page_title):
    file_list = os.listdir(toon_title + '/out')
    already = 0
    for i in file_list:
        if i.startswith(page_title):
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
    return toons


def homepagemaker():
    toons = direc()
    menus = ""
    ind = ""
    for i in toons:
        try:
            auth = open("info/%s.txt" % i, mode="r", encoding='UTF-8').read()
        except:
            print(i)
            raise
        ind += '"%s",' % i
        toonname = i.replace("-", " ")
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
    </div>""" % (i, i, "./info/%s.jpg" % i, i + 'a', toonname, auth, i + 'b', toonname, auth)
    ind = ind[:-1]
    temp = open("index_template.html", "r", encoding='UTF-8').read() % (menus, ind)
    with open("index.html", mode='w', encoding='UTF-8') as indexhtml:
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
    return [[' '.join(i.split(' ')[:-1]),i.split(' ')[-1].replace('\n','')] for i in open('src.txt','r').readlines()]
def srcwriter(src):
    open('src.txt','w').writelines([i[0]+' '+i[1]+'\n' for i in src])
def update():
    src=srcftn()
    #print(src)
    for info in src:
        mytoon=toon(info[1],info[0])
        mytoon.download()
        mytoon.page_html()
        mytoon.index_html()
    homepagemaker()
class toon:
    def __init__(self, option, query):
        self.option = option
        res=search(query,option)
        self.real_title=res[0]
        info=res[1]
        
        if option == 'newtoki':
            self.address, self.page_addresses, self.page_titles, self.title, self.thumb, self.description, self.like = self.newtoki_toontopages(
                info)
            print(self.title,self.option,self.address,self.like)
        if option == 'tkor':
            # valid = not "존재하지 않는 게시판입니다." in req(tkor_domain + "/" + query.replace(' ', '_')).text
            # while not valid:
            #     query = input('웹툰 제목이 잘못되었거나 특수문자 등의 이유로 주소 상 제목이 잘못되었습니다. 다시 시도해보세요 : ')
            #     valid = not "존재하지 않는 게시판입니다." in req(tkor_domain + "/" + query.replace(' ', '_')).text
            self.title = info
            self.address, self.page_addresses, self.page_titles, self.thumb, self.authors, self.description = self.tkor_toontopages(
                info)
            print(self.title,self.option,self.address,self.authors)
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

    def newtoki_toontopages(self, toon_id):
        toon_address = newtoki_domain + '/webtoon/' + str(toon_id)
        response = req(toon_address)
        soup = bs(response.text, 'html.parser')
        toons = soup.select('form div ul li div a')
        page_addresses = [newtoki_domain + '/webtoon/' + i['href'].split('/')[4] for i in toons]
        page_addresses.reverse()
        page_titles = [filenamer(' '.join(i.text.strip().split('\n')[-1].split(' ')[:-1]).strip()) for i in toons]
        page_titles.reverse()
        toon_title = filenamer(soup.select(
            '#content_wrapper > div.content > div > div.view-wrap > section > article > div.view-title > div > div > div.col-sm-8 > div:nth-child(1) > span > b')[
            0].text.strip())
        des = soup.select(
            '#content_wrapper > div.content > div > div.view-wrap > section > article > div.view-title > div > div > div.col-sm-8 > div:nth-child(2) > p')[
            0].text

        likes = int(soup.find('b', {'id': 'wr_good'}).text)
        thumb = soup.select(
            '#content_wrapper > div.content > div > div.view-wrap > section > article > div.view-title > div > div > div.col-sm-4 > div > div > img')[
            0]['src']
        #print(toon_address, toon_title, des, thumb)
        return toon_address, page_addresses, page_titles, toon_title, thumb, des, likes

    def tkor_toontopages(self, toon_title):
        toon_address = tkor_domain + "/" + toon_title  # if it doesnt work, replace space with _ in toon_title
        soup = bs(req(toon_address).text, 'html.parser')
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
        already = every_already_counter(toon_title, page_titles)
        print(already)
        start -= 1  # in list's index
        # this part can cause error, so if something happends remove this part
        if not overwrite:
            if not 0 in already:
                start = end
            else:
                start = min(max(start, already.index(0) - 1), end)
        for page_index in range(start, end):
            temppage = page(page_titles[page_index], page_addresses[page_index], page_index, option, toon_title)
            temppage.download()
            self.html(toon_title, page_titles[page_index], page_index)

    def html(self, toon_title, page_title, page_index):
        mp3filename = ''
        for mp3 in os.listdir('.'):
            if mp3.endswith('.mp3'):
                mp3filename = mp3
        with open(toon_title + '/' + str(page_index + 1) + ".html", mode="w", encoding='UTF-8') as file:
            tempa = ""
            for j in range(1, already_counter(toon_title, page_title) + 1):
                tempa += '<div style="font-size:0;"><img src="./out/' + page_title + '_' + str(
                    j) + '.jpg" style="border:1px;margin:0px; width: 40%; height: auto;" alt="" ' \
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
            self.image_addresses, self.image_titles = self.tkor_pagetoimages(page_address, page_title)
        if option == 'newtoki':
            self.image_addresses, self.image_titles = self.newtoki_pagetoimages(page_address, page_title)

    def tkor_pagetoimages(self, page_address, page_title):
        soup = bs(req(page_address).text, 'html.parser')
        scripts = soup.find_all('script')
        matching = [str(s) for s in scripts if "toon_img" in str(s)]
        encryptedtext = matching[0].split("toon_img = '")[1].split("'")[0]
        address = base64.b64decode(encryptedtext).decode('UTF-8').split('src="')
        a = address[1].split('"')[0][0] != "h"
        image_addresses = []
        for j in range(1, len(address)):
            if address[j].split('"')[0].endswith('.gif'):
                print(tkor_domain * a + address[j].split('"')[0] + ' was advertisement image')
            else:
                image_addresses.append((tkor_domain * a + address[j].split('"')[0]))
        image_titles = [page_title + '_' + str(j) + '.jpg' for j in range(1, len(image_addresses) + 1)]
        return image_addresses, image_titles

    def newtoki_pagetoimages(self, page_address, page_title):
        response = req(page_address)
        soup = bs(response.text, 'html.parser')
        script = soup.select('section article div script')[0]
        encrypted = (''.join(str(script).split("';\nhtml_data+=\'")[1:-1])).split('.')[:-1]
        temp = ''
        for j in encrypted:
            try: temp += bytearray.fromhex(j).decode(errors='replace')
            except: print(page_address,page_title,script,'페이지 에러'); open('script.html','w').write(str(script)); return [],[]
        
        soup = bs(temp, 'html.parser')
        images = soup.find_all('img', {'src': "/img/loading-image.gif"})
        attrkeys = list(images[0].attrs.keys())
        for ke in attrkeys:
            if ke.startswith('data'):
                attrkey=ke
        temp_image_addresses = [k[attrkey] for k in images]
        image_addresses=[]
        for k in temp_image_addresses:
            if not k.endswith('.gif'):
                image_addresses.append(k)
        #print(image_addresses)
        image_titles = [page_title + '_' + str(j) + '.jpg' for j in range(1, len(image_addresses) + 1)]
        return image_addresses, image_titles

    def download(self):
        image_addresses, image_titles, toon_title = self.image_addresses, self.image_titles, self.toon_title
        # print(image_titles)
        for i in tqdm(range(len(image_titles)), desc="%s is being downloaded" % self.title):
            file_name = os.path.join('.', toon_title, 'out', image_titles[i])
            if not os.path.isfile(file_name):
                with open(file_name, "wb") as file:
                    response = req(image_addresses[i])
                    file.write(response.content)
if __name__ == "__main__":
    update()