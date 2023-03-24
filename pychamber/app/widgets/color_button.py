# The qtwidgets file has not been updated for use with PySide6
# I should submit a pull request, but for now I'll just make an
# updated class here
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QColorDialog, QPushButton


class ColorButton(QPushButton):
    """
    Custom Qt Widget to show a chosen color.
    Left-clicking the button shows the color-chooser, while
    right-clicking resets the color to the default color (None by default).
    """

    colorChanged = Signal(object)

    def __init__(self, *args, color=None, **kwargs):
        super().__init__(*args, **kwargs)

        self._color = None
        self.update_text = True
        self._default = color
        self.pressed.connect(self.onColorPicker)

        # Set the initial/default state.
        self.color = self._default

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        if color != self._color:
            self._color = color
            self.colorChanged.emit(color)
            if self.update_text:
                self.setText(color)

        if self._color:
            self.setStyleSheet("background-color: %s;" % self._color)
        else:
            self.setStyleSheet("")

    def onColorPicker(self):
        """
        Show color-picker dialog to select color.
        Qt will use the native dialog by default.
        """
        dlg = QColorDialog(self)
        if self._color:
            dlg.setCurrentColor(QColor(self._color))

        if dlg.exec_():
            self.color = dlg.currentColor().name()

    def mousePressEvent(self, e):
        if e.button() == Qt.RightButton:
            self.color = self._default

        return super().mousePressEvent(e)
