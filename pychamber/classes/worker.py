from PyQt5.QtCore import QMutex, QObject


class Worker(QObject):
    def __init__(self, mutex: QMutex, parent=None) -> None:
        self.mutex = mutex
        super(Worker, self).__init__(parent)

    def run(self) -> None:
        raise NotImplementedError("Must be subclassed")
