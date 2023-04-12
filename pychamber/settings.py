from qtpy.QtCore import QObject, QSettings, Signal


class SettingsManager(QObject):
    """Persistent settings manager.

    This class uses Qt's QSettings class which abstracts platform-specific
    locations for persistent settings. For example, on Windows this is the
    registry, and on Linux it's typically ~/.config/<application name>.

    Beyond maintaining settings, the GUI can also register widgets with
    particular settings so that they may be saved to a setting when changed, and
    updated from stored settings when the application is loaded.

    You should **NOT** need to instantiate a SettingsManager yourself. Instead, you
    should opt to import and use the global CONF object like

    ```python
        from pychamber.settings import CONF
    ```

    Attributes:
        settingsChanged (PySide6.QtCore.Signal): Signal emitted when settings
            are changed

        widget_fns (dict): Dictionary of QWidget names, and their getter/setter
            methods. This is used when updating widgets with existing settings
            or when updating settings from widgets.
    """

    # Thank you, https://www.pythonguis.com/faq/qsettings-usage/

    settingsChanged = Signal()

    widget_fns = {
        # 'widget class name (e.g. QLineEdit)': (getter, setter)
        "QComboBox": ("currentText", "setCurrentText"),
        "QPushButton": ("text", "setText"),
        "QSpinBox": ("value", "setValue"),
        "QDoubleSpinBox": ("value", "setValue"),
        "QLineEdit": ("text", "setText"),
        "QCheckBox": ("isChecked", "setChecked"),
        "Toggle": ("isChecked", "setChecked"),
    }

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)

        self.settings = QSettings("PyChamber", "PyChamber")
        self._widget_map = {}

    def __getitem__(self, key: str):
        """Tries to retrive the value specified by key.

        If the setting has been registered, it will be cast to the appropriate
        type before being returned

        Args:
            key: The setting name

        Returns:
            (Any): The value associated with the key
        """
        # Try to return the value as the expected type if specified
        if key in self._widget_map:
            _, default, type_ = self._widget_map.get(key, (None, None, None))
            return self.settings.value(key, defaultValue=default, type=type_)
        # Otherwise, just return the value as QSettings interprets it
        else:
            return self.settings.value(key)

    def __setitem__(self, key, value):
        """Changes the setting to the specified value"""
        self.settings.setValue(key, value)
        self.settingsChanged.emit()

    def register_widgets(self, widget_map: dict) -> None:
        """Registers widgets with the settings object.

        When creating widgets with values you want to be persistent, you can
        register them by creating a widget map and calling this function. The
        widget_map should be of the form:

        ```python
            widget_map = {
                "<key>": (<widget>, <default value>, <type>),
            }
        ```

        Args:
            widget_map: A dictionary of the type described
        """
        if not set(self._widget_map.keys()).isdisjoint(set(widget_map.keys())):
            conflicts = set(self._widget_map) & set(widget_map.keys())
            raise RuntimeError(f"Conflicting widget setting names: {conflicts}")
        self._widget_map |= widget_map

    def update_widgets_from_settings(self) -> None:
        """Updates registered widgets from the stored settings."""
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
