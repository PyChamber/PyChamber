import webbrowser

from PyQt5.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout

import pychamber


class AboutPyChamber(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout()

        self.label = QLabel(self)
        self.label.setText(
            f"""
            <html><p>
            PyChamber v{pychamber.__version__}<br/>
            <br/>
            Developed by:
            <ul>
            <li>Bailey Campbell</li>
            </ul>
            Contribute on <a
            href="https://github.com/HRG-Lab/pychamber">GitHub</a>
            </p></html>
            """
        )
        self.label.setOpenExternalLinks(True)

        layout.addWidget(self.label)
        self.setLayout(layout)

        self.setWindowTitle("About PyChamber")

    @classmethod
    def display(cls) -> None:
        about = cls(parent=None)
        about.exec_()
