import time
from PySide6.QtCore import QRunnable, Slot
from api import get_musinsa_item_detail, musinsa_item_detail_parser
from worker import WorkerSignals
from log_type import LogType
from logger import logger

class MusinsaDetailLoader(QRunnable):
    def __init__(self, task_id, detail, total_index, index, parent=None):
        super().__init__()
        self.task_id = task_id
        self.detail = detail
        self.total_index = total_index
        self.index = index
        self.is_stopped = False
        self.signals = WorkerSignals(parent=parent)

    def stop(self):
        self.is_stopped = True
        logger.info(f"[{self.task_id}] 상세 정보 수집 중지 요청됨")

    @Slot()
    def run(self):
        if self.is_stopped:
            self.signals.stop_signal.emit(self.task_id)
            logger.info(f"[{self.task_id}] 작업 중지됨")
            return

        product_name = self.detail.get('product_name', 'Unknown')
        self.signals.progress_signal.emit(
            f'[{self.task_id}] [{product_name}] 상세 정보 수집 시작 [{self.index + 1}/{self.total_index}]',
            LogType.INFO
        )

        result = self.detail

        try:
            # 최대 3회 재시도
            for attempt in range(1, 4):
                response = get_musinsa_item_detail(self.detail.get('detail_link', ''))
                if response.status_code == 200:
                    break
                else:
                    msg = f'[{self.task_id}] {product_name} 상세 정보 조회 {attempt}회 실패, 5초 후 재시도'
                    self.signals.error_signal.emit(msg)
                    logger.warning(msg)
                    time.sleep(5)
            else:
                msg = f'[{self.task_id}] {product_name} 상세 정보 조회 3회 실패, 포기'
                self.signals.error_signal.emit(msg)
                logger.error(msg)
                self.signals.finished_signal.emit(self.task_id)
                self.signals.add_progress_bar_signal.emit()
                return

            # 안전하게 파싱
            try:
                title = self.detail.get('title', '')
                is_sale = self.detail.get('is_sale', False)
                category_code = self.detail.get('category_code', '')
                item_index = self.detail.get('item_index', 0)

                musinsa_item_detail_parser(
                    parent=self,
                    response=response,
                    title=title,
                    is_sale=is_sale,
                    category_code=category_code,
                    item_index=item_index,
                    result=result,
                )

            except Exception as e:
                msg = f"[{self.task_id}] {product_name} 상세 정보 파싱 중 에러 발생: {e}"
                self.signals.error_signal.emit(msg)

            time.sleep(1)

        except Exception as e:
            msg = f"[{self.task_id}] {product_name} 상세 정보 수집 중 에러 발생: {e}"
            self.signals.error_signal.emit(msg)

        finally:
            self.signals.finished_signal.emit(self.task_id)