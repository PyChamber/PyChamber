import pathlib

from classes.settings_manager import SettingsManager
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
)
from pyvisa.util import get_system_details
from ui import pyconsole


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
        backends = ['pyvisa-py', 'IVI']
        self.backend.addItems(backends)
        self.backend.textActivated.connect(self.backend_browse)

        current_backend = self.settings_mgr['backend']
        idx = self.backend.findText(current_backend)
        if idx != -1:
            self.backend.setCurrentIndex(idx)
        else:
            self.backend.addItem(current_backend)
            self.backend.setCurrentIndex(self.backend.count() - 1)

        self.py_theme = QComboBox(self)
        self.py_theme.addItems(pyconsole.themes.keys())
        self.py_theme.setCurrentText(self.settings_mgr['python-theme'])

        self.polar_autoscale = QCheckBox(self)
        self.polar_autoscale.setChecked(self.settings_mgr['polar-autoscale'])

        self.overfreq_autoscale = QCheckBox(self)
        self.overfreq_autoscale.setChecked(self.settings_mgr['overfreq-autoscale'])

        layout.addRow("VISA Backend", self.backend)
        layout.addRow("Python Console Theme", self.py_theme)
        layout.addRow("Auto-scale Polar Plot During Experiment", self.polar_autoscale)
        layout.addRow(
            "Auto-scale Over Frequency Plot During Experiment", self.overfreq_autoscale
        )

        self.setLayout(layout)

    def setup_buttons(self) -> None:
        _buttons = QDialogButtonBox.Apply | QDialogButtonBox.Cancel
        self.button_box = QDialogButtonBox(_buttons)
        self.button_box.button(QDialogButtonBox.Apply).clicked.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout().addWidget(self.button_box)

    def accept(self) -> None:
        self.settings_mgr["backend"] = self.backend.currentText()
        self.settings_mgr["python-theme"] = self.py_theme.currentText()
        self.close()

    def backend_browse(self, text: str) -> None:
        if text == "Browse...":
            backend_path, _ = QFileDialog.getOpenFileName()
            if backend_path != "":
                self.backend.insertItem(2, backend_path)
                self.backend.setCurrentIndex(2)
