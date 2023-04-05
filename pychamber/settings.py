from qtpy.QtCore import QObject, QSettings, Signal


class SettingsManager(QObject):
    """Persistent Settings.

    Thank you, https://www.pythonguis.com/faq/qsettings-usage/
    """

    settingsChanged = Signal()

    widget_fns = {
        # 'widget class name (e.g. QLineEdit)': (getter, setter)
        "QComboBox": ("currentText", "setCurrentText"),
        "QPushButton": ("text", "setText"),
        "QSpinBox": ("value", "setValue"),
        "QDoubleSpinBox": ("value", "setValue"),
        "QLineEdit": ("text", "setText"),
    }

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)

        self.settings = QSettings("PyChamber", "PyChamber")
        self._widget_map = {}

    def __getitem__(self, key):
        # Try to return the value as the expected type if specified
        if key in self._widget_map:
            _, default, type_ = self._widget_map.get(key, (None, None, None))
            return self.settings.value(key, defaultValue=default, type=type_)
        # Otherwise, just return the value as QSettings interprets it
        else:
            return self.settings.value(key)

    def __setitem__(self, key, value):
        self.settings.setValue(key, value)
        self.settingsChanged.emit()

    def register_widgets(self, widget_map: dict) -> None:
        if not set(self._widget_map.keys()).isdisjoint(set(widget_map.keys())):
            conflicts = set(self._widget_map) & set(widget_map.keys())
            raise RuntimeError(f"Conflicting widget setting names: {conflicts}")
        self._widget_map |= widget_map

    def update_widgets_from_settings(self) -> None:
        for name, (widget, default, type_) in self._widget_map.items():
            widget_cls = widget.__class__.__name__
            _, setter = self.widget_fns.get(widget_cls, (None, None))
            setting_val = self.settings.value(name, defaultValue=default, type=type_)
            if setter and setting_val is not None:
                fn = getattr(widget, setter)
                try:
                    fn(setting_val)
                except Exception as e:
                    print(e)  # TODO: Logging


CONF = SettingsManager()
