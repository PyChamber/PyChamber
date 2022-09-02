"""Horizontal Tab Widget.

From:
https://stackoverflow.com/questions/51230544/pyqt5-how-to-set-tabwidget-west-but-keep-the-text-horizontal?noredirect=1&lq=1 # noqa
"""
from PyQt5.QtCore import QPoint, QRect, QSize
from PyQt5.QtGui import QPaintEvent
from PyQt5.QtWidgets import QStyle, QStyleOptionTab, QStylePainter, QTabBar, QTabWidget


class HorizontalTabBar(QTabBar):
    def tabSizeHint(self, index: int) -> QSize:
        s = QTabBar.tabSizeHint(self, index)
        s.transpose()
        return s

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QStylePainter(self)
        opt = QStyleOptionTab()

        for i in range(self.count()):
            self.initStyleOption(opt, i)
            painter.drawControl(QStyle.CE_TabBarTabShape, opt)
            painter.save()

            s = opt.rect.size()
            s.transpose()
            r = QRect(QPoint(), s)
            r.moveCenter(opt.rect.center())
            opt.rect = r

            c = self.tabRect(i).center()
            painter.translate(c)
            painter.rotate(90)
            painter.translate(-c)
            painter.drawControl(QStyle.CE_TabBarTabLabel, opt)
            painter.restore()


class HorizontalTabWidget(QTabWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setTabBar(HorizontalTabBar(self))
        self.setTabPosition(QTabWidget.West)
