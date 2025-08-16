import copy
import math
import os
import subprocess
import sys
import time
import uuid

from collections import defaultdict, Counter
from datetime import datetime
from io import BytesIO
from openpyxl.drawing.image import Image, PILImage

import pandas as pd
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import QApplication, QWidget, QFileDialog, QMessageBox
from PySide6.QtCore import Qt, QTimer
from openpyxl import load_workbook
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from ui.main_ui import Ui_Form
from ui.ui_controller import UiController

from category_loader import CategoryLoader
from musinsa_sale_detail_link_loader import MusinsaSaleDetailLinkLoader
from musinsa_detail_link_loader import MusinsaDetailLinkLoader
from musinsa_detail_loader import MusinsaDetailLoader
from ably_detail_loader import AblyDetailLoader
from worker import LogType

from task_group import TaskGroup
from logger import logger

from api import get_ably_image, get_musinsa_image
from api import make_unique_filename

os.environ["WDM_SSL_VERIFY"] = "0"

os.makedirs('config', exist_ok=True)

CONFIG_FILE = "config/chrome_config.txt"
FIRST_START = False

# DEBUG_MODE = True
DEBUG_MODE = False

def short_uuid10():
    return uuid.uuid4().hex[:10]



class MainWindow(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        UiController.set_window_title(self, "무신사 에이블리 데이터 수집기")
        UiController.setup_dark_mode(self)
        UiController.setup_icon(self, app)

        self.chrome_proc = get_chrome_paths()
        if self.chrome_proc is None:
            global CONFIG_FILE
            UiController.show_confirm_dialog_chrome_path(self, CONFIG_FILE)
            self.chrome_proc = get_chrome_paths()

        # Selenium 연결
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", "localhost:9222")

        self.driver = webdriver.Chrome(options=chrome_options)

        self.uuid = ''
        self.progress_bar_value = 0
        self.is_stop = False

        self.category_task = TaskGroup(code='CATEGORY', name='카테고리')

        self.musinsa_link_task = TaskGroup(code='MUSINSA_LINK', name='무신사 링크')
        self.musinsa_task = TaskGroup(code='MUSINSA', name='무신사')

        self.musinsa_sale_link_task = TaskGroup(code='MUSINSA_SALE_LINK', name='무신사 세일 링크')
        self.musinsa_sale_task = TaskGroup(code='MUSINSA_SALE', name='무신사 세일')

        self.ably_task = TaskGroup(code='ABLY', name='에이블리')


        self.running_task_groups = set()
        self.task_finished_count = 0

        self.count_input.setValidator(QIntValidator(1, 999))
        self.chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self.char_index = 0
        self.label_running.hide()
        self.musinsa_categories = {}
        self.ably_categories = {}
        self.ably_token = ''
        self.detail_link_result = []
        self.sale_detail_link_result = []

        self.musinsa_sale_result = []
        self.musinsa_result = []
        self.ably_result = []

        # DEBUG 모드 여부
        self.debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'

        # UI 이벤트 연결
        self.setup_signals()

        global FIRST_START
        if FIRST_START:
            logger.info("최초 실행 브라우져 정리 Dialog 실행")
            UiController.show_confirm_dialog(self)
            logger.info("최초 실행 브라우져 정리 Dialog 종료")

        # 초기 카테고리 로드
        self.load_categories_async()

    # ===============================
    # 최초 카테고리 API 조회
    # ===============================
    def load_categories_async(self):
        category_task_id = f"category-0"
        self.category_task.add_task(CategoryLoader(category_task_id, self))
        self.category_task.start_tasks(
            debug_mode=DEBUG_MODE,
            start_callback=self.load_categories_start_callback,
            category_finished_callback=self.categories_loaded_callback,
            error_callback=self.error_callback,
        )

    def load_categories_start_callback(self):
        logger.info("카테고리 조회 시작")
        UiController.set_input_enabled(self, False)
        # 타이머 설정
        UiController.set_timer(self, True, '카테고리 조회 중 입니다.')
        logger.info("타이머 동작 시작")

    def categories_loaded_callback(self, musinsa, ably):
        logger.info(f"카테고리 조회 완료")
        logger.info(f"무신사: {musinsa}")
        logger.info(f"에이블리: {ably}")
        self.musinsa_categories = musinsa
        self.ably_categories = ably
        UiController.setup_default_categories(self)

        UiController.set_timer(self, False)
        logger.info("타이머 동작 종료")
        UiController.set_input_enabled(self, True)

    # ===============================
    # UI 이벤트 연결
    # ===============================
    def setup_signals(self):
        # 카테고리 1/2 리스트 클릭/더블클릭
        self.category1_list_widget.itemClicked.connect(lambda item: UiController.category1_click_callback(self, item))
        self.category1_list_widget.itemDoubleClicked.connect(lambda item: UiController.category1_double_click_callback(self, item))
        self.category2_list_widget.itemDoubleClicked.connect(lambda item: UiController.add_to_selected(self, item))
        self.selected_category_list_widget.itemDoubleClicked.connect(lambda item: UiController.remove_selected_item(self, item))

        # 카테고리 선택/해제 버튼
        self.use_button.clicked.connect(lambda: UiController.use_category(self))
        self.disable_button.clicked.connect(lambda: UiController.disable_category(self))

        # 라디오 버튼 이벤트
        self.musinsa_radio_button.clicked.connect(lambda: UiController.setup_categories1(self, 'musinsa'))
        self.musinsa_category_type_male_radio.clicked.connect(lambda: UiController.musinsa_radio_check_click(self))
        self.musinsa_category_type_female_radio.clicked.connect(lambda: UiController.musinsa_radio_check_click(self))
        self.musinsa_category_type_sale_check.clicked.connect(lambda: UiController.musinsa_radio_check_click(self))
        self.ably_radio_button.clicked.connect(lambda: UiController.setup_categories1(self, 'ably'))

        # 버튼
        self.reset_button.clicked.connect(lambda: UiController.reset(self))
        self.stop_button.clicked.connect(lambda: UiController.stop(self))
        self.excel_save_button.clicked.connect(self.start_all_tasks)
        self.exit_button.clicked.connect(lambda: UiController.exit(self))

    # ===============================
    # 작업 실행 로직
    # ===============================
    def start_all_tasks(self):
        self.is_stop = False

        logger.info("데이터 조회 시작")
        self.uuid = short_uuid10()
        logger.info(f"세션 UUID 생성: {self.uuid}")

        count_input = self.count_input.text()
        if not count_input:
            logger.warning("검색 건수 입력 누락")
            self.contents.setText("검색할 건수를 입력해주세요.")
            return

        count_input = int(count_input)
        logger.info(f"검색 건수: {count_input}")

        item_count = self.selected_category_list_widget.count()
        logger.info(f"선택된 카테고리 수: {item_count}")

        if not item_count:
            logger.warning("검색 카테고리 설정 누락")
            self.contents.setText("검색할 카테고리를 설정해주세요.")
            return

        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(item_count * count_input)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar_value = 0

        self.task_finished_count = 0
        self.detail_link_result = []
        self.sale_detail_link_result = []
        self.musinsa_result = []
        self.ably_result = []

        self.musinsa_link_task = TaskGroup(code='MUSINSA_LINK', name='무신사 링크')
        self.musinsa_task = TaskGroup(code='MUSINSA', name='무신사')
        self.musinsa_sale_link_task = TaskGroup(code='MUSINSA_SALE_LINK', name='무신사 세일 링크')
        self.musinsa_sale_task = TaskGroup(code='MUSINSA_SALE', name='무신사 세일')
        self.ably_task = TaskGroup(code='ABLY', name='에이블리')

        self.contents.clear()
        logger.info("카테고리 및 작업 그룹 초기화 완료")

        if item_count > 0:
            self.contents.setText("작업 시작 중...")
            UiController.set_input_enabled(self, enabled=False, exclude=[self.stop_button, self.exit_button])
            UiController.set_timer(self, True)
            logger.info("UI 입력 비활성화 및 타이머 시작")

        ably_current_item_count = 0

        for i in range(item_count):
            item = self.selected_category_list_widget.item(i)
            title = item.text()
            data = item.data(Qt.ItemDataRole.UserRole)
            type = data['type']
            link_url = data['link_url']
            category_title = data['category_title']
            is_sale = data['is_sale']
            gender = data['gender']

            logger.info(f"[{i + 1}/{item_count}] {title} ({type}) 작업 준비")

            if type == 'musinsa':
                self.progress_callback(f'{title} 조회 시작', LogType.INFO)
                QApplication.processEvents()

                if is_sale:
                    task_id = f'musinsa-sale-detail-link-loader-{i + 1}'
                    self.musinsa_sale_link_task.add_task(
                        MusinsaSaleDetailLinkLoader(
                            task_id=task_id,
                            title=title,
                            gender=gender,
                            category_title=category_title,
                            category_code=link_url,
                            is_sale=True,
                            item_index=i,
                            page=0,
                            parent=self,
                        )
                    )
                    logger.info(f"무신사 세일 링크 작업 추가: {task_id}")
                else:
                    per_call = 60
                    api_calls_needed = math.ceil(count_input / per_call)
                    logger.info(f"{title} 무신사 일반 링크 API 호출 수: {api_calls_needed}")

                    for page in range(1, api_calls_needed + 1):
                        task_id = f'musinsa-detail-link-loader-{page}'
                        self.musinsa_link_task.add_task(
                            MusinsaDetailLinkLoader(
                                task_id=task_id,
                                title=title,
                                gender=gender,
                                category_title=category_title,
                                category_code=link_url,
                                is_sale=False,
                                item_index=i,
                                page=page,
                                parent=self,
                            )
                        )
                        logger.info(f"무신사 링크 작업 추가: {task_id}")
            else:  # ably
                task_id = f'ably-detail-loader-{ably_current_item_count + 1}'
                ably_total_item_count = sum(
                    1 for j in range(item_count)
                    if self.selected_category_list_widget.item(j).data(Qt.ItemDataRole.UserRole).get('type') == 'ably'
                )
                self.ably_task.add_task(
                    AblyDetailLoader(
                        driver=self.driver,
                        task_id=task_id,
                        link_url=link_url,
                        title=title,
                        category_title=category_title,
                        total_item_count=ably_total_item_count,
                        count_input=count_input,
                        current_item_count=ably_current_item_count,
                        parent=self,
                    )
                )
                logger.info(f"에이블리 작업 추가: {task_id} ({ably_current_item_count + 1}/{ably_total_item_count})")
                ably_current_item_count += 1



        # 작업 시작 로그
        if len(self.musinsa_sale_link_task.tasks) > 0:
            self.running_task_groups.add(self.musinsa_sale_link_task)
            logger.info(f"무신사 세일 링크 작업 그룹 시작 ({len(self.musinsa_sale_link_task.tasks)}개)")
            self.musinsa_sale_link_task.start_tasks(
                debug_mode=DEBUG_MODE,
                progress_callback=self.progress_callback,
                data_send_callback=self.musinsa_sale_link_data_send_callback,
                stop_callback=self.stop_callback,
                error_callback=self.error_callback,
                finished_callback=self.detail_link_handle_task_finished,
            )

        if len(self.musinsa_link_task.tasks) > 0:
            self.running_task_groups.add(self.musinsa_link_task)
            logger.info(f"무신사 일반 링크 작업 그룹 시작 ({len(self.musinsa_link_task.tasks)}개)")
            self.musinsa_link_task.start_tasks(
                debug_mode=DEBUG_MODE,
                progress_callback=self.progress_callback,
                data_send_callback=self.musinsa_link_data_send_callback,
                stop_callback=self.stop_callback,
                error_callback=self.error_callback,
                finished_callback=self.detail_link_handle_task_finished,
            )

        if len(self.ably_task.tasks) > 0:
            self.running_task_groups.add(self.ably_task)
            logger.info(f"에이블리 작업 그룹 시작 ({len(self.ably_task.tasks)}개)")
            self.ably_task.start_tasks(
                debug_mode=DEBUG_MODE,
                progress_callback=self.progress_callback,
                add_progress_bar_signal=self.add_progress_bar_callback,
                data_send_callback=self.ably_data_send_callback,
                stop_callback=self.stop_callback,
                error_callback=self.error_callback,
                finished_callback=self.detail_handle_task_finished,
            )

        self.progress_callback("모든 작업 그룹 실행 완료", LogType.INFO)

    def progress_callback(self, message, type):
        def update():
            if type == LogType.SUCCESS:
                self.contents.append(f'<span style="color:blue;">{message}</span>')
                logger.info(f"[SUCCESS] {message}")
            elif type == LogType.ERROR:
                self.contents.append(f'<span style="color:red;">{message}</span>')
                logger.error(f"[ERROR] {message}")
            elif type == LogType.WARNING:
                self.contents.append(f'<span style="color:yellow;">{message}</span>')
                logger.warning(f"[WARN] {message}")
            else:
                self.contents.append(f'<span>{message}</span>')
                logger.info(message)

        QTimer.singleShot(0, update)  # 메인 스레드에서 실행
        QApplication.processEvents()

    def musinsa_sale_link_data_send_callback(self, data):
        self.sale_detail_link_result.append(data)
        logger.info(f"무신사 세일 상세 링크 데이터 수신: {data.get('product_name', 'Unknown')}")

    def musinsa_link_data_send_callback(self, data):
        self.detail_link_result.append(data)
        logger.info(f"무신사 상세 링크 데이터 수신: {data.get('product_name', 'Unknown')}")

    def musinsa_data_send_callback(self, data):
        self.musinsa_result.append(data)
        self.progress_bar_value += 1
        self.progress_bar.setValue(self.progress_bar_value)
        logger.info(f"무신사 상세 데이터 처리 완료: {data.get('product_name', 'Unknown')} (진행 {self.progress_bar_value})")

    def ably_data_send_callback(self, data):
        self.ably_result.append(data)
        self.progress_bar_value += 1
        self.progress_bar.setValue(self.progress_bar_value)
        logger.info(f"에이블리 데이터 처리 완료: {data.get('product_name', 'Unknown')} (진행 {self.progress_bar_value})")

    def add_progress_bar_callback(self):
        self.progress_bar_value += 1
        self.progress_bar.setValue(self.progress_bar_value)

    def detail_link_handle_task_finished(self, task_id, task_group):
        """개별 작업 완료 처리"""
        task_group.finished += 1

        # 완료 메시지
        msg = f"✅ [{task_id}] 링크 수집 완료됨 ({task_group.finished}/{task_group.total})"
        self.progress_callback(msg, LogType.SUCCESS)
        logger.info(f"[Task Finished] [{task_id}] ({task_group.finished}/{task_group.total}) in group {task_group.code}")

        # 그룹 완료 체크
        if task_group.finished == task_group.total:
            self.running_task_groups.discard(task_group)
            logger.info(f"[Task Group Finished] [{task_group.name}] ({task_group.code}) 완료")
            if task_group.code == 'MUSINSA_SALE_LINK':
                self.sale_detail_link_all_tasks_finished(task_group)
            elif task_group.code == 'MUSINSA_LINK':
                self.detail_link_all_tasks_finished(task_group)

    def sale_detail_link_all_tasks_finished(self, task_group):
        """모든 작업 완료 시 UI 업데이트"""
        msg = f"{task_group.name} 상세 링크 수집 완료"
        self.progress_callback(msg, LogType.INFO)

        # 정렬 및 그룹화
        sorted_data = sorted(
            self.sale_detail_link_result,
            key=lambda x: (x['item_index'], x['page'])
        )
        grouped = defaultdict(list)
        for item in sorted_data:
            key = (item['category_code'], item['is_sale'], item['category_title'])
            grouped[key].append(item)

        # 각 그룹에서 상위 count개만 추출
        count = int(self.count_input.text())
        filtered_data = []
        for items in grouped.values():
            filtered_data.extend(items[:count])

        self.sale_detail_link_result = filtered_data
        logger.info(f"[Sale Link Tasks Filtered] 총 {len(filtered_data)}개 항목 남음")

        # MusinsaDetailLoader 작업 생성
        for i, detail in enumerate(self.sale_detail_link_result):
            task_id = f'musinsa_sale_detail_data_crawler-{i}'
            self.musinsa_sale_task.add_task(
                MusinsaDetailLoader(
                    task_id=task_id,
                    detail=detail,
                    total_index=len(self.sale_detail_link_result),
                    index=i,
                    parent=self,
                )
            )
            logger.info(f"[MusinsaDetailLoader Added] {task_id} - {detail.get('product_name', 'Unknown')}")

        # 작업 시작
        self.running_task_groups.add(self.musinsa_sale_task)
        self.musinsa_sale_task.start_tasks(
            debug_mode=DEBUG_MODE,
            progress_callback=self.progress_callback,
            add_progress_bar_signal=self.add_progress_bar_callback,
            data_send_callback=self.musinsa_data_send_callback,
            stop_callback=self.stop_callback,
            error_callback=self.error_callback,
            finished_callback=self.detail_handle_task_finished,
        )
        logger.info(f"[Musinsa Sale Tasks Started] 총 {len(self.musinsa_sale_task.tasks)}개 작업 실행")

    def detail_link_all_tasks_finished(self, task_group):
        """모든 작업 완료 시 UI 업데이트"""
        msg = f"{task_group.name} 상세 링크 수집 완료"
        self.progress_callback(msg, LogType.INFO)

        # 정렬 및 그룹화
        sorted_data = sorted(
            self.detail_link_result,
            key=lambda x: (x['item_index'], x['page'])
        )
        grouped = defaultdict(list)
        for item in sorted_data:
            key = (item['category_code'], item['is_sale'], item['category_title'])
            grouped[key].append(item)

        # 각 그룹에서 상위 count개만 추출
        count = int(self.count_input.text())
        filtered_data = []
        for items in grouped.values():
            filtered_data.extend(items[:count])

        self.detail_link_result = filtered_data
        msg2 = f"{task_group.name} 상세 링크 필터 완료, 총 {len(filtered_data)}개 항목"
        self.progress_callback(msg2, LogType.INFO)

        # MusinsaDetailLoader 작업 생성
        for i, detail in enumerate(self.detail_link_result):
            task_id = f'musinsa_detail_data_crawler-{i}'
            self.musinsa_task.add_task(
                MusinsaDetailLoader(
                    task_id=task_id,
                    detail=detail,
                    total_index=len(self.detail_link_result),
                    index=i,
                    parent=self
                )
            )
            logger.info(f"[MusinsaDetailLoader Added] {task_id} - {detail.get('product_name', 'Unknown')}")

        # 작업 시작
        self.running_task_groups.add(self.musinsa_task)
        self.musinsa_task.start_tasks(
            debug_mode=DEBUG_MODE,
            progress_callback=self.progress_callback,
            add_progress_bar_signal=self.add_progress_bar_callback,
            data_send_callback=self.musinsa_data_send_callback,
            stop_callback=self.stop_callback,
            error_callback=self.error_callback,
            finished_callback=self.detail_handle_task_finished,
        )
        logger.info(f"[Musinsa Tasks Started] 총 {len(self.musinsa_task.tasks)}개 작업 실행")

    def detail_handle_task_finished(self, task_id, task_group):
        """개별 작업 완료 처리"""
        task_group.finished += 1

        # UI + 로그
        msg = f"[{task_id}] 상세 데이터 수집 완료됨 ({task_group.total}개 카테고리 중 {task_group.finished}개 완료)"
        self.progress_callback(msg, LogType.SUCCESS)

        # 그룹 완료 시 처리
        if task_group.finished == task_group.total:
            logger.info(f"[Task Group Finished] {task_group.name} ({task_group.code}) 완료")
            if task_group.code.startswith('MUSINSA'):
                self.musinsa_detail_all_tasks_finished(task_group)
            else:
                self.ably_detail_all_tasks_finished(task_group)
            self.running_task_groups.discard(task_group)
            self.check_all_groups_finished('🚀 모든 작업완료')


    def musinsa_detail_all_tasks_finished(self, task_group):
        """모든 작업 완료 시 UI 업데이트"""
        msg_prefix = f"[{task_group.name}]"
        self.progress_callback(f"{msg_prefix} 상세 정보 수집 완료", LogType.SUCCESS)

        sorted_data = sorted(
            copy.deepcopy(self.musinsa_result),
            key=lambda x: (x['item_index'], x['index'])
        )
        count = int(self.count_input.text()) * self.selected_category_list_widget.count()
        filtered_data = sorted_data[:count]

        self.progress_callback(f"{msg_prefix} 정렬 완료", LogType.INFO)

        self.progress_callback(f"{msg_prefix} 엑셀 다운로드 시작", LogType.INFO)

        # 데이터 전처리
        for item in filtered_data:
            if 'is_sale' in item:
                item['is_sale'] = 'Y' if item['is_sale'] else 'N'
            if 'page' in item:
                del item['page']
            if 'gender' in item:
                if item.get('gender') == 'M':
                    item['gender'] = '남성'
                elif item.get('gender') == 'F':
                    item['gender'] = '여성'

        columns_to_export = ['thumbnail_image', 'gender', 'is_sale', 'product_name',
                             'brand_name', 'contents', 'sale_price',
                             'regular_price', 'category', 'rating',
                             'discount_rate', 'review_count', 'detail_link']

        columns_kr = {
            'thumbnail_image': '썸네일',
            'gender': '성별',
            'is_sale': '세일여부',
            'product_name': '상품명',
            'brand_name': '브랜드명',
            'contents': '상세내용',
            'sale_price': '세일가',
            'regular_price': '정상가',
            'category': '카테고리',
            'rating': '평점',
            'discount_rate': '할인률',
            'review_count': '후기건수',
            'detail_link': '상세링크'
        }

        df = pd.DataFrame(filtered_data, columns=columns_to_export)
        df.rename(columns=columns_kr, inplace=True)

        today = datetime.now().strftime('%Y-%m-%d')
        output_dir = os.path.join('excel', today, '무신사')

        os.makedirs(output_dir, exist_ok=True)
        excel_name = self.excel_name.text() or self.uuid

        file_path = os.path.join(output_dir, f"{excel_name}.xlsx")
        df.to_excel(file_path, index=False)

        self.progress_callback(f"{msg_prefix} 엑셀 다운로드 완료", LogType.SUCCESS)


    def ably_detail_all_tasks_finished(self, task_group):
        """모든 작업 완료 시 UI 업데이트"""
        msg_prefix = f"[{task_group.name}]"
        self.progress_callback(f"{msg_prefix} 상세 정보 수집 완료", LogType.SUCCESS)

        sorted_data = sorted(
            self.ably_result,
            key=lambda x: (x['item_index'], x['index'])
        )
        count = int(self.count_input.text()) * self.selected_category_list_widget.count()
        filtered_data = sorted_data[:count]
        self.ably_result = filtered_data

        self.progress_callback(f"{msg_prefix} 정렬 완료", LogType.INFO)
        self.progress_callback(f"{msg_prefix} 엑셀 다운로드 시작", LogType.INFO)

        columns_to_export = ['thumbnail_image', 'product_name',
                             'brand_name', 'contents', 'sale_price',
                             'regular_price', 'category', 'rating',
                             'discount_rate', 'review_count', 'detail_link']

        columns_kr = {
            'thumbnail_image': '썸네일',
            'product_name': '상품명',
            'brand_name': '브랜드명',
            'contents': '상세내용',
            'sale_price': '세일가',
            'regular_price': '정상가',
            'category': '카테고리',
            'rating': '좋아요 수',
            'discount_rate': '할인률',
            'review_count': '후기건수',
            'detail_link': '상세링크'
        }

        df = pd.DataFrame(self.ably_result, columns=columns_to_export)
        df.rename(columns=columns_kr, inplace=True)

        today = datetime.now().strftime('%Y-%m-%d')
        output_dir = os.path.join('excel', today, '에이블리')
        os.makedirs(output_dir, exist_ok=True)

        excel_name = self.excel_name.text() or self.uuid

        file_path = os.path.join(output_dir, f"{excel_name}.xlsx")
        df.to_excel(file_path, index=False)
        self.progress_callback(f"{msg_prefix} 엑셀 다운로드 완료", LogType.SUCCESS)


    def check_all_groups_finished(self, message):
        if not self.running_task_groups:  # 모두 완료
            self.all_groups_finished(message)

    def all_groups_finished(self, message):
        self.progress_callback(message, LogType.SUCCESS)
        self.progress_callback('UI 업데이트 완료, 입력 활성화 및 타이머 종료', LogType.SUCCESS)

        musinsa_image_message = ''
        ably_image_message = ''
        if len(self.musinsa_result) > 0:
            musinsa_image_message = self.image_download_and_excel_update('무신사', self.musinsa_result, get_musinsa_image)
        if len(self.ably_result) > 0:
            ably_image_message = self.image_download_and_excel_update('에이블리', self.ably_result, get_ably_image)

        self.summarize_results(musinsa_image_message, ably_image_message)
        UiController.set_input_enabled(self, True)
        UiController.set_timer(self, False)
        UiController.stop(self)

    def summarize_results(self, musinsa_image_message, ably_image_message):
        has_musinsa = bool(self.musinsa_result)
        has_ably = bool(self.ably_result)

        if has_musinsa or has_ably:
            self.progress_callback("#" * 30, LogType.SUCCESS)

        if has_musinsa:
            musinsa_counts = defaultdict(int)
            for item in self.musinsa_result:
                key = (item.get("title"), item.get("is_sale"))
                musinsa_counts[key] += 1

            for (title, is_sale), count in musinsa_counts.items():
                self.progress_callback(
                    f"[무신사 결과] 카테고리: {title}, 세일여부: {'Y' if is_sale else 'N'}, 추출 개수: {count}건",
                    LogType.SUCCESS
                )

        if has_ably:
            title_counts = Counter(item.get("title") for item in self.ably_result)
            for title, count in title_counts.items():
                self.progress_callback(
                    f"[에이블리 결과] 카테고리: {title}, 추출 개수: {count}건",
                    LogType.SUCCESS
                )

        if not musinsa_image_message is None and len(musinsa_image_message) > 0:
            self.progress_callback(musinsa_image_message, LogType.SUCCESS)

        if not ably_image_message is None and len(ably_image_message) > 0:
            self.progress_callback(ably_image_message, LogType.SUCCESS)

        if has_musinsa or has_ably:
            self.progress_callback("#" * 30, LogType.SUCCESS)

    def image_download_and_excel_update(self, type, result, image_function):
        today = datetime.now().strftime('%Y-%m-%d')

        output_dir = os.path.join('excel', today, type)

        excel_name = self.excel_name.text() or self.uuid

        file_path = os.path.join(output_dir, f"{excel_name}.xlsx")

        wb = load_workbook(file_path)
        ws = wb.active

        thumbnail_total_count = 0
        thumbnail_download_success_count = 0
        detail_image_total_count = 0
        detail_image_download_success_count = 0

        self.progress_callback(f"[{type}] 이미지 다운로드 시작", LogType.INFO)
        for item_index, item in enumerate(result):
            is_excel_thumbnail = False

            thumbnails = item.get('thumbnails', [])
            thumbnail_total_count += len(thumbnails)
            for thumbnail_index, thumbnail in enumerate(thumbnails):
                if self.is_stop:
                    self.progress_callback(f"[{type}] 이미지 다운로드 중지", LogType.INFO)
                    break

                thumbnail_url = thumbnail['thumbnail_url']
                thumbnail_path = thumbnail['thumbnail_path']
                thumbnail_filename = thumbnail['thumbnail_filename']

                try:
                    thumbnail_response = image_function(thumbnail_url)
                except Exception as e:
                    msg = f"[{type} {len(self.ably_result)}개 아이템 중 {item_index + 1}번째 아이템] {item['product_name']} {thumbnail_index + 1}번 썸네일 다운로드 오류: {e} 이미지 URL: {thumbnail_url}"
                    self.error_callback(msg)
                    continue

                os.makedirs(thumbnail_path, exist_ok=True)
                detail_image_full_file_path = make_unique_filename(os.path.join(thumbnail_path, thumbnail_filename))

                if thumbnail_response.status_code == 200:
                    if not is_excel_thumbnail:
                        item['excel_thumbnail'] = thumbnail_response.content
                        is_excel_thumbnail = True

                    with open(detail_image_full_file_path, 'wb') as f:
                        f.write(thumbnail_response.content)
                    msg = f"[{type} {len(result)}개 아이템 중 {item_index + 1}번째 아이템] {item['product_name']} 썸네일 이미지 저장 완료 [{thumbnail_index + 1}/{len(thumbnails)}]"
                    self.info_callback(msg)
                    thumbnail_download_success_count += 1
                else:
                    msg = f"[{type} {len(result)}개 아이템 중 {item_index + 1}번째 아이템] {item['product_name']} {thumbnail_index + 1}번 썸네일 다운로드 실패 상태 코드: {thumbnail_response.status_code} 이미지 URL: {thumbnail_url}"
                    self.error_callback(msg)
            # end

            detail_images = item.get('detail_images', [])

            detail_image_total_count += len(detail_images)
            for thumbnail_index, detail_image in enumerate(detail_images):
                if self.is_stop:
                    self.progress_callback(f"[{type}] 이미지 다운로드 중지", LogType.INFO)
                    break

                detail_image_url = detail_image['detail_image_url']
                detail_image_path = detail_image['detail_image_path']
                detail_image_filename = detail_image['detail_image_filename']

                try:
                    detail_image_response = image_function(detail_image_url)
                except Exception as e:
                    msg = f"[{type} {len(result)}개 아이템 중 {item_index + 1}번째 아이템] {item['product_name']} {thumbnail_index + 1}번 상세페이지 이미지 다운로드 오류: {e} 이미지 URL: {detail_image_url}"
                    self.error_callback(msg)
                    continue

                os.makedirs(detail_image_path, exist_ok=True)
                detail_image_full_file_path = make_unique_filename(
                    os.path.join(detail_image_path, detail_image_filename))

                if detail_image_response.status_code == 200:
                    with open(detail_image_full_file_path, 'wb') as f:
                        f.write(detail_image_response.content)
                    msg = f"[{type} {len(result)}개 아이템 중 {item_index + 1}번째 아이템] {item['product_name']} 상세페이지 이미지 저장 완료 [{thumbnail_index + 1}/{len(detail_images)}]"
                    self.info_callback(msg)
                    detail_image_download_success_count += 1
                else:
                    msg = f"[{type} {len(result)}개 아이템 중 {item_index + 1}번째 아이템] {item['product_name']} {thumbnail_index + 1}번 상세페이지 이미지 다운로드 실패 상태 코드: {detail_image_response.status_code} 이미지 URL: {detail_image_url}"
                    self.error_callback(msg)

        self.progress_callback(f"[{type}] 이미지 다운로드 완료", LogType.SUCCESS)
        self.progress_callback(f"[{type}] 엑셀 썸네일 추가 시작", LogType.INFO)

        for thumbnail_index, item in enumerate(result, start=2):
            thumbnail = item.get('excel_thumbnail')
            if thumbnail:
                try:
                    pil_img = PILImage.open(BytesIO(thumbnail)).convert("RGB")
                    output = BytesIO()
                    pil_img.save(output, format="PNG")
                    output.seek(0)

                    img = Image(output)

                    max_size = 80
                    ratio = min(max_size / img.width, max_size / img.height)
                    img.width = int(img.width * ratio)
                    img.height = int(img.height * ratio)

                    col_letter = 'A'
                    ws.add_image(img, f'{col_letter}{thumbnail_index}')

                    ws.row_dimensions[thumbnail_index].height = 80
                    ws.column_dimensions['A'].width = 20
                except Exception as e:
                    logger.error(f"[{type}] 이미지 처리 실패: {e}")

        wb.save(file_path)
        self.progress_callback(f"[{type}] 엑셀 썸네일 추가 완료 {file_path}", LogType.SUCCESS)

        return (f'[{type}] 썸네일 {thumbnail_total_count}건 중 {thumbnail_download_success_count}건 다운로드 성공\n'
                f'상세페이지 이미지 {detail_image_total_count}건 중 {detail_image_download_success_count}건 다운로드 성공')

    def stop_callback(self, task_id):
        self.progress_callback(f"[{task_id}] 실행 중지 완료", LogType.SUCCESS)

        # 모든 그룹이 중지된 후 UI 초기화
        running_tasks = []

        if len(self.musinsa_task.tasks) > 0:
            running_tasks.append(self.musinsa_task)
        if len(self.musinsa_sale_link_task.tasks) > 0:
            running_tasks.append(self.musinsa_sale_link_task)
        if len(self.ably_task.tasks) > 0:
            running_tasks.append(self.ably_task)

        if all(task.all_tasks_stopped() for task in running_tasks):
            logger.info("모든 실행 중인 그룹 중지 완료, UI 초기화")
            UiController.set_input_enabled(self, True)
            for group in [self.musinsa_task, self.musinsa_sale_link_task, self.ably_task]:
                group.reset_tasks()
            UiController.set_timer(self, False)


    def info_callback(self, message):
        def update():
            self.contents.append(f'<span>{message}</span>')
            logger.info(message)

        QTimer.singleShot(0, update)
        QApplication.processEvents()


    def success_callback(self, message):
        def update():
            self.contents.append(f'<span style="color:blue;">{message}</span>')
            logger.info(f"[SUCCESS] {message}")

        QTimer.singleShot(0, update)
        QApplication.processEvents()


    def warning_callback(self, message):
        def update():
            self.contents.append(f'<span style="color:yellow;">{message}</span>')
            logger.warning(f"[WARN] {message}")

        QTimer.singleShot(0, update)
        QApplication.processEvents()

    def error_callback(self, message):
        def update():
            self.contents.append(f'<span style="color:red;">{message}</span>')
            logger.error(f"[ERROR] {message}")

        QTimer.singleShot(0, update)
        QApplication.processEvents()



# ===============================
# Selenium Global 설정
# ===============================


def get_chrome_paths():
    """Chrome 경로와 user_data_dir 경로를 가져오거나 선택하도록 안내"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
            if len(lines) == 2:
                chrome_path = lines[0]
                user_data_dir_path = lines[1]

                # Chrome 디버깅 모드로 실행
                chrome_proc = subprocess.Popen([
                    chrome_path,
                    '--remote-debugging-port=9222',
                    f'--user-data-dir={user_data_dir_path}'
                ])
                time.sleep(2)  # Chrome 기동 대기
                return chrome_proc

    global FIRST_START
    FIRST_START = True

    return None



# ===============================
# 앱 실행
# ===============================
# QApplication 생성 (한 번만)
app = QApplication.instance()
if not app:
    app = QApplication([])
window = MainWindow()
window.show()
sys.exit(app.exec())
