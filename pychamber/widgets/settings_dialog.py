"""Defines a window to change application settings."""
from PyQt5.QtWidgets import QComboBox, QDialog, QDialogButtonBox, QFileDialog, QFormLayout

from pychamber.settings import SETTINGS


class SettingsDialog(QDialog):
    """A dialog of user-editable settings.

    This may change soon to enable per-plugin settings.
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setup()

    def setup(self) -> None:
        """Add the control widgets and dialog buttons."""
        self._add_widgets()
        self._setup_buttons()

    def _add_widgets(self) -> None:
        layout = QFormLayout()

        self.backend = QComboBox(self)
        self.backend.addItem("Browse...")
        backends = ['pyvisa-py', 'IVI']
        self.backend.addItems(backends)
        self.backend.textActivated.connect(self.backend_browse)

        current_backend = SETTINGS['analyzer/backend']
        idx = self.backend.findText(current_backend)
        if idx != -1:
            self.backend.setCurrentIndex(idx)
        else:
            self.backend.addItem(current_backend)
            self.backend.setCurrentIndex(self.backend.count() - 1)

        self.py_theme = QComboBox(self)
        # self.py_theme.addItems(pyconsole.themes.keys())
        self.py_theme.setCurrentText(SETTINGS['pyconsole/theme'])

        layout.addRow("VISA Backend", self.backend)
        layout.addRow("Python Console Theme", self.py_theme)

        self.setLayout(layout)

    def _setup_buttons(self) -> None:
        _buttons = QDialogButtonBox.Apply | QDialogButtonBox.Cancel
        self.button_box = QDialogButtonBox(_buttons)
        self.button_box.button(QDialogButtonBox.Apply).clicked.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout().addWidget(self.button_box)

    def accept(self) -> None:
        """Accept the changes and save to SETTINGS."""
        SETTINGS["analyzer/backend"] = self.backend.currentText()
        SETTINGS["pyconsole/theme"] = self.py_theme.currentText()
        self.close()

    def backend_browse(self, text: str) -> None:
        """Open a file browser to find a VISA backend file.

        Arguments:
            text: text string of the combobox
        """
        if text == "Browse...":
            backend_path, _ = QFileDialog.getOpenFileName()
            if backend_path != "":
                self.backend.insertItem(2, backend_path)
                self.backend.setCurrentIndex(2)

    @classmethod
    def display(cls) -> None:
        """Open the dialog."""
        dialog = cls(parent=None)
        dialog.exec_()
