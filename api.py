import re
import urllib
from urllib.parse import urlencode

import requests
from selenium.webdriver.common.by import By


### 프랜차이즈
##############################

def get_franchise_url(page):
    params = {
        'searchCondition': '',
        'searchKeyword': '',
        'column': 'brd',
        'selUpjong': '',
        'selIndus': '',
        'pageUnit': '300',
        'pageIndex': page,
    }

    base_url = "https://franchise.ftc.go.kr/mnu/00013/program/userRqst/list.do"
    return f"{base_url}?{urlencode(params)}"

def franchise_detail_link_parser(link):
    match = re.search(r"fn_moveUrl\('([^']*)'\s*,\s*'([^']*)'\)", link)

    if match:
        param1, param2 = match.groups()

        return f"https://franchise.ftc.go.kr{param1 + urllib.parse.quote(param2, safe='')}"
    else:
        print("매개변수 추출 실패")

def remove_label(driver, element):
    try:
        label = element.find_element(By.CSS_SELECTOR, 'label')
        driver.execute_script("arguments[0].remove();", label)
    except:
        pass

    return element.text.strip()

##############################
### 종합건설
##############################

def get_general_construction_tasks_header(driver):
    driver.get("https://www.cak.or.kr/lay1/program/S1T56C252/biz/bizSearch.do")
    jsession_cookie = driver.get_cookie("JSESSIONID")
    jsession_id = ''
    if jsession_cookie:
        jsession_id = jsession_cookie['value']
    csrf_token = driver.find_element(By.CSS_SELECTOR, 'meta[name="_csrf"]').get_attribute("content")

    driver.close()

    return jsession_id, csrf_token

def general_construction_request(csrf_token, jsession_id, page):
    cookies = {
        'JSESSIONID': jsession_id,
    }
    headers = {
        'AJAX': 'true',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,zh;q=0.6',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://www.cak.or.kr',
        'Referer': 'https://www.cak.or.kr/lay1/program/S1T56C252/biz/bizSearch.do',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'X-CSRF-TOKEN': csrf_token,
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'Cookie': f'JSESSIONID={jsession_id}'
    }

    data = f'srh_closed=commBiz&srh_sort=sigong&srh_sort_dir=DESC&srh_sangho=&srh_nm=&srh_type_city=1&srh_city=&srh_sikun=&srh_sigong=&handoamt_min=&handoamt_max=&srh_upjong=&srh_upjong_detail=&handoamt_min2=&handoamt_max2=&srh_young=&srh_sangsi=&srh_comp_type=&srh_etc2=&srh_etc3=&srh_etc4=&srh_etc5=&cpage={page}&pageUnit=50&firstIndex={page}'

    return requests.post('https://www.cak.or.kr/biz/ajax/srchBizList.do', headers=headers, cookies=cookies, data=data)

def general_construction_detail_request(csrf_token, jsession_id, hwno):
    cookies = {
        'JSESSIONID': jsession_id,
    }
    headers = {
        'AJAX': 'true',
        'Accept': '*/*',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,zh;q=0.6',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://www.cak.or.kr',
        'Referer': 'https://www.cak.or.kr/lay1/program/S1T56C252/biz/bizSearchView.do',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'X-CSRF-TOKEN': csrf_token,
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'Cookie': f'JSESSIONID={jsession_id}'
    }

    data = {
        'hwno': f'{hwno}',
    }

    return requests.post('https://www.cak.or.kr/biz/ajax/bizSearchDetailView.do', headers=headers, cookies=cookies, data=data)