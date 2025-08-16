import copy
import json
import os
import random
import re
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from log_type import LogType
from logger import logger

referers = [
    'https://www.musinsa.com'
    'https://www.musinsa.com/main/musinsa/release?sectionId=91&gf=A',
    'https://www.musinsa.com/ranking/archive?categoryCode=000&date=202412&ranking_gf=A',
    'https://www.musinsa.com/products/5077795',
    'https://www.musinsa.com/products/3256194',
    'https://www.musinsa.com/category/003004?gf=F',
    'https://www.musinsa.com/category/003006?gf=F',
    'https://www.musinsa.com/category/003007?gf=F'
]

user_agents = [
    # Windows Chrome
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",

    # Windows Edge
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67",

    # Windows Firefox
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) "
    "Gecko/20100101 Firefox/115.0",

    # macOS Chrome
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4_1) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",

    # macOS Safari
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4_1) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/16.5 Safari/605.1.15",

    # macOS Firefox
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13.4; rv:115.0) "
    "Gecko/20100101 Firefox/115.0",

    # iPhone Safari
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 "
    "Mobile/15E148 Safari/604.1",

    # Android Chrome
    "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36"
]


musinsa_category_clothing_titles = ['상의', '아우터', '바지', '원피스/스커트', '스포츠/레저', '키즈']
musinsa_category_clothing_code = [
    {'title': '상의', 'code': '001'},
    {'title': '아우터', 'code': '002'},
    {'title': '바지', 'code': '003'},
    {'title': '원피스/스커트', 'code': '100'},
    {'title': '스포츠/레저', 'code': '017'},
    {'title': '키즈', 'code': '106'},
]
ably_category_clothing_titles = ['아우터', '상의', '팬츠', '원피스/세트', '스커트', '트레이닝']


def get(url, headers=None, params=None, timeout=None):
    if headers is None:
        headers = {}

    if params is None:
        params = {}

    if timeout is None:
        return requests.get(url, headers=headers, params=params)
    else:
        return requests.get(url, headers=headers, params=params, timeout=timeout)

# ===============================
# 무신사 카테고리 조회
# ===============================
def _get_musinsa_categories(gender='A'):
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,zh;q=0.6',
        'origin': 'https://www.musinsa.com',
        'priority': 'u=1, i',
        'referer': 'https://www.musinsa.com/',
        'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
    }

    params = {
        'tabId': 'category',
        'gf': gender,
    }

    response = requests.get('https://api.musinsa.com/api2/dp/v3/menu', params=params, headers=headers)
    json_data = response.json()
    return json_data.get('data', {}).get('list', [])

# ===============================
# 에이블리 카테고리 조회
# ===============================
def get_ably_categories(parent):
    try:
        parent.signals.progress_signal.emit("A-bly 카테고리 페이지 접속 중...", LogType.INFO)
        parent.parent.driver.get("https://m.a-bly.com/overview")
        time.sleep(3)

        html = parent.parent.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        script_tag = soup.select_one('#__NEXT_DATA__')
        if not script_tag:
            msg = "[get_ably_categories] __NEXT_DATA__ 스크립트 태그를 찾을 수 없음. 3초 후 재시도"
            logger.warning(msg)
            parent.signals.error_signal.emit(msg)

            time.sleep(3)

            parent.signals.progress_signal.emit("A-bly 카테고리 페이지 접속 중...", LogType.INFO)

            parent.parent.driver.get("https://m.a-bly.com/overview")
            time.sleep(3)

            html = parent.parent.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            script_tag = soup.select_one('#__NEXT_DATA__')
            if not script_tag:
                msg = "[get_ably_categories] __NEXT_DATA__ 스크립트 태그를 찾을 수 없음."
                logger.warning(msg)
                parent.signals.error_signal.emit(msg)
                return []
            else:
                msg = "[get_ably_categories] 카테고리 조회 시작"
                parent.signals.progress_signal.emit(msg, LogType.INFO)
                logger.info(msg)

        try:
            json_data = json.loads(script_tag.text)
        except json.JSONDecodeError as e:
            msg = f"[get_ably_categories] JSON 디코딩 실패: {e}"
            logger.error(msg)
            parent.signals.error_signal.emit(msg)
            return []

        queries = json_data.get('props', {}).get('serverQueryClient', {}).get('queries', [])
        if not queries:
            msg = "[get_ably_categories] queries 데이터 없음"
            logger.warning(msg)
            parent.signals.warning_signal.emit(msg)
            return []

        item_list = queries[0].get('state', {}).get('data', {}).get('itemList', [])
        if not item_list:
            msg = "[get_ably_categories] itemList 데이터 없음"
            logger.warning(msg)
            parent.signals.warning_signal.emit(msg)
            return []

        items = [item.get('item') for item in item_list if 'item' in item]
        result = extract_menu(
            items,
            'name',
            'deeplink',
            'subCategoryList',
            type='ably',
            replace_prev='ably://screens/?',
            replace_after='https://m.a-bly.com/screens?screen_name=SUB_'
        )

        msg = f"[get_ably_categories] 카테고리 수집 완료, 총 {len(result)}개"
        logger.info(msg)
        parent.signals.progress_signal.emit(msg, LogType.SUCCESS)
        return result

    except Exception as e:
        msg = f"[get_ably_categories] 예외 발생: {e}"
        logger.error(msg)
        parent.signals.error_signal.emit(msg)
        return []

# ===============================
# 무신사 아이템 목록 조회
# ===============================
def get_musinsa_item_list(category_title, gender, category_code, page=1):
    headers = {
        'accept': 'application/json',
        'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,zh;q=0.6',
        'origin': 'https://www.musinsa.com',
        'priority': 'u=1, i',
        'referer': random.choice(referers),
        'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': random.choice(user_agents),
    }

    params = {
        'gf': gender,
        'category': category_code,
        'size': 60,
        'caller': 'CATEGORY',
        'page': page,
    }

    if category_title == '신상':
        params['sortCode'] = 'NEW'
    if category_title == '무배당발':
        params['isPlusDelivery'] = 'true'

    return requests.get('https://api.musinsa.com/api2/dp/v1/plp/goods', params=params, headers=headers)

# ===============================
# 무신사 세일 아이템 목록 조회
# ===============================
def get_musinsa_sale_item_list(gender, category_code):
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,zh;q=0.6',
        'origin': 'https://www.musinsa.com',
        'priority': 'u=1, i',
        'referer': random.choice(referers),
        'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': random.choice(user_agents),
    }

    params = {
        'storeCode': 'musinsa',
        'gf': gender,
        'contentsId': category_code,
        'categoryCode': category_code,
        'interestStore': '',
        'bucket': '',
    }

    return requests.get('https://api.musinsa.com/api2/hm/web/v2/pans/sale/sections/37', params=params, headers=headers)

# ===============================
# 무신사 상세 아이템 조회
# ===============================
def get_musinsa_item_detail(link):
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,zh;q=0.6',
        'cache-control': 'max-age=0',
        'priority': 'u=0, i',
        'referer': random.choice(referers),
        'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': random.choice(user_agents),
    }
    return requests.get(link, headers=headers)


# ===============================
# 무신사 카테고리 파싱
# ===============================
def get_musinsa_categories():
    logger.info("무신사 카테고리 조회 시작")

    category_list = _get_musinsa_categories()
    logger.info(f"전체 카테고리 수: {len(category_list)}")

    menu = extract_menu(category_list, 'title', 'code', 'list')
    logger.info(f"메뉴 추출 완료: {len(menu)}개 항목")

    male_categories = update_items_musinsa(menu, 'M')
    logger.info(f"남성 카테고리 처리 완료: {len(male_categories)}개 항목")

    female_categories = update_items_musinsa(menu, 'F')
    logger.info(f"여성 카테고리 처리 완료: {len(female_categories)}개 항목")

    male_sale_categories = get_musinsa_sale_categories('M')
    logger.info(f"남성 세일 카테고리 처리 완료: {len(male_sale_categories)}개 항목")

    female_sale_categories = get_musinsa_sale_categories('F')
    logger.info(f"여성 세일 카테고리 처리 완료: {len(female_sale_categories)}개 항목")

    logger.info("무신사 카테고리 조회 완료")

    return {
        'male_categories': male_categories,
        'female_categories': female_categories,
        'male_sale_categories': male_sale_categories,
        'female_sale_categories': female_sale_categories,
    }

def extract_menu(category_list, title_name, link_url_name, sub_name, type='musinsa', replace_prev='', replace_after=''):
    logger.info(f"extract_menu 시작 - type: {type}, 총 카테고리 수: {len(category_list)}")
    result = []
    category_clothing_titles = musinsa_category_clothing_titles if type == 'musinsa' else ably_category_clothing_titles

    for category in category_list:
        if category[title_name] in category_clothing_titles:
            cat_dict = {
                'title': category[title_name],
                'category_title': category[title_name],
                'link_url': category[link_url_name].replace(replace_prev, replace_after),
                'is_sale': False,
                'type': type,
                'sub': []
            }
            sub_count = 0
            for sub_group in category.get(sub_name, []):
                if type == 'ably':
                    sub = sub_group.get('item', {})
                    cat_dict['sub'].append({
                        'title': sub[title_name],
                        'category_title': category[title_name],
                        'link_url': sub[link_url_name].replace(replace_prev, replace_after),
                        'type': type,
                    })
                    sub_count += 1
                else:
                    for sub in sub_group.get(sub_name, []):
                        cat_dict['sub'].append({
                            'title': sub[title_name],
                            'category_title': sub[title_name],
                            'link_url': sub[link_url_name].replace(replace_prev, replace_after),
                            'is_sale': False,
                            'type': type,
                        })
                        sub_count += 1
            result.append(cat_dict)
            logger.info(f"카테고리 처리 완료: {category[title_name]} / 서브 항목 수: {sub_count}")

    logger.info(f"extract_menu 완료 - 최종 결과 수: {len(result)}")
    return result

def update_items_musinsa(items, gender):
    updated_list = []
    for item in items:
        if gender == 'M' and item.get("title") == "원피스/스커트":
            logger.info(f"남성용 처리 제외 항목: {item.get('title')}")
            continue
        new_item = copy.deepcopy(item)
        # title 수정
        if "title" in new_item:
            new_item["title"] = f"({'남자' if gender == 'M' else '여자'}) {new_item['title']}"
            logger.info(f"타이틀 업데이트: {new_item['title']}")
        new_item["gender"] = gender
        # sub 재귀 처리
        if "sub" in new_item:
            new_item["sub"] = update_items_musinsa(new_item["sub"], gender)
        updated_list.append(new_item)
    logger.info(f"update_items_musinsa 완료 - gender: {gender}, 총 항목 수: {len(updated_list)}")
    return updated_list

def get_musinsa_sale_categories(gender):
    result = []
    for data in musinsa_category_clothing_code:
        if gender == 'M' and data.get("title") == "원피스/스커트":
            logger.info(f"남성용 세일 카테고리 제외: {data.get('title')}")
            continue
        code = data.get('code')
        title = data.get('title')
        cat_dict = {
            'title': f"(세일 {'남자' if gender == 'M' else '여자'}) {title}",
            'link_url': code,
            'is_sale': True,
            'type': 'musinsa',
            'gender': gender,
            'sub': [],
        }
        logger.info(f"세일 카테고리 추가: {cat_dict['title']}")
        result.append(cat_dict)
    logger.info(f"get_musinsa_sale_categories 완료 - gender: {gender}, 총 항목 수: {len(result)}")
    return result


# ===============================
# 무신사 API 파싱
# ===============================
def musinsa_item_detail_parser(parent, response, title, is_sale, category_code, item_index, result):
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        soup = BeautifulSoup(response.text, 'html.parser')

        # __NEXT_DATA__ 스크립트 추출
        script_tag = soup.select_one("#__NEXT_DATA__")
        if not script_tag:
            msg = f"[{parent.task_id}] __NEXT_DATA__ 스크립트 없음"
            parent.signals.error_signal.emit(msg)
            parent.signals.add_progress_bar_signal.emit()
            return

        # JSON 파싱
        try:
            json_data = json.loads(script_tag.text)
        except json.JSONDecodeError as e:
            msg = f"[{parent.task_id}] JSON 파싱 실패: {e}"
            parent.signals.error_signal.emit(msg)
            parent.signals.add_progress_bar_signal.emit()
            return

        # 데이터 존재 여부 확인
        data = json_data.get('props', {}).get('pageProps', {}).get('meta', {}).get('data', {})
        if not data:
            msg = f"[{parent.task_id}] 데이터 없음"
            parent.signals.progress_signal.emit(msg, LogType.WARNING)
            parent.signals.add_progress_bar_signal.emit()
            return

        # 안전하게 데이터 추출
        try:
            brand_name = data.get('brandInfo', {}).get('brandName', '')
        except Exception as e:
            brand_name = ''
            msg = f"[{parent.task_id}] brand_name 추출 실패: {e}"
            parent.signals.progress_signal.emit(msg, LogType.WARNING)
        try:
            _카테고리_객체 = data.get('category', {})
            _카테고리_리스트 = [
                _카테고리_객체.get('categoryDepth1Name'),
                _카테고리_객체.get('categoryDepth2Name'),
                _카테고리_객체.get('categoryDepth3Name'),
                _카테고리_객체.get('categoryDepth4Name')
            ]
            _카테고리_리스트 = [c for c in _카테고리_리스트 if c]
            category = " > ".join(_카테고리_리스트) + (f" ({brand_name})" if brand_name else "")
        except Exception as e:
            category = ''
            msg = f"[{parent.task_id}] category 추출 실패: {e}"
            parent.signals.progress_signal.emit(msg, LogType.WARNING)

        try:
            product_name = data.get('goodsNm', '')
        except Exception as e:
            product_name = ''
            msg = f"[{parent.task_id}] product_name 추출 실패: {e}"
            parent.signals.progress_signal.emit(msg, LogType.WARNING)

        try:
            _가격_객체 = data.get('goodsPrice', {})
            regular_price = comma(_가격_객체.get('normalPrice', ''))
            sale_price = comma(_가격_객체.get('salePrice', ''))
            discount_rate = comma(_가격_객체.get('discountRate', ''))
        except Exception as e:
            regular_price = sale_price = discount_rate = ''
            msg = f"[{parent.task_id}] 가격 정보 추출 실패 (할인 없음): {e}"
            parent.signals.progress_signal.emit(msg, LogType.WARNING)

        try:
            contents = data.get('mdOpinion', '')
        except Exception as e:
            contents = ''
            msg = f"[{parent.task_id}] contents 추출 실패: {e}"
            parent.signals.progress_signal.emit(msg, LogType.WARNING)

        try:
            rating = comma(data.get('goodsReview', {}).get('satisfactionScore', ''))
            review_count = comma(data.get('goodsReview', {}).get('totalCount', ''))
        except Exception as e:
            rating = review_count = ''
            msg = f"[{parent.task_id}] 평점 또는 리뷰 수 정보 추출 실패: {e}"
            parent.signals.progress_signal.emit(msg, LogType.WARNING)

        msg = f"[{parent.task_id}] 데이터 추출 완료: {product_name}"
        parent.signals.progress_signal.emit(msg, LogType.SUCCESS)

    except Exception as e:
        msg = f"[{parent.task_id}] 파싱 중 예외 발생: {e}"
        parent.signals.error_signal.emit(msg)
        parent.signals.add_progress_bar_signal.emit()
        return


    _썸네일주소_리스트 = data.get('goodsImages', [])

    thumbnails = []
    # --- 썸네일 이미지 추출 ---
    for i, _썸네일주소 in enumerate(_썸네일주소_리스트):
        if parent.is_stopped:
            parent.signals.stop_signal.emit(parent.task_id)
            logger.info(f"[{parent.task_id}] 작업 중지됨")
            return

        try:
            thumbnail_url = _썸네일주소.get('imageUrl', '')
            if thumbnail_url == '':
                continue

            _img_file_path = f'{product_name}_썸네일_{i}.png'
            safe_file_name = sanitize_filename(_img_file_path)
            folder_path = os.path.join('images', today, '무신사', '썸네일', sanitize_filename(product_name))

            thumbnails.append({
                'thumbnail_url': thumbnail_url,
                'thumbnail_path': folder_path,
                'thumbnail_filename': safe_file_name,
            })

        except Exception as e:
            msg = f"[{parent.task_id}] 상세페이지 이미지 처리 예외 [{i}]: {e}"
            parent.signals.error_signal.emit(msg)

    # --- 상세페이지 이미지 추출 ---
    detail_images = []

    try:
        goods_contents = data.get('goodsContents', '')
        matches = re.finditer(r'(https?:)?//[^\s"\']+', goods_contents)
        _상세페이지_이미지_주소_목록 = [m.group(0) for m in matches]

        if not _상세페이지_이미지_주소_목록:
            msg = f"[{parent.task_id}] {product_name} 상세페이지 이미지 없음 {goods_contents}"
            parent.signals.progress_signal.emit(msg, LogType.WARNING)


        for i, 상세페이지_이미지_주소 in enumerate(_상세페이지_이미지_주소_목록):
            if parent.is_stopped:
                parent.signals.stop_signal.emit(parent.task_id)
                logger.info(f"[{parent.task_id}] 작업 중지됨")
                return

            try:
                if 상세페이지_이미지_주소.endswith('mp4'):
                    continue
                상세페이지_이미지_주소 = 상세페이지_이미지_주소.replace('&amp;', '')
                _img_file_path = f'{product_name}_상세페이지_{i}.png'
                safe_file_name = sanitize_filename(_img_file_path)
                folder_path = os.path.join('images', today, '무신사', '상세페이지', sanitize_filename(product_name))

                detail_images.append({
                    'detail_image_url': 상세페이지_이미지_주소,
                    'detail_image_path': folder_path,
                    'detail_image_filename': safe_file_name,
                })

            except Exception as e:
                msg = f"[{parent.task_id}] 상세페이지 이미지 처리 예외 [{i}]: {e}"
                parent.signals.error_signal.emit(msg)

    except Exception as e:
        msg = f"[{parent.task_id}] 상세페이지 이미지 루프 처리 예외: {e}"
        parent.signals.error_signal.emit(msg)

    parsed_data = {
        'title': title,
        'brand_name': brand_name,
        'category': category,
        'product_name': product_name,
        'regular_price': regular_price,
        'sale_price': sale_price,
        'discount_rate': discount_rate,
        'contents': contents,
        'rating': rating,
        'review_count': review_count,
        'thumbnails': thumbnails,
        'detail_images': detail_images,
        'item_index': item_index,
        'index': parent.index,
        'is_sale': is_sale,
        'category_code': category_code,
    }

    result.update(parsed_data)

    parent.signals.progress_signal.emit(
        f'[{parent.task_id}] {product_name} 상세 정보 수집 완료 [{parent.index + 1}/{parent.total_index}]',
        LogType.SUCCESS
    )
    parent.signals.data_send_signal.emit(result)

# ===============================
# 에이블리 API 파싱
# ===============================
def ably_detail_parser(parent, current_item_index, shadow_dom_retry=0, product_name_retry=0):
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        page_source = parent.driver.page_source
        main_soup = BeautifulSoup(page_source, 'html.parser')

        # Shadow DOM 파싱
        try:
            panel = (WebDriverWait(parent.driver, 5)
                     .until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                            '.sc-b760d6-3.hVLeas.react-tabs__tab-panel.react-tabs__tab-panel--selected > div:nth-of-type(1) > div:nth-of-type(1) > div:nth-of-type(1) > div:nth-of-type(1)'))))
            shadow_html = parent.driver.execute_script('return arguments[0].shadowRoot.innerHTML', panel)
            shadow_soup = BeautifulSoup(shadow_html, 'html.parser')
        except Exception as e:
            if shadow_dom_retry < 3:
                msg = f"[{parent.task_id}] Shadow DOM 파싱 실패 2초 후 재시도 ({shadow_dom_retry + 1}/3): {e}"
                parent.signals.error_signal.emit(msg)
                time.sleep(2)
                return ably_detail_parser(parent, current_item_index, shadow_dom_retry=shadow_dom_retry + 1,
                                          product_name_retry=product_name_retry)
            else:
                msg = f"[{parent.task_id}] Shadow DOM 파싱 최종 실패"
                parent.signals.error_signal.emit(msg)
                parent.signals.add_progress_bar_signal.emit()
                return None

        # 상품명 추출
        product_name_el = main_soup.select_one('.typography.typography__body1.color__gray70')
        product_name = product_name_el.text.strip() if product_name_el else 'UNKNOWN_PRODUCT'

        if product_name == 'UNKNOWN_PRODUCT':
            if product_name_retry < 3:
                msg = f"[{parent.task_id}] 상품명 추출 실패 3초 후 재시도 ({product_name_retry + 1}/3)"
                parent.signals.progress_signal.emit(msg, LogType.WARNING)
                time.sleep(3)
                return ably_detail_parser(parent, current_item_index, shadow_dom_retry=shadow_dom_retry,
                                          product_name_retry=product_name_retry + 1)
            else:
                msg = f"[{parent.task_id}] 상품명 추출 최종 실패"
                parent.signals.error_signal.emit(msg)
                parent.signals.add_progress_bar_signal.emit()
                return None

        thumbnail_urls = main_soup.select('.sc-474405d1-0.cNVikc .swiper-slide img')

        thumbnails = []
        for i, img_tag in enumerate(thumbnail_urls):
            if parent.is_stopped:
                parent.signals.stop_signal.emit(parent.task_id)
                logger.info(f"[{parent.task_id}] 작업 중지됨")
                return None

            try:
                thumbnail_url = img_tag.attrs['src']
                img_file_path = f'{product_name}_썸네일_{i}.png'
                folder_path = os.path.join('images', today, '에이블리', '썸네일', sanitize_filename(product_name))
                safe_file_name = sanitize_filename(img_file_path)

                thumbnails.append({
                    'thumbnail_url': thumbnail_url,
                    'thumbnail_path': folder_path,
                    'thumbnail_filename': safe_file_name,
                })
            except Exception as e:
                msg = f"[{parent.task_id}] 썸네일 처리 예외 [{i}]: {e}"
                parent.signals.error_signal.emit(msg)

        # 가격/리뷰/브랜드 정보 안전하게 추출
        try:
            rating = main_soup.select_one('.typography.typography__body5.color__pink30').text.strip()
        except Exception as e:
            rating = ''
            msg = f"[{parent.task_id}] 좋아요 정보 추출 실패: {e}"
            parent.signals.progress_signal.emit(msg, LogType.WARNING)

        brand_name = ''
        try:
            brand_name = main_soup.select_one('.sc-bc435950-1.getNAU .typography.typography__subtitle2.color__gray70').text.strip()
        except Exception as e:
            try:
                brand_name = main_soup.select_one('.sc-d4a21d0e-0.hDesJg .typography.typography__subtitle2.color__gray70').text.strip()
            except Exception as e:
                msg = f"[{parent.task_id}] 브랜드명 정보 추출 실패: {e}"
                parent.signals.progress_signal.emit(msg, LogType.WARNING)

        try:
            regular_price_el = main_soup.select('.typography.typography__body2.color__content_disabled.sc-461fef97-1.bYJTeK')
            if regular_price_el:
                regular_price = regular_price_el[0].text.strip().replace('원', '')
                sale_price = main_soup.select_one('.typography.typography__h4.color__gray70').text.strip().replace('원', '')
                discount_rate = main_soup.select_one('.typography.typography__h4.color__pink30').text.strip().replace('%', '')
            else:
                regular_price = main_soup.select_one('.typography.typography__h4.color__gray70').text.strip().replace('원', '')
                sale_price = ''
                discount_rate = ''
        except Exception as e:
            regular_price = sale_price = discount_rate = ''
            msg = f"[{parent.task_id}] 가격 정보 추출 실패 (할인 없음): {e}"
            parent.signals.progress_signal.emit(msg, LogType.WARNING)

        try:
            review_count_el = main_soup.select('.sc-be780511-3.hcLzye')
            review_count = review_count_el[1].text.replace('리뷰', '').strip() if len(review_count_el) > 1 else ''
        except Exception as e:
            review_count = ''
            msg = f"[{parent.task_id}] 리뷰 수 정보 추출 실패: {e}"
            parent.signals.progress_signal.emit(msg, LogType.WARNING)

        # 상세 내용 및 상세 이미지
        contents = []
        try:
            content_elements = shadow_soup.select('.detail-inner:not(.goods-notice-container) > p:not(img)')
            for el in content_elements:
                text = el.get_text(strip=True)
                if text:
                    contents.append(text)
        except Exception as e:
            msg = f"[{parent.task_id}] 상세 내용 파싱 실패: {e}"
            parent.signals.progress_signal.emit(msg, LogType.WARNING)

        contents_text = '\n'.join(contents)

        상세페이지_이미지_목록 = []
        try:
            _상세페이지_이미지_주소_목록 = shadow_soup.select('.detail-inner:not(.goods-notice-container) > p > img')
            if not _상세페이지_이미지_주소_목록:
                _상세페이지_이미지_주소_목록 = shadow_soup.select('.detail-inner:not(.goods-notice-container) > img')

            for i, img_tag in enumerate(_상세페이지_이미지_주소_목록):
                if parent.is_stopped:
                    parent.signals.stop_signal.emit(parent.task_id)
                    return None

                img_url = img_tag.attrs['src']
                img_file_path = f'{product_name}_상세페이지_{i}.png'

                folder_path = os.path.join('images', today, '에이블리', '상세페이지', sanitize_filename(product_name))
                safe_file_name = sanitize_filename(img_file_path)

                상세페이지_이미지_목록.append({
                    'detail_image_url': img_url,
                    'detail_image_path': folder_path,
                    'detail_image_filename': safe_file_name,
                })
        except Exception as e:
            msg = f"[{parent.task_id}] 상세페이지 이미지 처리 예외: {e}"
            parent.signals.error_signal.emit(msg)

        # 데이터 전송
        parent.signals.data_send_signal.emit({
            'title': getattr(parent, 'title', ''),
            'brand_name': brand_name,
            'category': getattr(parent, 'category_title', ''),
            'product_name': product_name,
            'regular_price': regular_price,
            'sale_price': sale_price,
            'discount_rate': discount_rate,
            'contents': contents_text,
            'rating': rating,
            'review_count': review_count,
            'thumbnails': thumbnails,
            'detail_images': 상세페이지_이미지_목록,
            'detail_link': parent.driver.current_url,
            'item_index': parent.total_item_count,
            'index': current_item_index,
        })

        current_progress = parent.current_item_count * parent.count_input + (current_item_index + 1)
        total_progress = parent.total_item_count * parent.count_input
        msg = f"[{parent.task_id}] {product_name} 상세 정보 수집 완료 ({current_progress}/{total_progress})"
        parent.signals.progress_signal.emit(msg, LogType.SUCCESS)
        return None

    except Exception as e:
        msg = f"[{parent.task_id}] 전체 파싱 예외 발생: {e}"
        parent.signals.error_signal.emit(msg)
        parent.signals.add_progress_bar_signal.emit()
        return None


def get_musinsa_image(uri):
    headers = {
        'sec-ch-ua-platform': '"macOS"',
        'Referer': 'https://www.musinsa.com/',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        'sec-ch-ua-mobile': '?0',
    }

    if uri.startswith('/images'):
        url = f'https://image.msscdn.net/thumbnails{uri}'
    elif uri.startswith('//'):
        url = f'https:{uri}'
    else:
        url = uri

    return get(
        url=url,
        headers=headers,
        timeout=2,
    )

def get_ably_image(uri):
    headers = {
        'sec-ch-ua-platform': '"macOS"',
        'Referer': 'https://m.a-bly.com/',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
        'sec-ch-ua-mobile': '?0',
    }

    url = uri
    if uri.startswith('//'):
        url = f'https:{uri}'

    return get(
        url=url,
        headers=headers,
        timeout=2,
    )




# ===============================
# 유틸리티
# ===============================
def comma(text):
    if isinstance(text, (int, float)):
        return format(text, ',')
    else:
        return ''

def sanitize_filename(filename):
    # 파일 이름에서 허용되지 않는 문자 제거 또는 대체
    return re.sub(r'[\\/*?:"<>|]', '_', filename)

def make_unique_filename(filepath):
    if not os.path.exists(filepath):
        return filepath

    base, ext = os.path.splitext(filepath)
    i = 1
    while True:
        new_filepath = f"{base}({i}){ext}"
        if not os.path.exists(new_filepath):
            return new_filepath
        i += 1
