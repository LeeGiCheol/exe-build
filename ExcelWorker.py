from PySide6.QtCore import QThread, Signal


class ExcelWorker(QThread):
    progress = Signal(int)
    log_signal = Signal(str)  # 로그 시그널 추가
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window


    def run(self):
        self.log_signal.emit("엑셀 저장 작업 시작!")
        self.main_window.perform_excel_save_step(log_func=self.log_signal.emit)
        self.progress.emit(100)
        self.log_signal.emit("엑셀 저장 작업 완료!")
        self.finished.emit()