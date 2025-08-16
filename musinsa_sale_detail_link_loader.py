import time
from PySide6.QtCore import QRunnable, Slot
from worker import WorkerSignals
from api import get_musinsa_sale_item_list
from log_type import LogType
from logger import logger

class MusinsaSaleDetailLinkLoader(QRunnable):
    def __init__(self, task_id, title, gender, category_title, category_code, is_sale, item_index, page, parent=None):
        super().__init__()
        self.task_id = task_id
        self.title = title
        self.gender = gender
        self.category_title = category_title
        self.category_code = category_code
        self.is_sale = is_sale
        self.item_index = item_index
        self.page = page
        self.is_stopped = False
        self.signals = WorkerSignals(parent=parent)

    def stop(self):
        self.is_stopped = True
        logger.info(f"[{self.task_id}] 세일 링크 수집 중지 요청됨")

    @Slot()
    def run(self):
        self.signals.progress_signal.emit(
            f'[{self.task_id}] 세일 > {self.title} 카테고리 상세페이지 링크 수집 시작', 
            LogType.INFO
        )

        try:
            # API 호출 시 재시도
            for attempt in range(1, 4):
                response = get_musinsa_sale_item_list(self.gender, self.category_code)
                if response.status_code == 200:
                    break
                else:
                    msg = f"[{self.task_id}] API 요청 {attempt}회 실패, 5초 후 재시도"
                    self.signals.error_signal.emit(msg)
                    logger.warning(msg)
                    time.sleep(5)
            else:
                msg = f"[{self.task_id}] API 요청 3회 실패, 포기"
                self.signals.error_signal.emit(msg)
                logger.error(msg)
                self.signals.finished_signal.emit(self.task_id)
                return

            try:
                json_list = response.json().get('data', {}).get('modules', [])
            except Exception as e:
                msg = f"[{self.task_id}] API 응답 파싱 중 에러: {e}"
                self.signals.error_signal.emit(msg)
                logger.exception(msg)
                self.signals.finished_signal.emit(self.task_id)
                return

            items = []
            for json in json_list:
                if self.is_stopped:
                    self.signals.stop_signal.emit(self.task_id)
                    logger.info(f"[{self.task_id}] 작업 중지됨")
                    return

                if json.get('id', '').startswith('MULTICOLUMN'):
                    items.extend(json.get('items', []))

            for item in items:
                if self.is_stopped:
                    self.signals.stop_signal.emit(self.task_id)
                    logger.info(f"[{self.task_id}] 작업 중지됨")
                    return

                info = item.get('info', {})
                product_name = info.get('productName', '')
                detail_link = item.get('onClick', {}).get('url', '')

                self.signals.data_send_signal.emit({
                    'title': self.title,
                    'detail_link': detail_link,
                    'gender': self.gender,
                    'is_sale': self.is_sale,
                    'product_name': product_name,
                    'category_title': self.category_title,
                    'category_code': self.category_code,
                    'item_index': self.item_index,
                    'page': self.page,
                })

            self.signals.progress_signal.emit(
                f"[{self.task_id}] 세일 > {self.title} 카테고리 상세 페이지 링크 수집 완료", 
                LogType.SUCCESS
            )

        except Exception as e:
            msg = f"[{self.task_id}] 세일 링크 수집 중 에러 발생: {e}"
            self.signals.error_signal.emit(msg)
            logger.exception(msg)
        finally:
            self.signals.finished_signal.emit(self.task_id)
