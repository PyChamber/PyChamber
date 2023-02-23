from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtCore import QModelIndex, QPersistentModelIndex
    from PySide6.QtGui import QPainter
    from PySide6.QtWidgets import QStyleOptionViewItem, QWidget

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QStandardItem
from PySide6.QtWidgets import QComboBox, QItemDelegate, QStyle


class CategoryComboBoxDelegate(QItemDelegate):
    def paint(
        self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex
    ) -> None:
        if index.data(Qt.AccessibleDescriptionRole) == "separator":
            painter.setPen(Qt.gray)
            painter.drawLine(
                option.rect.left(), option.rect.center().y(), option.rect.right(), option.rect.center().y()
            )
        elif index.data(Qt.AccessibleDescriptionRole) == "parent":
            parent_option = option
            parent_option.state |= QStyle.State_Enabled
            super().paint(painter, parent_option, index)
        elif index.data(Qt.AccessibleDescriptionRole) == "child":
            child_option = option
            indent = option.fontMetrics.horizontalAdvance("    ")
            child_option.rect.adjust(indent, 0, 0, 0)
            child_option.textElideMode = Qt.ElideNone
            super().paint(painter, child_option, index)
        else:
            super().paint(painter, option, index)


class CategoryComboBox(QComboBox):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setItemDelegate(CategoryComboBoxDelegate())

    def add_parent(self, text: str) -> None:
        item = QStandardItem(text)
        item.setFlags(item.flags() ^ (Qt.ItemIsEnabled | Qt.ItemIsSelectable))
        item.setData("parent", Qt.AccessibleDescriptionRole)
        font = QFont()
        font.setBold(True)
        item.setFont(font)
        self.model().appendRow(item)

    def add_child(self, text: str, data) -> None:
        item = QStandardItem(text)
        item.setData(data, Qt.UserRole)
        item.setData("child", Qt.AccessibleDescriptionRole)
        self.model().appendRow(item)
