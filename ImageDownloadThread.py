import re

from PySide6.QtCore import QThread, Signal
import requests
import os
from datetime import datetime

from utils import make_unique_filename


class ImageDownloadThread(QThread):
    log_signal = Signal(str)  # 콘솔 로그 출력용 (선택)

    def __init__(self, image_url, file_name, semaphore, parent=None):
        super().__init__(parent)
        self.image_url = image_url
        self.file_name = file_name
        self.semaphore = semaphore

    def run(self):
        self.semaphore.acquire()  # 🔒 스레드 제한

        try:
            today = datetime.now().strftime('%Y-%m-%d')
            folder_path = os.path.join('downloads', today, 'images')
            os.makedirs(folder_path, exist_ok=True)

            safe_file_name = sanitize_filename(self.file_name)
            file_path = make_unique_filename(os.path.join(folder_path, safe_file_name))

            response = requests.get(self.image_url)
            if response.status_code == 200:
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                # self.log_signal.emit(f"✅ 이미지 저장 완료: {file_path}")
            else:
                self.log_signal.emit(f"❌ 다운로드 실패: {self.image_url}")
        except Exception as e:
            self.log_signal.emit(f"⚠️ 예외 발생: {e}")
        finally:
            self.semaphore.release()  # 🔓 스레드 하나 종료됨

def sanitize_filename(filename):
    # 파일 이름에서 허용되지 않는 문자 제거 또는 대체
    return re.sub(r'[\\/*?:"<>|]', '_', filename)
