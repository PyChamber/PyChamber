from PyQt5.QtWidgets import QApplication


class PyChamberApp(QApplication):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def gui(self):
        from pychamber.controller import PyChamberCtrl
        from pychamber.ui import MainWindow

        self.window = MainWindow()
        self.ctrl = PyChamberCtrl(self.window)
