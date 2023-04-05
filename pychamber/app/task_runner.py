import sys
import traceback

from qtpy.QtCore import QObject, QRunnable, Signal

# https://www.pythonguis.com/tutorials/multithreading-pyqt6-applications-qthreadpool/


class TaskRunnerSignals(QObject):
    gotResult = Signal(object)
    error = Signal(object)
    finished = Signal()


class TaskRunner(QRunnable):
    def __init__(self, fn: callable, *args, **kwargs):
        super().__init__()

        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = TaskRunnerSignals()

    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
        except Exception:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.gotResult.emit(result)
        finally:
            self.signals.finished.emit()
