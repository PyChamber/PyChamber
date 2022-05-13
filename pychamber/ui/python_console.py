from typing import Dict, Optional

from PyQt5.QtWidgets import QDialog, QVBoxLayout
from qtconsole.console_widget import ConsoleWidget
from qtconsole.manager import QtKernelManager
from qtconsole.rich_jupyter_widget import RichJupyterWidget


class PythonConsoleWidget(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)

        self.jupyter_widget = self.start_jupyter_widget_with_kernel()
        layout.addWidget(self.jupyter_widget)

    def start_jupyter_widget_with_kernel(self) -> RichJupyterWidget:
        self.kernel_mgr = QtKernelManager()
        self.kernel_mgr.start_kernel()

        self.kernel_client = self.kernel_mgr.client()
        self.kernel_client.start_channels()

        jupyter_widget = RichJupyterWidget()
        jupyter_widget.kernel_manager = self.kernel_mgr
        jupyter_widget.kernel_client = self.kernel_client

        return jupyter_widget

    def shutdown_kernel(self) -> None:
        self.jupyter_widget.kernel_client.stop_channels()  # type: ignore
        self.jupyter_widget.kernel_manager.shutdown_kernel()  # type: ignore

    # def push_vars(self, vars: Dict) -> None:
    #     pass
    #     # self.kernel_mgr.kernel.shell.push(vars)
