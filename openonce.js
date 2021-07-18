var strReturn;
//아래에 정의되어 있는 GetCookie()라는 함수를 호출하여 현재 쿠키값이 있는지 확인
strReturn = GetCookie('test_cookie');
//만약 쿠키가 없다면 starPop()함수를 호출하여 오픈 창으로 이벤트 페이지 실행
if(strReturn == null || strReturn == '0'){
    starPop();
}

function GetCookie(sName){
    /*저장되어있는 쿠키 정보 불러오기
    오픈 페이지에서 부여하는 쿠키의 이름 및 값을 aCookie라는 변수에 저장.
    여기서는 test_cookie=1이란 값이 저장 */
    var aCookie = document.cookie.split("; ");
    //검색을 원하는 쿠키명(test_cookie)과 저장되어 있는 쿠키의 이름이 일치하는지 확인
    for(var i=0; i<aCookie.length; i++){
        var aCrumb = aCookie[i].split("=");
        if(sName == aCrumb[0]){
            return unescape(aCrumb[1]);
        }
    }
    return null;
}
//쿠키가 없을 경우 오픈창을 띄우는 스크립트 
function starPop(){
    window.open('../popup.html','popup', 'width=650, height=280');
}
