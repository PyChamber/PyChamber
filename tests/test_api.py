from pychamber.api import PluginManager


def test_plugin_manager_creation(mocker):
    mocker.patch("pychamber.api.PluginManager.iter_namespace", return_value=[("", "test", "")])
    pm = PluginManager()

    expected_plugins = {"test"}

    assert pm.plugins == expected_plugins
    assert pm.plugin_dirs == []


def test_plugin_manager_import_plugin(mocker):
    mocker.patch("pychamber.api.PluginManager.iter_namespace", return_value=[("", "test", "")])
    mock_plugin = mocker.Mock()
    mocker.patch("pychamber.api.importlib.import_module", return_value=mock_plugin)

    pm = PluginManager()
    assert pm.import_plugin("test") == mock_plugin


def test_plugin_manager_load_plugins(mocker):
    mocker.patch("pychamber.api.PluginManager.iter_namespace", return_value=[("", "test", "")])
    mock_plugin = mocker.Mock()
    mocker.patch("pychamber.api.PluginManager.import_plugin", return_value=mock_plugin)
    pm = PluginManager()
    pm.load_plugins()
    mock_plugin.initialize.assert_called_once()
