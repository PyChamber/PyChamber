from qtpy.QtCore import Signal
from qtpy.QtWidgets import QDialog, QWidget, QFileDialog, QMessageBox

from pyvisa import ResourceManager, LibraryError

from pychamber.settings import CONF
from pychamber.app.ui.settings import Ui_Dialog


class SettingsDialog(QDialog, Ui_Dialog):
    theme_changed = Signal(object)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setupUi(self)

        self.populate_widgets()
        self.connect_signals()

    def show(self):
        self.update_widgets()
        super().show()

    def populate_widgets(self):
        backends = ["@py"]
        current_backend = CONF["visalib"]
        if current_backend is not None and current_backend != "@py":
            backends.append(current_backend)

        self.backend_cb.addItems(backends)
        self.backend_cb.insertSeparator(self.backend_cb.count())
        self.backend_cb.addItem("Browse...")

    def update_widgets(self):
        current_backend = CONF["visalib"]
        if current_backend is not None:
            idx = self.backend_cb.findText(current_backend)
            if idx != -1:
                self.backend_cb.setCurrentIndex(idx)
            else:
                self.backend_cb.addItem(current_backend)
                self.backend_cb.setCurrentIndex(self.backend_cb.count() - 2)

        current_theme = CONF["theme"]
        if current_theme is not None:
            idx = self.theme_cb.findText(current_theme)
            self.theme_cb.setCurrentIndex(idx)

    def connect_signals(self):
        self.backend_cb.currentTextChanged.connect(self.backend_changed)
        self.theme_cb.currentTextChanged.connect(self.theme_changed.emit)

    def backend_changed(self, backend: str):
        if backend == "Browse...":
            backend, _ = QFileDialog.getOpenFileName(self)
            try:
                ResourceManager(backend)
            except LibraryError:
                QMessageBox.critical(self, "Invalid Library", "The selected file is not a valid VISA library.")
                backend = CONF["visalib"]
                idx = self.backend_cb.findText(CONF["visalib"])
                self.backend_cb.setCurrentIndex(idx)

        CONF["visalib"] = backend
