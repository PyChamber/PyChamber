from pychamber import positioner
from pychamber.api import PluginManager


def test_plugins_registered():
    pm = PluginManager()
    pm.load_plugins()
    assert "Diamond Eng." in positioner.available_models()
    assert "D6050" in positioner.available_models()["Diamond Eng."]
