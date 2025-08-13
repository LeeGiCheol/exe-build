import time

from PySide6.QtCore import QObject, Signal, Slot, QRunnable
from selenium import webdriver
from selenium.webdriver.common.by import By

from api import get_franchise_url, franchise_detail_link_parser, remove_label, get_general_construction_tasks_header, \
    general_construction_request, general_construction_detail_request


# 공통 시그널 클래스
class WorkerSignals(QObject):
    log = Signal(str)
    progress = Signal(str)
    result = Signal(list)
    stop = Signal(str)
    total_count_send = Signal(int)
    data_send = Signal(dict)
    fail_send = Signal(str)
    finished = Signal(str)

### TASK
class FranchiseTotalCountTask(QRunnable):
    def __init__(self, chrome_options, task_id):
        super().__init__()
        self.chrome_options = chrome_options
        self.task_id = task_id
        self.is_stopped = False
        self.signals = WorkerSignals()

    def stop(self):
        self.is_stopped = True

    @Slot()
    def run(self):
        self.signals.log.emit(f"[{self.task_id}] 프랜차이즈 전체 페이지 수 조회 시작")
        driver = webdriver.Chrome(options=self.chrome_options)
        driver.get(get_franchise_url(1))
        time.sleep(1)

        total_count = int(driver.find_element(By.CSS_SELECTOR, 'tbody > tr > td').text)
        self.signals.log.emit(f"[{self.task_id}] 프랜차이즈 전체 페이지 수 추출 완료")
        if self.is_stopped:
            self.signals.stop.emit(self.task_id)
            return
        self.signals.data_send.emit({'total_count': total_count})

class FranchiseExcelSaveTask(QRunnable):
    def __init__(self, chrome_options, task_id, page):
        super().__init__()
        self.chrome_options = chrome_options
        self.task_id = task_id
        self.page = page
        self.is_stopped = False
        self.signals = WorkerSignals()

    def stop(self):
        self.is_stopped = True

    @Slot()
    def run(self):
        result = []
        if self.is_stopped:
            self.signals.result.emit(result)
            self.signals.stop.emit(self.task_id)
            self.signals.finished.emit(self.task_id)
            return []

        self.signals.log.emit(f"[{self.task_id}] 프랜차이즈 {self.page}페이지 조회 시작")
        driver = webdriver.Chrome(options=self.chrome_options)
        driver.get(get_franchise_url(self.page))
        time.sleep(1)

        가맹본부일반현황_테이블_1_trs = driver.find_elements(By.CSS_SELECTOR, "tbody > tr")

        if len(가맹본부일반현황_테이블_1_trs) == 0:
            self.signals.finished.emit(self.task_id)
            return []

        for i in range(len(가맹본부일반현황_테이블_1_trs)):
            if self.is_stopped:
                self.signals.result.emit(result)
                self.signals.stop.emit(self.task_id)
                self.signals.finished.emit(self.task_id)
                return result

            가맹본부일반현황_테이블_1_trs = driver.find_elements(By.CSS_SELECTOR, "tbody > tr")
            tr = 가맹본부일반현황_테이블_1_trs[i]
            tds = tr.find_elements(By.CSS_SELECTOR, "td")
            리스트_영업표지 = tds[2].text
            상세페이지_링크 = franchise_detail_link_parser(tds[1].find_element(By.CSS_SELECTOR, 'a').get_attribute('onclick'))
            driver.get(상세페이지_링크)

            time.sleep(3)

            tables = driver.find_elements(By.CSS_SELECTOR, "table")
            if len(tables) == 0:
                self.signals.log.emit(f"[{self.task_id}] 프랜차이즈 {self.page}페이지 `{리스트_영업표지}` 조회 오류 재조회 첫번째 시작")
                driver.close()
                driver = webdriver.Chrome(options=self.chrome_options)
                driver.get(get_franchise_url(self.page))
                time.sleep(2)

                가맹본부일반현황_테이블_1_trs = driver.find_elements(By.CSS_SELECTOR, "tbody > tr")
                tr = 가맹본부일반현황_테이블_1_trs[i]
                tds = tr.find_elements(By.CSS_SELECTOR, "td")
                리스트_영업표지 = tds[2].text
                상세페이지_링크 = franchise_detail_link_parser(
                    tds[1].find_element(By.CSS_SELECTOR, 'a').get_attribute('onclick'))
                driver.get(상세페이지_링크)

                time.sleep(3)

                tables = driver.find_elements(By.CSS_SELECTOR, "table")
                if len(tables) > 0:
                    self.signals.log.emit(f"[{self.task_id}] 프랜차이즈 {self.page}페이지 `{리스트_영업표지}` 재조회 성공")
                else:
                    self.signals.log.emit(f"[{self.task_id}] 프랜차이즈 {self.page}페이지 `{리스트_영업표지}` 조회 오류 재조회 두번째 시작")
                    driver.close()
                    driver = webdriver.Chrome(options=self.chrome_options)
                    driver.get(get_franchise_url(self.page))
                    time.sleep(3)

                    가맹본부일반현황_테이블_1_trs = driver.find_elements(By.CSS_SELECTOR, "tbody > tr")
                    tr = 가맹본부일반현황_테이블_1_trs[i]
                    tds = tr.find_elements(By.CSS_SELECTOR, "td")
                    상세페이지_링크 = franchise_detail_link_parser(
                        tds[1].find_element(By.CSS_SELECTOR, 'a').get_attribute('onclick'))
                    driver.get(상세페이지_링크)

                    time.sleep(4)

                    tables = driver.find_elements(By.CSS_SELECTOR, "table")
                    if len(tables) > 0:
                        self.signals.log.emit(f"[{self.task_id}] 프랜차이즈 {self.page}페이지 `{리스트_영업표지}` 재조회 성공")
                    else:
                        self.signals.log.emit(f"[{self.task_id}] 프랜차이즈 {self.page}페이지 `{리스트_영업표지}` 조회 오류 재조회 세번째 시작")
                        driver.close()
                        driver = webdriver.Chrome(options=self.chrome_options)
                        driver.get(get_franchise_url(self.page))
                        time.sleep(3)

                        가맹본부일반현황_테이블_1_trs = driver.find_elements(By.CSS_SELECTOR, "tbody > tr")
                        tr = 가맹본부일반현황_테이블_1_trs[i]
                        tds = tr.find_elements(By.CSS_SELECTOR, "td")
                        상세페이지_링크 = franchise_detail_link_parser(
                            tds[1].find_element(By.CSS_SELECTOR, 'a').get_attribute('onclick'))
                        driver.get(상세페이지_링크)

                        time.sleep(5)

                        tables = driver.find_elements(By.CSS_SELECTOR, "table")
                        if len(tables) > 0:
                            self.signals.log.emit(f"[{self.task_id}] 프랜차이즈 {self.page}페이지 `{리스트_영업표지}` 재조회 성공")
                        else:
                            self.signals.progress.emit(f"[{self.task_id}] 프랜차이즈 {self.page}페이지 `{리스트_영업표지}` 조회 실패 포기")
                            driver.close()
                            driver = webdriver.Chrome(options=self.chrome_options)
                            driver.get(get_franchise_url(self.page))
                            time.sleep(3)

                            가맹본부일반현황_테이블_1_trs = driver.find_elements(By.CSS_SELECTOR, "tbody > tr")
                            time.sleep(1)

                            self.signals.fail_send.emit(리스트_영업표지)
                            continue

            가맹본부일반현황_테이블_1 = tables[0]
            가맹본부일반현황_테이블_1_trs = 가맹본부일반현황_테이블_1.find_elements(By.CSS_SELECTOR, "tbody > tr")
            # 홀수 인덱스가 data
            tds0 = 가맹본부일반현황_테이블_1_trs[0].find_elements(By.CSS_SELECTOR, "td")
            상호 = remove_label(driver, tds0[0])
            영업표지 = remove_label(driver, tds0[1])
            대표자 = remove_label(driver, tds0[2])
            업종 = remove_label(driver, tds0[3])
            tds2 = 가맹본부일반현황_테이블_1_trs[2].find_elements(By.CSS_SELECTOR, "td")
            법인설립등기일 = tds2[0].text
            사업자등록일 = tds2[1].text
            대표번호_replace = tds2[2].text.replace(' ', '')
            대표번호 = 대표번호_replace[1:] if 대표번호_replace.startswith('-') else 대표번호_replace
            대표팩스_번호_replace = tds2[3].text.replace(' ', '')
            대표팩스_번호 = 대표팩스_번호_replace[1:] if 대표팩스_번호_replace.startswith('-') else 대표팩스_번호_replace
            tds4 = 가맹본부일반현황_테이블_1_trs[4].find_elements(By.CSS_SELECTOR, "td")
            등록번호 = tds4[0].text
            최초등록일 = tds4[1].text
            최종등록일 = tds4[2].text

            가맹본부일반현황_테이블_2 = tables[1]
            가맹본부일반현황_테이블_2_trs = 가맹본부일반현황_테이블_2.find_elements(By.CSS_SELECTOR, "tbody > tr")
            주소 = 가맹본부일반현황_테이블_2_trs[0].find_element(By.CSS_SELECTOR, 'td').text
            가맹본부일반현황_테이블_2_trs1_tds = 가맹본부일반현황_테이블_2_trs[1].find_elements(By.CSS_SELECTOR, 'td')
            사업자유형 = 가맹본부일반현황_테이블_2_trs1_tds[0].text
            법인등록번호 = 가맹본부일반현황_테이블_2_trs1_tds[1].text
            사업자등록번호 = 가맹본부일반현황_테이블_2_trs1_tds[2].text

            가맹본부재무상황_테이블 = tables[2]
            가맹본부재무상황_테이블_trs = 가맹본부재무상황_테이블.find_elements(By.CSS_SELECTOR, "tbody > tr")
            가맹본부재무상황 = ''

            가맹본부재무상황_labels = ['연도', '자산', '부채', '자본', '매출액', '영업이익', '당기순이익']

            for tr in 가맹본부재무상황_테이블_trs:
                tds = tr.find_elements(By.CSS_SELECTOR, 'td')
                row_info = [f"{label}: {td.text.strip()}" for label, td in zip(가맹본부재무상황_labels, tds)]
                가맹본부재무상황 += ', '.join(row_info) + '\n'

            가맹사업_임직원수_테이블 = tables[3]
            가맹사업_임직원수_테이블_trs = 가맹사업_임직원수_테이블.find_elements(By.CSS_SELECTOR, 'tbody > tr')

            가맹사업_임직원수_labels = ['연도', '임원수', '직원수']
            가맹사업_임직원수 = ''
            for tr in 가맹사업_임직원수_테이블_trs:
                tds = tr.find_elements(By.CSS_SELECTOR, 'td')
                row_info = [f"{label}: {td.text.strip()}" for label, td in zip(가맹사업_임직원수_labels, tds)]
                가맹사업_임직원수 += ', '.join(row_info) + '\n'

            가맹본부_브랜드_및_가맹사업_계열사_수_테이블 = tables[4]
            가맹본부_브랜드_및_가맹사업_계열사_수_테이블_tds = 가맹본부_브랜드_및_가맹사업_계열사_수_테이블.find_element(By.CSS_SELECTOR,
                                                                                   'tbody > tr').find_elements(
                By.CSS_SELECTOR, 'td')

            브랜드_수 = ''
            가맹사업_계열사_수 = ''
            if len(가맹본부_브랜드_및_가맹사업_계열사_수_테이블_tds) > 0:
                브랜드_수 = 가맹본부_브랜드_및_가맹사업_계열사_수_테이블_tds[0].text
                가맹사업_계열사_수 = 가맹본부_브랜드_및_가맹사업_계열사_수_테이블_tds[1].text

            가맹사업_개시일_테이블 = tables[5]
            가맹사업_개시일 = 가맹사업_개시일_테이블.find_element(By.CSS_SELECTOR, 'tbody > tr').find_element(By.CSS_SELECTOR, 'td').text

            가맹점_및_직영점_현황_테이블 = tables[6]
            가맹점_및_직영점_현황_테이블_tr = 가맹점_및_직영점_현황_테이블.find_element(By.CSS_SELECTOR, 'tbody > tr')
            가맹점_및_직영점_현황_연도_ths = 가맹점_및_직영점_현황_테이블.find_elements(By.CSS_SELECTOR,
                                                                 'thead > tr:nth-of-type(1) > th.listOfCntShow')

            가맹점_및_직영점_현황_테이블_tds = 가맹점_및_직영점_현황_테이블_tr.find_elements(By.CSS_SELECTOR, 'td')

            가맹점_및_직영점_현황 = ''
            for index in range(len(가맹점_및_직영점_현황_연도_ths)):
                start_idx = index * 3 + 1
                전체 = 가맹점_및_직영점_현황_테이블_tds[start_idx].text
                가맹점수 = 가맹점_및_직영점_현황_테이블_tds[start_idx + 1].text
                직영점수 = 가맹점_및_직영점_현황_테이블_tds[start_idx + 2].text

                가맹점_및_직영점_현황 = 가맹점_및_직영점_현황 + '연도 : ' + 가맹점_및_직영점_현황_연도_ths[
                    index].text + ', 전체 : ' + 전체 + ', 가맹점수 : ' + 가맹점수 + ', 직영점수 : ' + 직영점수 + '\n'

            가맹점_변동_현황_테이블 = tables[7]
            가맹점_변동_현황_테이블_trs = 가맹점_변동_현황_테이블.find_elements(By.CSS_SELECTOR, "tbody > tr")
            가맹점_변동_현황 = ''

            가맹점_변동_현황_labels = ['연도', '신규개점', '계약종료', '계약해지', '명의변경']

            for tr in 가맹점_변동_현황_테이블_trs:
                tds = tr.find_elements(By.CSS_SELECTOR, 'td')
                row_info = [f"{label}: {td.text.strip()}" for label, td in zip(가맹점_변동_현황_labels, tds)]
                가맹점_변동_현황 += ', '.join(row_info) + '\n'

            광고_판촉비_내역_테이블 = tables[10]
            광고_판촉비_내역_테이블_trs = 광고_판촉비_내역_테이블.find_elements(By.CSS_SELECTOR, "tbody > tr")
            광고_판촉비_내역 = ''

            광고_판촉비_내역_labels = ['연도', '광고비', '판촉비']

            for tr in 광고_판촉비_내역_테이블_trs:
                tds = tr.find_elements(By.CSS_SELECTOR, 'td')
                row_info = [f"{label}: {td.text.strip()}" for label, td in zip(광고_판촉비_내역_labels, tds)]
                광고_판촉비_내역 += ', '.join(row_info) + '\n'

            가맹계약_기간_테이블 = tables[15]
            가맹계약_기간_테이블_tds = 가맹계약_기간_테이블.find_elements(By.CSS_SELECTOR, 'tbody > tr:nth-of-type(3) > td')

            가맹계약_기간 = ''

            if len(가맹계약_기간_테이블_tds) > 0:
                가맹계약_기간 = 가맹계약_기간 + '최초 계약기간 : ' + 가맹계약_기간_테이블_tds[0].text + '년, 연장 계약기간 : ' + 가맹계약_기간_테이블_tds[
                    1].text + '년\n'

            result.append(
                [상호, 영업표지, 대표자, 업종, 법인설립등기일, 사업자등록일, 대표번호, 대표팩스_번호, 등록번호, 최초등록일, 최종등록일, 주소, 사업자유형, 법인등록번호, 사업자등록번호,
                 가맹본부재무상황, 가맹사업_임직원수, 브랜드_수, 가맹사업_계열사_수, 가맹사업_개시일, 가맹점_및_직영점_현황, 가맹점_변동_현황, 광고_판촉비_내역, 가맹계약_기간])

            self.signals.progress.emit(f"[{self.task_id}] 프랜차이즈 `{영업표지}` 추출 완료")

            driver.back()
            time.sleep(1)

            driver.refresh()
            time.sleep(1)

        driver.close()
        self.signals.result.emit(result)
        self.signals.finished.emit(self.task_id)
        return None

class GeneralConstructionTotalCountTask(QRunnable):
    def __init__(self, task_id, chrome_options):
        super().__init__()
        self.task_id = task_id
        self.chrome_options = chrome_options
        self.is_stopped = False
        self.signals = WorkerSignals()

    def stop(self):
        self.is_stopped = True

    @Slot()
    def run(self):
        self.signals.log.emit(f"[{self.task_id}] 종합건설 전체 페이지 수 조회 시작")
        driver = webdriver.Chrome(options=self.chrome_options)
        header = get_general_construction_tasks_header(driver)
        jsession_id = header[0]
        csrf_token = header[1]

        total_count = int(general_construction_request(csrf_token, jsession_id, 1).json()['totCnt'])
        self.signals.log.emit(f"[{self.task_id}] 종합건설 전체 페이지 수 추출 완료")
        if self.is_stopped:
            self.signals.stop.emit(self.task_id)
            return
        self.signals.data_send.emit({'total_count': total_count, 'csrf_token': csrf_token, 'jsession_id': jsession_id})

class GeneralConstructionExcelSaveTask(QRunnable):
    def __init__(self, task_id, csrf_token, jsession_id, page):
        super().__init__()
        self.task_id = task_id
        self.csrf_token = csrf_token
        self.jsession_id = jsession_id
        self.page = page
        self.is_stopped = False
        self.signals = WorkerSignals()

    def stop(self):
        self.is_stopped = True

    @Slot()
    def run(self):
        result = []
        if self.is_stopped:
            self.signals.result.emit(result)
            self.signals.stop.emit(self.task_id)
            self.signals.finished.emit(self.task_id)
            return []

        self.signals.log.emit(f"[{self.task_id}] 종합건설 {self.page}페이지 조회 시작")
        response_json = general_construction_request(self.csrf_token, self.jsession_id, self.page).json()
        biz_list = response_json['bizList']

        if len(biz_list) == 0:
            self.signals.finished.emit(self.task_id)
            return []

        for i in range(len(biz_list)):
            if self.is_stopped:
                self.signals.result.emit(result)
                self.signals.stop.emit(self.task_id)
                self.signals.finished.emit(self.task_id)

                return []

            biz = biz_list[i]
            hwno = biz.get('hwno', '')
            등록번호 = biz.get('upjongno', '').strip()
            시공능력평가액 = biz.get('handoamt', '')
            if not 시공능력평가액 == '':
                시공능력평가액 = format(시공능력평가액, ',').strip()
            상호 = biz.get('sangho', '').strip()
            대표자 = biz.get('nm', '').strip()
            전화번호 = biz.get('cotelno', '').strip()
            주소 = f"({biz.get('bszipno', '').strip()}) {biz.get('bsaddr', '')}"
            홈페이지 = ''
            try:
                홈페이지 = general_construction_detail_request(self.csrf_token, self.jsession_id, hwno).json().get('info', []).get('url', '-')
            except:
                self.signals.log.emit(f"[{self.task_id}] 종합건설 {self.page}페이지 `{상호}` 조회 오류 재조회 첫번째 시작")
                time.sleep(2)
                try:
                    홈페이지 = general_construction_detail_request(self.csrf_token, self.jsession_id, hwno).json().get(
                        'info', []).get('url', '-')
                    self.signals.log.emit(f"[{self.task_id}] 종합건설 {self.page}페이지 `{상호}` 재조회 성공")
                except:
                    self.signals.log.emit(f"[{self.task_id}] 종합건설 {self.page}페이지 `{상호}` 조회 오류 재조회 두번째 시작")
                    time.sleep(2)
                    try:
                        홈페이지 = general_construction_detail_request(self.csrf_token, self.jsession_id, hwno).json().get('info', []).get('url', '-')
                        self.signals.log.emit(f"[{self.task_id}] 종합건설 {self.page}페이지 `{상호}` 재조회 성공")
                    except:
                        self.signals.log.emit(f"[{self.task_id}] 종합건설 {self.page}페이지 `{상호}` 조회 오류 재조회 세번째 시작")
                        time.sleep(2)
                        try:
                            홈페이지 = general_construction_detail_request(self.csrf_token, self.jsession_id,
                                                                       hwno).json().get(
                                'info', []).get('url', '-')
                            self.signals.log.emit(f"[{self.task_id}] 종합건설 {self.page}페이지 `{상호}` 재조회 성공")
                        except:
                            self.signals.progress.emit(f"[{self.task_id}] 종합건설 {self.page}페이지 `{상호}` 조회 실패 포기")
                            self.signals.fail_send.emit(상호)
                            continue

            result.append([등록번호, 시공능력평가액, 상호, 대표자, 전화번호, 주소, 홈페이지])
            self.signals.progress.emit(f"[{self.task_id}] 종합건설 `{상호}` 추출 완료")
        self.signals.result.emit(result)
        self.signals.finished.emit(self.task_id)