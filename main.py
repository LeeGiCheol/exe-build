import os
from datetime import datetime

import pandas as pd
import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import QThreadPool

from worker import FranchiseExcelSaveTask, FranchiseTotalCountTask, GeneralConstructionTotalCountTask, GeneralConstructionExcelSaveTask
from selenium.webdriver.chrome.options import Options
from main_ui import Ui_Form

class MainWindow(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.total_count_tasks = []
        self.tasks = []
        self.setupUi(self)
        self.debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'

        self.franchise_thread_pool = QThreadPool()
        self.franchise_thread_pool.setMaxThreadCount(3)
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(3)
        self.total_count_thread_pool = QThreadPool()
        self.total_count_thread_pool.setMaxThreadCount(1)

        self.progress_bar_value = 0
        self.task_total = 0
        self.task_finished = 0
        self.result = []
        self.total_count = 0
        self.count = 0
        self.fail_result = []

        self.setup_dark_mode()
        self.setWindowTitle("프랜차이즈 종합건설 데이터 수집기")
        self.setup_icon()

        self.franchise_excel_download_button.clicked.connect(self.start_franchise_tasks)
        self.general_construction_excel_button.clicked.connect(self.start_general_construction_tasks)
        self.stop_button.clicked.connect(self.stop)
        self.exit_button.clicked.connect(self.exit)

    def setup_dark_mode(self):
        dark_stylesheet = """
        QWidget {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QTextBrowser {
            background-color: #2b2b2b;
            color: #ffffff;
            border: 1px solid #555555;
        }
        QPushButton {
            background-color: #4a4a4a;
            color: #ffffff;
            border: 1px solid #555555;
            padding: 8px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #5a5a5a;
        }
        QPushButton:pressed {
            background-color: #3a3a3a;
        }
        QPushButton:disabled {
            background-color: #999191;
        }
        QProgressBar {
            background-color: #3b3b3b;
            color: #ffffff;
            border: 1px solid #555555;
            border-radius: 4px;
        }
        QProgressBar::chunk {
            background-color: #4CAF50;
            border-radius: 4px;
        }
        """
        self.setStyleSheet(dark_stylesheet)

    def setup_icon(self):
        # 아이콘 파일 경로들 (여러 확장자 지원)
        icon_paths = [
            "icon.ico",  # 윈도우
            "icon.icns",  # 맥
            "icon.png",  # 일반 이미지
            "app_icon.ico",
            "app_icon.icns"
        ]

        for icon_path in icon_paths:
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
                app.setWindowIcon(QIcon(icon_path))
                break
        else:
            print("아이콘 파일을 찾을 수 없습니다. 기본 아이콘을 사용합니다.")

    # 중지 버튼 클릭 이벤트
    def stop(self):
        self.stop_button.setEnabled(False)
        for task in self.tasks:
            task.stop()

        for task in self.total_count_tasks:
            task.stop()


    # 중지 버튼 클릭 후 콜백 이벤트
    def stop_callback(self, task_id):
        self.contents.append(f"[{task_id}] 실행 중지 완료")
        self.stop_button.setEnabled(True)
        self.franchise_excel_download_button.setEnabled(True)
        self.general_construction_excel_button.setEnabled(True)
        self.count = 0
        self.total_count = 0
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(1)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar_value = 0
        self.tasks = []
        self.total_count_tasks = []

    # 종료 버튼 클릭 이벤트
    def exit(self):
        sys.exit()

    # 프랜차이즈 엑셀 다운로드 클릭 이벤트 (전체 건수 추출)
    def start_franchise_tasks(self):
        self.count = 0
        self.total_count = 0
        self.fail_result = []
        self.contents.clear()
        self.contents.append("프랜차이즈 작업 시작 중...")
        self.stop_button.setEnabled(True)
        self.franchise_excel_download_button.setEnabled(False)
        self.general_construction_excel_button.setEnabled(False)

        self.total_count_tasks = []
        task_id = f"franchise-total-count"
        task = FranchiseTotalCountTask(chrome_options, task_id)
        self.total_count_tasks.append(task)

        # 총 작업 수 계산
        self.task_total = len(self.total_count_tasks)
        self.task_finished = 0

        # debug 모드는 main 스레드에서 직접 실행
        if self.debug_mode:
            for task in self.total_count_tasks:
                task.signals.log.connect(self.log)
                task.signals.stop.connect(self.stop_callback)
                task.signals.data_send.connect(self.data_send_franchise_callback)
                task.run()
        else:
            for task in self.total_count_tasks:
                task.signals.log.connect(self.log)
                task.signals.stop.connect(self.stop_callback)
                task.signals.data_send.connect(self.data_send_franchise_callback)
                self.franchise_thread_pool.start(task)

    # 프랜차이즈 엑셀 다운로드 클릭 후 콜백 이벤트 (데이터 추출)
    def data_send_franchise_callback(self, data):
        self.stop_button.setEnabled(True)
        total_count = data['total_count']

        total_count_format_str = format(int(total_count), ',')
        self.contents.append(f'프랜차이즈 총 {total_count_format_str}건 조회 시작')
        self.total_count = total_count
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(total_count)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar_value = 0

        per_page = 300
        loop = (total_count // per_page) + (1 if total_count % per_page != 0 else 0)

        self.tasks = []
        for page in range(1, (loop + 1)):
            task_id = f"franchise-{page}"
            task = FranchiseExcelSaveTask(chrome_options, task_id, page)
            self.tasks.append(task)

        # 총 작업 수 계산
        self.task_total = len(self.tasks)
        self.task_finished = 0

        # debug 모드는 main 스레드에서 직접 실행
        if self.debug_mode:
            for task in self.tasks:
                task.signals.log.connect(self.log)
                task.signals.progress.connect(self.update_status)
                task.signals.result.connect(self.append_results)
                task.signals.stop.connect(self.stop_callback)
                task.signals.fail_send.connect(self.fail_send_callback)
                task.signals.finished.connect(self.handle_task_finished)
                task.run()
        else:
            for task in self.tasks:
                task.signals.log.connect(self.log)
                task.signals.progress.connect(self.update_status)
                task.signals.result.connect(self.append_results)
                task.signals.stop.connect(self.stop_callback)
                task.signals.fail_send.connect(self.fail_send_callback)
                task.signals.finished.connect(self.handle_task_finished)
                self.franchise_thread_pool.start(task)


    # 종합건설 엑셀 다운로드 클릭 이벤트 (전체 건수 추출)
    def start_general_construction_tasks(self):
        self.count = 0
        self.total_count = 0
        self.fail_result = []
        self.contents.clear()
        self.contents.append("종합건설 작업 시작 중...")
        self.stop_button.setEnabled(True)
        self.franchise_excel_download_button.setEnabled(False)
        self.general_construction_excel_button.setEnabled(False)

        self.total_count_tasks = []

        task_id = f"general_construction-total-count"
        task = GeneralConstructionTotalCountTask(task_id, chrome_options)
        self.total_count_tasks.append(task)
        # 총 작업 수 계산
        self.task_total = len(self.total_count_tasks)
        self.task_finished = 0

        # debug 모드는 main 스레드에서 직접 실행
        if self.debug_mode:
            for task in self.total_count_tasks:
                task.signals.log.connect(self.log)
                task.signals.stop.connect(self.stop_callback)
                task.signals.data_send.connect(self.data_send_construction_callback)
                task.run()
        else:
            for task in self.total_count_tasks:
                task.signals.log.connect(self.log)
                task.signals.stop.connect(self.stop_callback)
                task.signals.data_send.connect(self.data_send_construction_callback)
                self.total_count_thread_pool.start(task)

    # 종합건설 엑셀 다운로드 클릭 후 콜백 이벤트 (데이터 추출)
    def data_send_construction_callback(self, data):
        self.stop_button.setEnabled(True)
        total_count = data['total_count']
        csrf_token = data['csrf_token']
        jsession_id = data['jsession_id']

        total_count_format_str = format(int(total_count), ',')
        self.contents.append(f'종합건설 총 {total_count_format_str}건 조회 시작')
        self.total_count = total_count
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(total_count)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar_value = 0

        per_page = 50
        loop = (total_count // per_page) + (1 if total_count % per_page != 0 else 0)

        self.tasks = []
        for page in range(1, (loop + 1)):
            task_id = f"general_construction-{page}"
            task = GeneralConstructionExcelSaveTask(task_id, csrf_token, jsession_id, page)
            self.tasks.append(task)

        # 총 작업 수 계산
        self.task_total = len(self.tasks)
        self.task_finished = 0

        # debug 모드는 main 스레드에서 직접 실행
        if self.debug_mode:
            for task in self.tasks:
                task.signals.log.connect(self.log)
                task.signals.progress.connect(self.update_status)
                task.signals.result.connect(self.append_results)
                task.signals.stop.connect(self.stop_callback)
                task.signals.fail_send.connect(self.fail_send_callback)
                task.signals.finished.connect(self.handle_task_finished)
                task.run()
        else:
            for task in self.tasks:
                task.signals.log.connect(self.log)
                task.signals.progress.connect(self.update_status)
                task.signals.result.connect(self.append_results)
                task.signals.stop.connect(self.stop_callback)
                task.signals.fail_send.connect(self.fail_send_callback)
                task.signals.finished.connect(self.handle_task_finished)
                self.thread_pool.start(task)

    # Log 콜백
    def log(self, msg):
        self.contents.append(msg)

    # status 업데이트
    # 프로그래스바 증가
    # 현재 진행 건수 로깅
    def update_status(self, msg):
        self.count = self.count + 1
        self.contents.append(f'{msg} ({self.count}/{self.total_count})')
        self.progress_bar_value += 1
        self.progress_bar.setValue(self.progress_bar_value)

    # 성공 건 취합
    def append_results(self, result):
        self.result.extend(result)

    # 실패 건 취합
    def fail_send_callback(self, name):
        self.fail_result.append(name)

    # 스레드 종료 콜백
    def handle_task_finished(self, task_id):
        self.task_finished += 1
        page = task_id.split('-')[1]
        self.contents.append(f"[{task_id}] 완료됨 페이지 ({page}/{self.task_total})")
        if self.task_finished == self.task_total:
            if task_id.startswith('franchise'):
                self.franchise_all_tasks_finished()
            else:
                self.construction_all_tasks_finished()

    # 프랜차이즈 전체 종료 후 엑셀 다운로드
    def franchise_all_tasks_finished(self):
        self.tasks = []
        self.contents.append("프랜차이즈 엑셀 추출 작업 완료")
        if len(self.fail_result) > 0:
            self.contents.append("#################")
            self.contents.append("실패 목록")
            for fail in self.fail_result:
                self.contents.append(fail)
            self.contents.append("#################")
        QApplication.processEvents()

        self.franchise_excel_download_button.setEnabled(True)
        self.general_construction_excel_button.setEnabled(True)

        df = pd.DataFrame(self.result, columns=['상호', '영업표지', '대표자', '업종', '법인설립등기일', '사업자등록일', '대표번호', '대표팩스 번호', '등록번호', '최초등록일', '최종등록일', '주소', '사업자유형', '법인등록번호', '사업자등록번호',
                     '가맹본부재무상황', '가맹사업 임직원수', '브랜드 수', '가맹사업 계열사 수', '가맹사업 개시일', '가맹점 및 직영점 현황', '가맹점 변동 현황', '광고 판촉비 내역', '가맹계약 기간'])
        output_dir = "excel"
        os.makedirs(output_dir, exist_ok=True)
        today_str = datetime.today().strftime('%Y%m%d%H%M%S')
        df.to_excel(os.path.join(output_dir, f"프랜차이즈_{today_str}.xlsx"), index=False)

    # 종합건설 전체 종료 후 엑셀 다운로드
    def construction_all_tasks_finished(self):
        self.tasks = []
        self.contents.append("종합건설 엑셀 추출 작업 완료")
        if len(self.fail_result) > 0:
            self.contents.append("#################")
            self.contents.append("실패 목록")
            for fail in self.fail_result:
                self.contents.append(fail)
            self.contents.append("#################")

        self.franchise_excel_download_button.setEnabled(True)
        self.general_construction_excel_button.setEnabled(True)

        df = pd.DataFrame(self.result, columns=['등록번호', '시공능력평가액', '상호', '대표자', '전화번호', '주소', '홈페이지'])
        output_dir = "excel"
        os.makedirs(output_dir, exist_ok=True)
        today_str = datetime.today().strftime('%Y%m%d%H%M%S')
        df.to_excel(os.path.join(output_dir, f"종합건설_{today_str}.xlsx"), index=False)


chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
chrome_options.add_argument('headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('--disable-images')  # 이미지 로딩 비활성화


app = QApplication()

window = MainWindow()
window.show()

sys.exit(app.exec())