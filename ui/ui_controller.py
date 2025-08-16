import os
import sys

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QListWidgetItem, QPushButton, QRadioButton, QCheckBox, QLineEdit, QListWidget, \
    QMessageBox, QFileDialog

class UiController:
    @staticmethod
    def show_confirm_dialog(parent):
        msg = QMessageBox()
        msg.setWindowTitle("브라우저 설정 필요")
        msg.setText("브라우저 설정을 완료하고 확인 버튼을 눌러주세요.")
        msg.setStandardButtons(QMessageBox.Ok)
        ret = msg.exec()
        return ret == QMessageBox.Ok

    @staticmethod
    def show_confirm_dialog_chrome_path(parent, CONFIG_FILE):
        msg = QMessageBox()
        msg.setWindowTitle("Chrome 경로 설정 안내")
        msg.setText("프로그램 실행을 위해 Chrome 실행 파일을 선택해주세요.")
        msg.setWindowFlags(msg.windowFlags() | Qt.WindowStaysOnTopHint)

        # 최상단으로 강제
        msg.show()
        msg.raise_()
        msg.activateWindow()
        msg.exec()

        # Chrome 실행 파일 선택
        chrome_path, _ = QFileDialog.getOpenFileName(
            None,
            "Chrome 실행 파일 선택",
            "",
            "Chrome Executable;All Files (*)"
        )

        if not chrome_path:
            print("크롬 경로 선택 취소됨")
            sys.exit()

        user_data_dir_path = os.path.join(os.path.expanduser("~"), "chrome_user_data")
        os.makedirs(user_data_dir_path, exist_ok=True)

        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            f.write(f"{chrome_path}\n{user_data_dir_path}\n")

    @staticmethod
    def set_window_title(parent, message):
        parent.setWindowTitle(message)

    @staticmethod
    def setup_dark_mode(parent):
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
        parent.setStyleSheet(dark_stylesheet)

    @staticmethod
    def setup_icon(parent, app):
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
                parent.setWindowIcon(QIcon(icon_path))
                app.setWindowIcon(QIcon(icon_path))
                break
        else:
            print("아이콘 파일을 찾을 수 없습니다. 기본 아이콘을 사용합니다.")

    @staticmethod
    def set_timer(parent, is_start, message='', time=100):
        if is_start:
            parent.timer = QTimer(parent)
            parent.timer.timeout.connect(lambda: UiController.update_running_char(parent, message))
            parent.timer.start(time)
            parent.label_running.show()
        else:
            parent.timer.stop()
            parent.label_running.hide()

    @staticmethod
    def update_running_char(parent, message):
        parent.label_running.show()
        """label_running의 문자를 업데이트하는 함수"""
        parent.char_index = (parent.char_index + 1) % len(parent.chars)
        parent.label_running.setText(f'{parent.chars[parent.char_index]} {message}')

    # ===============================
    # 공통 헬퍼 함수
    # ===============================
    @staticmethod
    def clear_category_lists(parent):
        """카테고리 1/2 리스트 초기화"""
        parent.category1_list_widget.clear()
        parent.category2_list_widget.clear()

    @staticmethod
    def populate_category_list(list_widget, categories):
        """주어진 QListWidget에 카테고리 데이터 추가"""
        list_widget.clear()
        for cat in categories:
            item = QListWidgetItem(cat.get('title', ''))
            item.setData(Qt.UserRole,
                         {
                             'category_title': cat.get('category_title', ''),
                             'type': cat.get('type', ''),
                             'link_url': cat.get('link_url', ''),
                             'is_sale': cat.get('is_sale', ''),
                             'gender': cat.get('gender', ''),
                         }
            )
            list_widget.addItem(item)

    @staticmethod
    def get_musinsa_category_list(parent):
        """현재 무신사 라디오/세일 여부에 따라 적절한 카테고리 반환"""
        if parent.musinsa_category_type_sale_check.isChecked():
            return parent.musinsa_categories.get(
                'male_sale_categories') if parent.musinsa_category_type_male_radio.isChecked() else parent.musinsa_categories.get(
                'female_sale_categories')
        else:
            return parent.musinsa_categories.get(
                'male_categories') if parent.musinsa_category_type_male_radio.isChecked() else parent.musinsa_categories.get(
                'female_categories')

    @staticmethod
    def add_to_selected(parent, item, skip_if_sale=True):
        """중복 방지 후 선택 리스트에 추가"""
        if skip_if_sale and parent.musinsa_category_type_sale_check.isChecked():
            return  # 세일 모드에서는 category2 없음

        brand_name = "무신사" if parent.musinsa_radio_button.isChecked() else "에이블리"
        title = f'[{brand_name}] {item.text()}' \
            if parent.musinsa_category_type_sale_check.isChecked() or parent.ably_radio_button.isChecked() \
            else (f'[{brand_name}] '
                 f'{parent.category1_list_widget.selectedItems()[0].text()} > '
                 f'{item.text()}')
        if not UiController.is_in_selected(parent, title):
            new_item = QListWidgetItem(title)
            new_item.setData(Qt.UserRole, item.data(Qt.UserRole))
            parent.selected_category_list_widget.addItem(new_item)

    @staticmethod
    def category1_double_click_callback(parent, item):
        """세일 체크박스 선택 시에만 카테고리1 더블클릭 동작"""
        if parent.musinsa_category_type_sale_check.isChecked() or parent.ably_radio_button.isChecked():
            UiController.add_to_selected(parent, item, skip_if_sale=False)

    @staticmethod
    def is_in_selected(parent, title):
        """선택된 리스트에 동일한 항목이 있는지 확인"""
        return any(parent.selected_category_list_widget.item(i).text() == title for i in
                   range(parent.selected_category_list_widget.count()))

    # ===============================
    # 카테고리 UI 로직
    # ===============================
    @staticmethod
    def setup_default_categories(parent):
        """앱 시작 시 기본 무신사 남성 카테고리 로드"""
        UiController.populate_category_list(parent.category1_list_widget, parent.musinsa_categories.get('male_categories', []))
        parent.category2_list_widget.clear()

    @staticmethod
    def musinsa_radio_check_click(parent):
        """무신사 라디오 버튼 상태 변경 시 카테고리 업데이트"""
        categories = UiController.get_musinsa_category_list(parent)
        UiController.populate_category_list(parent.category1_list_widget, categories)
        parent.category2_list_widget.clear()
        # 세일 카테고리일 경우 category2 숨김
        parent.category2_list_widget.setVisible(not parent.musinsa_category_type_sale_check.isChecked())

    @staticmethod
    def setup_categories1(parent, type_):
        # parent.selected_category_list_widget.clear()

        """무신사/에이블리 카테고리 로드"""
        if type_ == 'musinsa':
            # 무신사 관련 UI 표시
            parent.sale_label.show()
            parent.category2_list_widget.show()
            parent.musinsa_category_type_sale_check.show()
            parent.musinsa_male_radio_group.show()
            parent.musinsa_category_type_label.show()
            categories = UiController.get_musinsa_category_list(parent)
        else:
            # 에이블리 UI 숨김
            parent.sale_label.hide()
            parent.category2_list_widget.hide()
            parent.musinsa_category_type_sale_check.hide()
            parent.musinsa_male_radio_group.hide()
            parent.musinsa_category_type_label.hide()
            categories = parent.ably_categories


        UiController.populate_category_list(parent.category1_list_widget, categories)
        parent.category2_list_widget.clear()

    @staticmethod
    def category1_click_callback(parent, item):
        """카테고리1 클릭 시 하위 카테고리(category2) 표시"""
        if parent.musinsa_category_type_sale_check.isChecked():
            return
        categories = UiController.get_musinsa_category_list(parent) \
            if parent.musinsa_radio_button.isChecked() else parent.ably_categories
        found = next((cat for cat in categories if cat['title'] == item.text()), None)
        UiController.populate_category_list(parent.category2_list_widget, found.get('sub', []) if found else [])

    @staticmethod
    def use_category(parent):
        """선택된 카테고리를 사용 목록에 추가"""
        source_list = parent.category1_list_widget \
            if parent.musinsa_category_type_sale_check.isChecked() or parent.ably_radio_button.isChecked() \
            else parent.category2_list_widget
        for item in source_list.selectedItems():
            UiController.add_to_selected(parent, item, skip_if_sale=False)

    @staticmethod
    def disable_category(parent):
        """선택 목록에서 선택된 카테고리 제거"""
        for item in parent.selected_category_list_widget.selectedItems():
            parent.selected_category_list_widget.takeItem(parent.selected_category_list_widget.row(item))

    @staticmethod
    def remove_selected_item(parent, item):
        """더블클릭으로 선택 목록에서 제거"""
        parent.selected_category_list_widget.takeItem(parent.selected_category_list_widget.row(item))

    @staticmethod
    def set_input_enabled(
            parent,
            enabled: bool,
            *,
            lineEdits: bool = True,
            listWidgets: bool = True,
            buttons: bool = True,
            radios: bool = True,
            checks: bool = True,
            exclude: list = None,
    ):
        """
        창 전체에서 버튼/라디오/체크박스를 일괄 활성/비활성.

        :param enabled: True면 활성화, False면 비활성화
        :param buttons: QPushButton 포함 여부
        :param radios: QRadioButton 포함 여부
        :param checks: QCheckBox 포함 여부
        :param exclude: 제외할 위젯 리스트 (옵션)
        """
        exclude = set(exclude or [])
        targets = []

        if listWidgets:
            targets.extend(parent.findChildren(QListWidget))
        if lineEdits:
            targets.extend(parent.findChildren(QLineEdit))
        if buttons:
            targets.extend(parent.findChildren(QPushButton))
        if radios:
            targets.extend(parent.findChildren(QRadioButton))
        if checks:
            targets.extend(parent.findChildren(QCheckBox))

        # 자기 자신(창) 안의 대상 위젯들만 처리
        for element in targets:
            if element in exclude:
                continue
            element.setEnabled(enabled)


    @staticmethod
    def reset(parent):
        parent.musinsa_radio_button.click()
        parent.musinsa_category_type_male_radio.click()
        if parent.musinsa_category_type_sale_check.isChecked():
            parent.musinsa_category_type_sale_check.click()
        parent.count_input.clear()
        parent.selected_category_list_widget.clear()
        parent.excel_name.clear()
        parent.contents.clear()

        parent.progress_bar.setMinimum(0)
        parent.progress_bar.setMaximum(1)
        parent.progress_bar.setValue(0)
        parent.progress_bar.setTextVisible(True)
        parent.progress_bar_value = 0

    @staticmethod
    def exit(parent):
        UiController.stop(parent)

        # Selenium driver 종료
        if getattr(parent, 'driver', None):
            try:
                parent.driver.quit()

                parent.warning_callback(f'Selenium driver 종료 완료')
            except Exception as e:
                parent.error_callback(f"Driver 종료 중 예외 발생: {e}")
            finally:
                parent.driver = None

        # Popen으로 띄운 브라우저 종료
        if getattr(parent, 'chrome_process', None):
            try:
                parent.chrome_process.terminate()  # 또는 kill() 가능
                parent.chrome_process.wait()  # 종료 완료 대기
                parent.warning_callback("Chrome 프로세스 종료 완료")
            except Exception as e:
                parent.error_callback(f"Chrome 프로세스 종료 중 예외 발생: {e}")
            finally:
                parent.chrome_process = None

        parent.warning_callback("프로그램 종료 완료")
        sys.exit()

    @staticmethod
    def stop(parent):
        # 특정 그룹만 중지 가능하거나 전체 그룹 중지
        for group in [parent.musinsa_task, parent.musinsa_sale_task, parent.ably_task]:
            parent.warning_callback(f'[{group.name}] 중지 요청')
            group.stop_all()
            parent.progress_bar.setMinimum(0)
            parent.progress_bar.setMaximum(1)
            parent.progress_bar.setValue(0)
            parent.progress_bar.setTextVisible(True)
            parent.progress_bar_value = 0
            parent.is_stop = True