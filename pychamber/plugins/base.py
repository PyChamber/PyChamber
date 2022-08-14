from PyQt5.QtWidgets import QWidget


class PyChamberPlugin(QWidget):
    def setup(self) -> None:
        ...

    def post_visible_setup(self) -> None:
        ...
