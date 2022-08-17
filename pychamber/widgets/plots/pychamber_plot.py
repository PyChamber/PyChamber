from dataclasses import dataclass
from typing import Optional

import skrf
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget

from pychamber.logger import log


@dataclass
class PlotControls:
    polarization: str
    frequency: Optional[str] = None
    azimuth: Optional[float] = None
    elevation: Optional[float] = None


class PyChamberPlot(QWidget):
    new_data_requested = pyqtSignal(PlotControls)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

    def setup(self) -> None:
        self._add_widgets()
        self._connect_signals()
        self.reset()

    def reset(self) -> None:
        ...

    def _connect_signals(self) -> None:
        ...

    def _send_controls_state(self) -> None:
        ...

    def _add_widgets(self) -> None:
        ...

    def rx_updated_data(self, ntwk: skrf.Network) -> None:
        ...
