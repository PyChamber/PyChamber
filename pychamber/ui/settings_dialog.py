import pathlib

from classes.logger import log
from classes.settings_manager import SettingsManager
from PyQt5.QtWidgets import QComboBox, QDialog, QDialogButtonBox, QFileDialog, QFormLayout
from pyvisa.util import get_system_details


class SettingsDialog(QDialog):
    def __init__(self, settings_mgr: SettingsManager, parent=None) -> None:
        super().__init__(parent)
        self.settings_mgr = settings_mgr
        self.setup_widgets()
        self.setup_buttons()

    def setup_widgets(self) -> None:
        layout = QFormLayout()

        self.backend = QComboBox(self)
        self.backend.addItem("Browse...")
        backends = list(get_system_details()['backends'])
        self.backend.addItems(backends)
        self.backend.currentTextChanged.connect(self.backend_browse)

        current_backend = self.settings_mgr['backend']
        idx = self.backend.findText(current_backend)
        if idx != -1:
            self.backend.setCurrentIndex(idx)

        layout.addRow("VISA Backend", self.backend)

        self.setLayout(layout)

    def setup_buttons(self) -> None:
        _buttons = QDialogButtonBox.Apply | QDialogButtonBox.Cancel
        self.button_box = QDialogButtonBox(_buttons)
        self.button_box.button(QDialogButtonBox.Apply).clicked.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout().addWidget(self.button_box)

    def accept(self) -> None:
        self.settings_mgr["backend"] = self.backend.currentText()
        # self.settings_mgr.sync()
        self.close()

    def backend_browse(self, text: str) -> None:
        if text == "Browse...":
            backend_path, _ = QFileDialog.getOpenFileName()
            if backend_path != "":
                path = pathlib.Path(backend_path)
                self.backend.insertItem(2, path.name)
                self.backend.setCurrentIndex(2)
