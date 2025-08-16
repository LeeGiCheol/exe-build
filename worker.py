from PySide6.QtCore import QObject, Signal
from log_type import LogType

# 공통 시그널 클래스
class WorkerSignals(QObject):
    start_signal = Signal(str)
    stop_signal = Signal(str)
    error_signal = Signal(str)
    data_send_signal = Signal(object)
    progress_signal = Signal(str, LogType)
    add_progress_bar_signal = Signal()
    finished_signal = Signal(str)
    category_finished_signal = Signal(dict, list)