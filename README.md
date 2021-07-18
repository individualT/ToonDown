툰코 다운로더
=============

크게 Toon 과 Page 클래스가 있고, 각각의 클래스에서 option으로 웹툰 사이트를 정해주게 되면  
제목이나 웹툰의 id를 입력하였을 때 내장함수들을 활용하여 많은 것을 할 수 있다.  

사용 예:  


    from core import toon, page, homepagemaker
    option='newtoki'
    info=14530561
    mytoon=toon(option,info)
    mytoon.download() #다운로드
    mytoon.page_html() #웹툰 보는 용 html
    mytoon.index_html() #웹툰 목록 용 html
    homepagemaker() #웹툰 홈 용 html
  


image combine 기능도 제공하나 아직 내장함수로는 넣지 않았다.
