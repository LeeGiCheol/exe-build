from PySide6.QtCore import QRunnable, Slot
from api import get_ably_categories, get_musinsa_categories
from worker import WorkerSignals

class CategoryLoader(QRunnable):
    def __init__(self, task_id, parent):
        super().__init__()
        self.task_id = task_id
        self.parent = parent
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        self.signals.start_signal.emit(self.task_id)

        musinsa = get_musinsa_categories()
        ably = get_ably_categories(self)

        self.signals.category_finished_signal.emit(musinsa, ably)