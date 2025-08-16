from PySide6.QtCore import QRunnable, Slot
from api import get_musinsa_item_list
from worker import WorkerSignals
from log_type import LogType
from logger import logger

class MusinsaDetailLinkLoader(QRunnable):
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
        logger.info(f"[{self.task_id}] 작업 중지 요청됨")

    @Slot()
    def run(self):
        if self.is_stopped:
            self.signals.stop_signal.emit(self.task_id)
            logger.info(f"[{self.task_id}] 작업 중지됨")
            return

        self.signals.progress_signal.emit(f"[{self.task_id}] {self.title} 카테고리 상세 페이지 링크 수집 시작", LogType.INFO)
        logger.info(f"[{self.task_id}] API 호출 시작: category={self.category_title}, page={self.page}")

        try:
            response = get_musinsa_item_list(self.category_title, self.gender, self.category_code, self.page)
            json_list = response.json().get('data', {}).get('list', [])
            logger.info(f"[{self.task_id}] API 호출 성공, {len(json_list)} 항목 수집")
        except Exception as e:
            msg = f"[{self.task_id}] API 요청 오류: {str(e)}"
            logger.error(msg)
            self.signals.error_signal.emit(msg)
            self.signals.finished_signal.emit(self.task_id)
            return

        for json_item in json_list:
            if self.is_stopped:
                self.signals.stop_signal.emit(self.task_id)
                logger.info(f"[{self.task_id}] 작업 중지됨")
                return

            try:
                detail_link = json_item.get('goodsLinkUrl', '')
                product_name = json_item.get('goodsName', '')
                item = {
                    'title': self.title,
                    'item_index': self.item_index,
                    'index': self.page,
                    'page': self.page,
                    'detail_link': detail_link,
                    'gender': self.gender,
                    'is_sale': self.is_sale,
                    'product_name': product_name,
                    'category_title': self.category_title,
                    'category_code': self.category_code,
                }
                self.signals.data_send_signal.emit(item)
            except Exception as e:
                msg = f"[{self.task_id}] 데이터 처리 중 오류 발생: {e}"
                logger.error(msg)
                self.signals.error_signal.emit(msg)

        self.signals.progress_signal.emit(f"[{self.task_id}] {self.title} 카테고리 상세 페이지 링크 수집 완료", LogType.SUCCESS)
        logger.info(f"[{self.task_id}] 작업 완료")
        self.signals.finished_signal.emit(self.task_id)
