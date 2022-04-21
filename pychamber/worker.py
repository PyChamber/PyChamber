from PyQt5.QtCore import QMutex, QObject


class Worker(QObject):
    def __init__(self, mutex: QMutex) -> None:
        self.mutex = mutex

    def run(self) -> None:
        raise NotImplementedError("Must be subclassed")
