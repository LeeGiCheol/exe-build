import time

from PySide6.QtCore import QRunnable, Slot
from selenium.webdriver.common.by import By

from api import ably_detail_parser
from worker import WorkerSignals
from log_type import LogType

class AblyDetailLoader(QRunnable):
    def __init__(
            self,
            driver,
            task_id,
            link_url,
            title,
            category_title,
            total_item_count,
            count_input,
            current_item_count,

            parent=None,
    ):
        super().__init__()
        self.driver = driver
        self.task_id = task_id
        self.link_url = link_url
        self.title = title
        self.category_title = category_title
        # 조회 할 전체 카테고리 수
        self.total_item_count = total_item_count
        # 유저가 입력한 아이템 조회 수
        self.count_input = count_input
        # 조회 할 카테고리 중 현재 카테고리 인덱스 (ably 기준)
        self.current_item_count = current_item_count
        self.parent = parent
        self.is_stopped = False
        self.try_count = 0

        self.signals = WorkerSignals(parent=parent)


    def stop(self):
        self.is_stopped = True

    @Slot()
    def run(self):
        if self.is_stopped:
            self.signals.stop_signal.emit(self.task_id)
            return

        self.driver.get(self.link_url)
        time.sleep(2)

        i = 0
        while i < self.count_input:
            try:
                if self.is_stopped:
                    self.signals.stop_signal.emit(self.task_id)
                    return

                current_global_index = self.current_item_count * self.count_input + (i + 1)
                self.signals.progress_signal.emit(f"[{self.task_id}] {current_global_index}번째 상품 처리 시작", LogType.INFO)
                products = self.driver.find_elements(By.CSS_SELECTOR,
                                                     f'.sc-6302c06c-3.hOCgbb .sc-e28a495a-0.hkTsoc.sc-6302c06c-0.gjyXx')

                if len(products) < (i + 1):
                    last_height = self.driver.execute_script("return document.body.scrollHeight")
                    products = self.scroll(i, last_height)

                if len(products) < (i + 1):
                    self.signals.error_signal.emit(f"[{self.task_id}] {i + 1}번째 상품이 끝까지 스크롤해도 안 보임 (1)")
                    self.driver.get(self.link_url)
                    time.sleep(2)
                    last_height = self.driver.execute_script("return document.body.scrollHeight")
                    products = self.scroll(i, last_height)

                    if len(products) < (i + 1):
                        self.signals.error_signal.emit(f"[{self.task_id}] {i + 1}번째 상품이 끝까지 스크롤해도 안 보임 넘어감 (2)")
                        self.signals.add_progress_bar_signal.emit()
                        continue  # 다음 상품으로 넘어감
                    else:
                        self.signals.error_signal.emit(f"[{self.task_id}] {i + 1}번째 상품이 스크롤 재시도 성공")
                products[i].click()

                time.sleep(2)
                ably_detail_parser(self, i)

                self.driver.back()
                time.sleep(2)
            except Exception as e:
                self.signals.error_signal.emit(f'[{self.task_id}] 상세 정보 수집 중 에러 발생 {e}')
            finally:
                i += 1

        self.signals.finished_signal.emit(self.task_id)

    def scroll(self, count, last_height, max_retry=5):
        retry = 0
        while retry < max_retry:
            # 스크롤 최하단으로 이동
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1.5)

            products = self.driver.find_elements(By.CSS_SELECTOR,
                                                 '.sc-6302c06c-3.hOCgbb .sc-e28a495a-0.hkTsoc.sc-6302c06c-0.gjyXx')

            # 원하는 개수 확보되면 즉시 반환
            if len(products) >= (count + 1):
                return products

            # 새 높이 체크
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                # 혹시 느려서 아직 못 불러온 것일 수 있으니 한 번 더 대기
                time.sleep(1.5)
                new_height2 = self.driver.execute_script("return document.body.scrollHeight")
                if new_height2 == last_height:
                    break  # 진짜 멈춘 경우만 종료

            last_height = new_height
            retry += 1

        # 여기까지 왔다는 건 충분한 상품이 안 로드된 상황
        return []
