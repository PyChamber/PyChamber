from pyqtgraph.dockarea import DockLabel


class CustomDockLabel(DockLabel):
    def __init__(self, text, closable=False, fontSize="12px", **kwargs):
        self._bg = kwargs.pop("background_color", "#66c")
        self._bg_dim = kwargs.pop("background_color_inactive", "#44a")
        self._fg = kwargs.pop("font_color", "#fff")
        self._fg_dim = kwargs.pop("font_color_inactive", "#aaa")
        self._border = kwargs.pop("border_color", "#55b")
        self._border_dim = kwargs.pop("border_color_inactive", "#339")

        super().__init__(text, closable, fontSize)

    def updateStyle(self):
        r = "3px"
        if self.dim:
            bg = self._bg_dim
            fg = self._fg_dim
            border = self._border_dim
        else:
            bg = self._bg
            fg = self._fg
            border = self._border

        if self.orientation == "vertical":
            self.vStyle = """DockLabel {{
                background-color : {};
                color : {};
                border-top-right-radius: 0px;
                border-top-left-radius: {};
                border-bottom-right-radius: 0px;
                border-bottom-left-radius: {};
                border-width: 0px;
                border-right: 2px solid {};
                padding-top: 3px;
                padding-bottom: 3px;
                font-size: {};
            }}""".format(
                bg,
                fg,
                r,
                r,
                border,
                self.fontSize,
            )
            self.setStyleSheet(self.vStyle)
        else:
            self.hStyle = """DockLabel {{
                background-color : {};
                color : {};
                border-top-right-radius: {};
                border-top-left-radius: {};
                border-bottom-right-radius: 0px;
                border-bottom-left-radius: 0px;
                border-width: 0px;
                border-bottom: 2px solid {};
                padding-left: 3px;
                padding-right: 3px;
                font-size: {};
            }}""".format(
                bg,
                fg,
                r,
                r,
                border,
                self.fontSize,
            )
            self.setStyleSheet(self.hStyle)
