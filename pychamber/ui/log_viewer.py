import pathlib
import shutil
import tempfile

from classes.logger import log_path
from PyQt5.QtWidgets import QDialog, QFileDialog, QPlainTextEdit, QPushButton, QVBoxLayout


class LogViewer(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout()

        self.text_edit = QPlainTextEdit(self)
        self.text_edit.setReadOnly(True)
        self.setMinimumSize(500, 500)

        self.save_btn = QPushButton("Save Logs", self)
        self.save_btn.pressed.connect(self.save_logs)

        layout.addWidget(self.text_edit)
        layout.addWidget(self.save_btn)
        self.setLayout(layout)
        self.setWindowTitle("PyChamber - Log")

        self.load_logs()

    @classmethod
    def display(cls) -> None:
        viewer = cls(parent=None)
        viewer.exec_()

    def load_logs(self) -> None:
        with open(log_path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                self.text_edit.appendPlainText(line.strip())

    def save_logs(self) -> None:
        save_path, _ = QFileDialog.getSaveFileName()
        if save_path != "":
            shutil.copyfile(log_path, save_path)
