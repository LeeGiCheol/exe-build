import os
import random
import sys
import time
import warnings
from datetime import datetime
from urllib.parse import urlencode

from DetailFetchThread import DetailFetchThread
from ExcelWorker import ExcelWorker
from ImageDownloadThread import ImageDownloadThread
from utils import make_unique_filename

import openpyxl
import pandas as pd
import requests
from PySide6.QtCore import QSemaphore, Qt, QTimer, Slot
from PySide6.QtGui import QTextCursor, QIcon
from PySide6.QtWidgets import QWidget, QListWidgetItem, QApplication
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from daangn_land_main_ui import Ui_Form

# urllib3 SSL 경고 억제
warnings.filterwarnings('ignore', message='.*OpenSSL.*')


class MainWindow(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.threads = []
        self.semaphore = QSemaphore(5)
        self.detail_threads = []
        self.all_results = {}
        self.collected_images = set()
        self.all_keys = set()  # 모든 dt 필드 이름 저장용

        self.setupUi(self)
        self.setup_dark_mode()  # 다크모드 적용
        
        # 윈도우 제목 설정
        self.setWindowTitle("당근마켓 부동산 수집기")
        
        # 아이콘 설정
        self.setup_icon()

        self.region_search_button.clicked.connect(self.call_api_and_update)
        self.reset_button.clicked.connect(self.reset_and_option)
        self.region_input.returnPressed.connect(self.call_api_and_update)
        self.region_input.textChanged.connect(self.filter_list)
        self.region_list_widget.itemDoubleClicked.connect(self.region_used)
        self.use_button.clicked.connect(self.region_used)
        self.used_region_list_widget.itemDoubleClicked.connect(self.region_disable)
        self.disable_button.clicked.connect(self.region_disable)
        self.excel_save_button.clicked.connect(self.save_excel)
        self.exit_button.clicked.connect(self.exit)
        self.etc_mapping = {
            '주택': '단독주택',
            '사무실': '업무시설',
            '건물': '제2종 근린생활시설',
            '공장/창고': '공장',
            '토지': '',  # 빈 문자열인 경우
        }

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
        QListWidget {
            background-color: #2b2b2b;
            color: #ffffff;
            border: 1px solid #555555;
        }
        QLineEdit {
            background-color: #3b3b3b;
            color: #ffffff;
            border: 1px solid #555555;
            padding: 5px;
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
        QCheckBox {
            color: #ffffff;
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
            "icon.ico",      # 윈도우
            "icon.icns",     # 맥
            "icon.png",      # 일반 이미지
            "app_icon.ico",
            "app_icon.icns"
        ]
        
        for icon_path in icon_paths:
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
                app.setWindowIcon(QIcon(icon_path))
                print(f"아이콘 설정 완료: {icon_path}")
                break
        else:
            print("아이콘 파일을 찾을 수 없습니다. 기본 아이콘을 사용합니다.")

    def call_api_and_update(self):
        try:
            query = self.region_input.text()
            if not query.strip():
                self.log_message("검색어를 입력해주세요.")
                return

            self.log_message(f"🔍 지역 검색 중: {query}")
            self.region_input.clear()
            self.region_list_widget.clear()

            # API 호출
            response = requests.get(f"https://www.daangn.com/v1/api/search/kr/location?keyword={query}", timeout=10)
            response.raise_for_status()  # HTTP 오류 체크
            
            data = response.json()
            locations = data.get('locations', [])
            
            if not locations:
                self.log_message("검색 결과가 없습니다.")
                return

            # 결과 처리
            for location in locations:
                address = location.get('name1', '') + " " + location.get('name2', '') + " " + location.get('name3', '')
                key = location.get("name", '') + "-" + str(location.get("id", ''))
                region = QListWidgetItem(address)
                region.setData(Qt.ItemDataRole.UserRole, key)
                self.region_list_widget.addItem(region)
            
            self.log_message(f"✅ {len(locations)}개 지역 검색 완료")

        except requests.exceptions.Timeout:
            self.log_message("❌ 검색 시간이 초과되었습니다. 다시 시도해주세요.")
        except requests.exceptions.ConnectionError:
            self.log_message("❌ 네트워크 연결에 실패했습니다. 인터넷 연결을 확인해주세요.")
        except requests.exceptions.RequestException as e:
            self.log_message(f"❌ API 요청 오류: {str(e)}")
        except ValueError as e:
            self.log_message(f"❌ JSON 파싱 오류: {str(e)}")
        except Exception as e:
            self.log_message(f"❌ 예상치 못한 오류: {str(e)}")
            import traceback
            print(f"상세 오류: {traceback.format_exc()}")

    def filter_list(self):
        for i in range(self.region_list_widget.count()):
            region = self.region_list_widget.item(i)
            # 입력 텍스트가 포함되지 않으면 숨기기
            if self.region_input.text().lower() in region.text().lower():
                region.setHidden(False)
            else:
                region.setHidden(True)

    def region_used(self):
        regions = self.region_list_widget.selectedItems()
        for region in regions:
            address = region.text()

            # 이미 사용된 리스트에 같은 텍스트가 있는지 확인
            exists = False
            for i in range(self.used_region_list_widget.count()):
                if self.used_region_list_widget.item(i).text() == address:
                    exists = True
                    break

            if not exists:
                used_region = QListWidgetItem(address)
                used_region.setData(Qt.ItemDataRole.UserRole, region.data(Qt.ItemDataRole.UserRole))
                self.used_region_list_widget.addItem(used_region)

    def region_disable(self):
        regions = self.used_region_list_widget.selectedItems()
        for region in regions:
            row = self.used_region_list_widget.row(region)
            self.used_region_list_widget.takeItem(row)

    def save_excel(self):
        if self.used_region_list_widget.count() <= 0:
            self.contents.setText("지역을 선택해주세요.")
            self.contents.setStyleSheet("color: red;")
            return

        self.contents.clear()
        self.contents.setStyleSheet("color: white;")

        self.progressBar.setValue(0)
        self.progressBar_2.setValue(0)
        self.progressBar_3.setValue(0)
        self.contents.setText("엑셀 저장 중...")
        self._set_controls_enabled(False)
        self.worker = ExcelWorker(self)
        self.worker.log_signal.connect(self.log_message)
        self.worker.finished.connect(self.save_finished)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(self._clear_worker_ref)
        self.worker.start()

    def save_finished(self):
        self.log_message("엑셀 저장 작업이 완료되었습니다.")

    def _set_controls_enabled(self, enabled):
        # exit_button만 제외하고 모두 enabled 상태 변경
        for widget in [
            self.region_search_button,
            self.region_input,
            self.region_list_widget,
            self.use_button,
            self.disable_button,
            self.excel_save_button,
            self.reset_button,
            self.used_region_list_widget,
            self.one_room_check_box,
            self.two_room_checkbox,
            self.officetel_check_box,
            self.apart_check_box,
            self.store_check_box,
            self.house_check_box,
            self.office_check_box,
            self.building_check_box,
            self.factory_check_box,
            self.land_check_box,
            self.month_check_box,
            self.borrow_check_box,
            self.buy_check_box,
            self.short_check_box,
        ]:
            if widget is not self.exit_button:
                widget.setEnabled(enabled)

    def _check_all_progress_complete(self):
        if (
            self.progressBar.value() == self.progressBar.maximum()
            and self.progressBar_2.value() == self.progressBar_2.maximum()
            and self.progressBar_3.value() == self.progressBar_3.maximum()
        ):
            self._set_controls_enabled(True)
            self.reset()

    def perform_excel_save_step(self, log_func=None):
        if log_func is None:
            log_func = self.log_message
        try:
            self.all_results = {}
            self.collected_images = set()
            self.detail_threads = []
            self.detail_thread_queue = []  # 대기 큐 추가
            self.progressBar.setMinimum(0)
            self.progressBar.setMaximum(self.used_region_list_widget.count())
            self.progressBar.setValue(0)
            self.progressBar.setTextVisible(True)
            log_func(f"🚀 크롤링 시작 - 총 {self.used_region_list_widget.count()}개 지역")

            detail_link_list = []
            for index in range(self.used_region_list_widget.count()):
                try:
                    region = self.used_region_list_widget.item(index)
                    self._check_all_progress_complete()
                    params = {
                        "areaViewType": "p",
                        "dealType": "direct",
                        "in": region.data(Qt.ItemDataRole.UserRole),
                        "onlyVerified": False,
                        "salesType": self.create_url_sales_type_parameter(),
                    }
                    url = "https://www.daangn.com/kr/realty/?" + urlencode(params)
                    log_func(f"📍 지역 크롤링: {region.text()} - {url}")
                    try:
                        driver.get(url)
                        time.sleep(random.uniform(2, 3))
                        scroll_and_click_more()
                        items = driver.find_elements(By.CSS_SELECTOR, ".un6cde3")
                        detail_link_list.extend(item.get_attribute("href") for item in items)
                        log_func(f"🔗 발견된 링크 수: {len(detail_link_list)}")
                        self.progressBar.setValue(index + 1)
                    except Exception as e:
                        log_func(f"❌ 지역 크롤링 실패 ({region.text()}): {str(e)}")
                        continue
                except Exception as e:
                    log_func(f"❌ 지역 처리 중 오류: {str(e)}")
                    continue

            self.progressBar_2.setMinimum(0)
            self.progressBar_2.setMaximum(len(detail_link_list))
            self.progressBar_2.setValue(0)
            self.progressBar_2.setTextVisible(True)
            self._progressBar_2_count = 0

            # 큐에 모든 스레드 준비
            for index in range(0, len(detail_link_list)):
                thread = DetailFetchThread(detail_link_list[index], index, len(detail_link_list), self.click_etc_only(), self.etc_values())
                thread.result_signal.connect(self.handle_result)
                thread.image_signal.connect(self.handle_image)
                thread.log_signal.connect(self.log_message)
                thread.finished.connect(self.remove_thread)
                self.detail_thread_queue.append(thread)
            log_func(f"🔄 총 {len(self.detail_thread_queue)}개 스레드 큐 준비 완료")
            self._start_next_detail_threads()
            if len(self.detail_thread_queue) == 0 and len(self.detail_threads) == 0:
                log_func("⚠️ 생성된 스레드가 없어서 즉시 완료 처리")
                self.after_all_details_fetched()
        except Exception as e:
            log_func(f"❌ 크롤링 작업 중 치명적 오류: {str(e)}")
            import traceback
            print(f"상세 오류: {traceback.format_exc()}")
            self._set_controls_enabled(True)

    def _start_next_detail_threads(self):
        # 동시에 5개까지만 실행
        while len(self.detail_threads) < 5 and self.detail_thread_queue:
            thread = self.detail_thread_queue.pop(0)
            self.detail_threads.append(thread)
            thread.start()
            self.log_message(f"🟡 스레드 시작: {thread.detail_link}")

    def remove_thread(self):
        try:
            thread = self.sender()
            if thread is None:
                return
            log_func = self.log_message
            log_func(f"🔻 스레드 종료 신호 받음: {thread.detail_link if hasattr(thread, 'detail_link') else 'Unknown'}")
            if thread and thread in self.detail_threads:
                self.detail_threads.remove(thread)
                log_func(f"✅ 스레드 제거 완료. 남은 스레드: {len(self.detail_threads)}개")
                self._start_next_detail_threads()  # 스레드 종료 시 다음 스레드 실행
                if len(self.detail_threads) == 0 and (not hasattr(self, 'detail_thread_queue') or len(self.detail_thread_queue) == 0):
                    log_func("🎯 마지막 스레드 완료! after_all_details_fetched 호출")
                    self.after_all_details_fetched()
            else:
                log_func("❌ 스레드를 찾을 수 없거나 이미 제거됨")
        except Exception as e:
            print(f"스레드 제거 중 오류: {str(e)}")

    def after_all_details_fetched(self):
        # print(f"🎉 모든 상세 페이지 크롤링 완료!")
        # print(f"📊 수집된 결과: {len(self.all_results)}개")
        # print(f"🖼️ 수집된 이미지: {len(self.collected_images)}개")

        self.download_excel()
        self.download_images()

    def handle_result(self, data):
        unique_key = data.get('내용', '')

        if unique_key and unique_key not in self.all_results:
            self.all_results[unique_key] = data
            self.all_keys.update(data.keys())
            self.log_message(f"📝 새 결과 수집: {len(self.all_results)}개 완료")
        elif unique_key in self.all_results:
            self.log_message(f"⚠️ 중복 데이터 발견 (스킵): {unique_key}")
        else:
            self.log_message(f"❌ 상세페이지 링크가 없는 데이터 (스킵)")

        if hasattr(self, '_progressBar_2_count'):
            self._progressBar_2_count += 1
            self.progressBar_2.setValue(self._progressBar_2_count)
            self._check_all_progress_complete()

    def handle_image(self, image_data):
        self.collected_images.add(frozenset(image_data.items()))
        self.log_message(f"🖼️ 이미지 수집: {len(self.collected_images)}개 완료")

    @Slot(str)
    def log_message(self, msg):
        # 메인 스레드에서 안전하게 UI 업데이트
        def update_ui():
            try:
                self.contents.append(msg)  # append로 변경
                self.contents.moveCursor(QTextCursor.End)
                print(msg)  # 콘솔에도 출력
            except Exception as e:
                print(f"UI 업데이트 오류: {str(e)}")
        
        QTimer.singleShot(0, update_ui)

    def download_excel(self):
        if not self.all_results:
            self.log_message("❌ 저장할 데이터가 없습니다.")
            return

        self.log_message("📊 엑셀 저장 시작...")

        # 1. 층 → 층수 변환
        for row in self.all_results.values():
            if "층" in row and "층수" not in row:
                row["층수"] = row.pop("층")

        # 엑셀 저장 준비: 열 헤더를 모두 포함하도록 DataFrame 생성
        preferred_order = [
            '건축물 용도', '가격', '주소', '아파트명', '전용면적', '공급면적', '사용승인일 (연식)',
            '방/욕실 수', '층수', '방향', '입주 가능일', '관리비', '엘리베이터', '판매자 이름',
            '내용', '상세페이지 링크'
        ]

        # 실제 사용된 키들 (self.all_keys 순서를 유지한 채)
        all_keys_list = ['층수' if k == '층' else k for k in self.all_keys]

        # 우선순위 리스트 중 실제로 존재하는 것만 뽑아냄 (순서 유지)
        ordered_keys = [key for key in preferred_order if key in all_keys_list]

        # all_keys_list 중 위에 포함되지 않은 나머지 키를 그대로 이어 붙임 (정렬 X)
        remaining_keys = [key for key in all_keys_list if key not in ordered_keys]

        # 최종 컬럼 순서
        final_keys = ordered_keys + remaining_keys

        # 데이터 정리
        structured_data = []
        for row in self.all_results.values():
            structured_row = {key: row.get(key, '') for key in final_keys}
            structured_data.append(structured_row)

        # 저장 경로 설정
        today_str = datetime.today().strftime('%Y-%m-%d')
        download_dir = os.path.join('downloads', today_str)
        os.makedirs(download_dir, exist_ok=True)
        file_name = self.excel_name.text()
        if file_name == '':
            file_name = f"당근마켓_부동산정보{self.convert_option_type()}"
        file_name = file_name + ".xlsx"
        excel_path = make_unique_filename(os.path.join(download_dir, file_name))

        # 엑셀 저장
        df = pd.DataFrame(structured_data)
        df.to_excel(excel_path, index=False, engine='openpyxl')

        # 하이퍼링크 적용
        wb = openpyxl.load_workbook(excel_path)
        ws = wb.active

        link_col_idx = None
        for col in ws.iter_cols(1, ws.max_column):
            if col[0].value == "상세페이지 링크":
                link_col_idx = col[0].column
                break

        if link_col_idx:
            for row in range(2, ws.max_row + 1):
                cell = ws.cell(row=row, column=link_col_idx)
                url = cell.value
                if url:
                    cell.hyperlink = url
                    cell.style = "Hyperlink"

        wb.save(excel_path)

        self.log_message(f"✅ 엑셀 저장 완료: {excel_path}")

    def click_etc_only(self):
        if (
                    not self.one_room_check_box.isChecked()
                and not self.two_room_checkbox.isChecked()
                and not self.officetel_check_box.isChecked()
                and not self.apart_check_box.isChecked()
                and not self.store_check_box.isChecked()
                and (
                self.house_check_box.isChecked()
            or self.office_check_box.isChecked()
            or self.building_check_box.isChecked()
            or self.factory_check_box.isChecked()
            or self.land_check_box.isChecked()
        )
        ):
            return True
        return False
    
    def etc_values(self):
        selected_uses = []

        if self.house_check_box.isChecked():
            selected_uses.append(self.etc_mapping['주택'])
        if self.office_check_box.isChecked():
            selected_uses.append(self.etc_mapping['사무실'])
        if self.building_check_box.isChecked():
            selected_uses.append(self.etc_mapping['건물'])
        if self.factory_check_box.isChecked():
            selected_uses.append(self.etc_mapping['공장/창고'])
        if self.land_check_box.isChecked():
            selected_uses.append(self.etc_mapping['토지'])
            
        return selected_uses
    
    def download_images(self):
        if not self.collected_images:
            self.log_message("❌ 다운로드할 이미지가 없습니다.")
            return
        self.log_message(f"🖼️ 이미지 저장 시작: {len(self.collected_images)}개")
        self.progressBar_3.setMinimum(0)
        self.progressBar_3.setMaximum(len(self.collected_images))
        self.progressBar_3.setValue(0)
        self.progressBar_3.setTextVisible(True)
        self._progressBar_3_count = 0
        for image in self.collected_images:
            thread = ImageDownloadThread(
                dict(image).get('image_src'),
                dict(image).get('file_name'),
                self.semaphore
            )
            thread.log_signal.connect(print)
            thread.finished.connect(lambda t=thread: self.remove_image_thread(t))
            self.threads.append(thread)
            thread.start()

    def remove_image_thread(self, thread):
        try:
            if thread and thread in self.threads:
                self.threads.remove(thread)
                if hasattr(self, '_progressBar_3_count'):
                    self._progressBar_3_count += 1
                    self.progressBar_3.setValue(self._progressBar_3_count)
                    self._check_all_progress_complete()
        except Exception as e:
            print(f"이미지 스레드 제거 중 오류: {str(e)}")

    def wait_for_all_threads(self, on_done):
        self.log_message(f"⏳ 스레드 대기 중... 현재 남은 스레드: {len(self.detail_threads)}개")

        def check():
            remaining_threads = len(self.detail_threads)
            if remaining_threads == 0:
                self.log_message("🟢 모든 상세 페이지 스레드 완료!")
                on_done()
            else:
                self.log_message(f"⏳ 대기 중... 남은 스레드: {remaining_threads}개")
                QTimer.singleShot(1000, check)  # 1초마다 체크

        check()

    def create_url_sales_type_parameter(self):
        types = []

        if self.one_room_check_box.isChecked():
            types.append("one_room")
        if self.two_room_checkbox.isChecked():
            types.append("two_room")
        if self.officetel_check_box.isChecked():
            types.append("officetel")
        if self.apart_check_box.isChecked():
            types.append("apart")
        if self.store_check_box.isChecked():
            types.append("store")
        if (
                self.house_check_box.isChecked()
            or self.office_check_box.isChecked()
            or self.building_check_box.isChecked()
            or self.factory_check_box.isChecked()
            or self.land_check_box.isChecked()
            ):
            types.append("etc")

        if types:
            url = ",".join(types)
        else:
            url = ""

        return url

    def create_url_trade_type_parameter(self):
        types = []

        if self.month_check_box.isChecked():
            types.append("month")
        if self.borrow_check_box.isChecked():
            types.append("borrow")
        if self.buy_check_box.isChecked():
            types.append("buy")
        if self.short_check_box.isChecked():
            types.append("short")

        if types:
            url = ",".join(types)
        else:
            url = ""

        return url

    def convert_option_type(self):
        types = []

        if self.one_room_check_box.isChecked():
            types.append("원룸")
        if self.two_room_checkbox.isChecked():
            types.append("투룸빌라")
        if self.officetel_check_box.isChecked():
            types.append("오피스텔")
        if self.apart_check_box.isChecked():
            types.append("아파트")
        if self.store_check_box.isChecked():
            types.append("상가")
        if self.house_check_box.isChecked():
            types.append("기타(주택)")
        if self.office_check_box.isChecked():
            types.append("기타(사무실)")
        if self.building_check_box.isChecked():
            types.append("기타(건물)")
        if self.factory_check_box.isChecked():
            types.append("기타(공장/창고)")
        if self.land_check_box.isChecked():
            types.append("기타(토지)")
        if self.month_check_box.isChecked():
            types.append("월세")
        if self.borrow_check_box.isChecked():
            types.append("전세")
        if self.buy_check_box.isChecked():
            types.append("매매")
        if self.short_check_box.isChecked():
            types.append("단기")

        if types:
            url = "(" + "_".join(types) + ")"
        else:
            url = ""

        return url

    def exit(self):
        if driver:
            driver.close()
        sys.exit()

    def _clear_worker_ref(self):
        self.worker = None

    def reset(self):
        # 실행 중인 스레드들 안전하게 종료
        for thread in self.detail_threads:
            if thread.isRunning():
                thread.quit()
                thread.wait()
        for thread in self.threads:
            if thread.isRunning():
                thread.quit()
                thread.wait()
        
        self.all_keys = set()
        self.all_results = {}
        self.collected_images = set()
        self.detail_threads = []
        self.threads = []

    def reset_and_option(self):
        # 실행 중인 스레드들 안전하게 종료
        for thread in self.detail_threads:
            if thread.isRunning():
                thread.quit()
                thread.wait()
        for thread in self.threads:
            if thread.isRunning():
                thread.quit()
                thread.wait()
        
        self.all_keys = set()
        self.all_results = {}
        self.collected_images = set()
        self.detail_threads = []
        self.threads = []
        self.region_input.clear()
        self.region_list_widget.clear()
        self.used_region_list_widget.clear()
        self.contents.clear()
        self.excel_name.clear()
        self.house_check_box.setChecked(False)
        self.office_check_box.setChecked(False)
        self.building_check_box.setChecked(False)
        self.factory_check_box.setChecked(False)
        self.land_check_box.setChecked(False)
        self.one_room_check_box.setChecked(False)
        self.two_room_checkbox.setChecked(False)
        self.officetel_check_box.setChecked(False)
        self.apart_check_box.setChecked(False)
        self.store_check_box.setChecked(False)
        self.month_check_box.setChecked(False)
        self.borrow_check_box.setChecked(False)
        self.buy_check_box.setChecked(False)
        self.short_check_box.setChecked(False)

def scroll_and_click_more():
    try:
        last_scroll_y = 0

        while True:
            # 문서 전체 높이 가져오기
            document_height = driver.execute_script("return document.body.scrollHeight")

            reached_end = True  # 더보기 버튼을 못 찾으면 종료
            while last_scroll_y < document_height:
                # 랜덤한 스크롤 단위
                scroll_step = random.randint(200, 500)
                last_scroll_y += scroll_step

                driver.execute_script(f"window.scrollTo(0, {last_scroll_y});")
                time.sleep(random.uniform(0.2, 0.5))

                # 더보기 버튼 감지
                more_button = driver.find_elements(
                    By.CSS_SELECTOR,
                    ".hz29bu0.hz29bu5.hz29bu3.sprinkles_width_full_base__1byufe84q"
                )

                if more_button:
                    # 자연스럽게 버튼까지 스크롤 후 클릭
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                                          more_button[0])
                    time.sleep(random.uniform(0.5, 1.2))
                    more_button[0].click()
                    time.sleep(random.uniform(0.5, 1.0))

                    reached_end = False
                    break  # 버튼 클릭 후 다시 scrollHeight 계산

            if reached_end:
                break  # 더보기 버튼 없으면 루프 종료
    except Exception as e:
        print(f"스크롤 중 오류 발생: {str(e)}")
        # 오류가 발생해도 계속 진행
        pass


chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=chrome_options)

app = QApplication()

window = MainWindow()
window.show()

sys.exit(app.exec())