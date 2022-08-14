from enum import Enum

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QSizePolicy

size_policy = {
    "MIN_MIN": QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum),
    'MIN_PREF': QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred),
    'MIN_EXP': QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding),
    'MIN_FIX': QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed),
    'PREF_MIN': QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum),
    'PREF_PREF': QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred),
    'PREF_FIX': QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed),
    'PREF_MINEXP': QSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding),
    'EXP_MIN': QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum),
    'EXP_PREF': QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred),
    'EXP_EXP': QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding),
}

font = {
    'BOLD_12': QFont('Roboto', 12, QFont.Bold),
    'BOLD_14': QFont('Roboto', 14, QFont.Bold),
    'BOLD_20': QFont('Roboto', 20, QFont.Bold),
    'BOLD_20_IBM': QFont('IBM 3270', 20, QFont.Bold),
}
