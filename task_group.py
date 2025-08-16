from PySide6.QtCore import QThreadPool

class TaskGroup:
    def __init__(self, max_threads=1, code='', name=''):
        self.code = code
        self.name = name
        self.tasks = []
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(max_threads)
        self.total = 0
        self.finished = 0

    def add_task(self, task):
        self.tasks.append(task)

    def start_tasks(
            self,
            debug_mode=False,
            start_callback=None,
            stop_callback=None,
            error_callback=None,
            data_send_callback=None,
            progress_callback=None,
            add_progress_bar_signal=None,
            finished_callback=None,
            category_finished_callback=None,
    ):
        self.total = len(self.tasks)
        self.finished = 0

        for task in self.tasks:
            if start_callback:
                task.signals.start_signal.connect(start_callback)
            if stop_callback:
                task.signals.stop_signal.connect(stop_callback)
            if error_callback:
                task.signals.error_signal.connect(error_callback)
            if data_send_callback:
                task.signals.data_send_signal.connect(data_send_callback)
            if progress_callback:
                task.signals.progress_signal.connect(progress_callback)
            if add_progress_bar_signal:
                task.signals.add_progress_bar_signal.connect(add_progress_bar_signal)
            if finished_callback:
                # 그룹 정보를 전달하고 싶으면 lambda 활용
                task.signals.finished_signal.connect(lambda task_id, t=task: finished_callback(task_id, self))
            if category_finished_callback:
                task.signals.category_finished_signal.connect(category_finished_callback)

            if debug_mode:
                task.run()
            else:
                self.thread_pool.start(task)

    def stop_all(self):
        for task in self.tasks:
            task.stop()
        self.thread_pool.waitForDone()

    def all_tasks_stopped(self):
        """모든 task가 중지된 후 UI 초기화 등 처리"""
        print("✅ 모든 작업 중지 완료")
        self.reset_tasks()

    def reset_tasks(self):
        """그룹 내 task 리스트 초기화"""
        self.stop_all()
        self.tasks = []
        self.total = 0
        self.finished = 0
