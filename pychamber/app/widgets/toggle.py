"""
Taken from https://github.com/pythonguis/python-qtwidgets/blob/a610d6cd20ad946f9de263015e4f62741a52d0b5/qtwidgets/toggle/toggle.py

Adapted for use with PySide6
"""

from qtpy.QtCore import Property, QPoint, QPointF, QRectF, QSize, Qt, Slot
from qtpy.QtGui import QBrush, QColor, QPainter, QPaintEvent, QPen
from qtpy.QtWidgets import QCheckBox


class Toggle(QCheckBox):
    _transparent_pen = QPen(Qt.transparent)
    _light_grey_pen = QPen(Qt.lightGray)

    def __init__(self, parent=None, bar_color=Qt.gray, checked_color="#00B0FF", handle_color=Qt.white):
        super().__init__(parent)

        self._bar_brush = QBrush(bar_color)
        self._bar_checked_brush = QBrush(QColor(checked_color).lighter())

        self._handle_brush = QBrush(handle_color)
        self._handle_checked_brush = QBrush(QColor(checked_color))

        self.setContentsMargins(8, 0, 8, 0)
        self._handle_position = 0

        self.stateChanged.connect(self.handle_state_change)

    def sizeHint(self) -> QSize:
        return QSize(58, 45)

    def hitButton(self, pos: QPoint) -> bool:
        return self.contentsRect().contains(pos)

    def paintEvent(self, e: QPaintEvent) -> None:
        cont_rect = self.contentsRect()
        handle_radius = round(0.24 * cont_rect.height())

        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(self._transparent_pen)

        bar_rect = QRectF(0, 0, cont_rect.width() - handle_radius, 0.40 * cont_rect.height())
        bar_rect.moveCenter(cont_rect.center())
        rounding = bar_rect.height() / 2

        trail_length = cont_rect.width() - 2 * handle_radius
        x_pos = cont_rect.x() + handle_radius + trail_length * self._handle_position

        if self.isChecked():
            p.setBrush(self._bar_checked_brush)
            p.drawRoundedRect(bar_rect, rounding, rounding)
            p.setBrush(self._handle_checked_brush)
        else:
            p.setBrush(self._bar_brush)
            p.drawRoundedRect(bar_rect, rounding, rounding)
            p.setPen(self._light_grey_pen)
            p.setBrush(self._handle_brush)

        p.drawEllipse(QPointF(x_pos, bar_rect.center().y()), handle_radius, handle_radius)

        p.end()

    @Slot(int)
    def handle_state_change(self, value):
        self._handle_position = 1 if value else 0

    @Property(float)
    def handle_position(self):
        return self._handle_position

    @handle_position.setter
    def handle_position(self, pos):
        self._handle_position = pos
        self.update()
