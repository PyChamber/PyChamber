from PyQt5.QtWidgets import QApplication


class PyChamberApp(QApplication):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def gui(self):
        from pychamber.deprecated import MainWindow
        from pychamber.deprecated.controller import PyChamberCtrl

        self.window = MainWindow()
        self.ctrl = PyChamberCtrl(self.window)
