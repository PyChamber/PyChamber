from pychamber import positioner


def test_factory_register(mocker):
    mock_positioner_model = mocker.Mock()
    positioner.register("mock", "mock", mock_positioner_model)

    assert positioner.factory._MODELS == {"mock": {"mock": mock_positioner_model}}


def test_available_models(mocker):
    mock_positioner_model = mocker.Mock()
    positioner.register("mock", "mock", mock_positioner_model)
    assert positioner.available_models() == {"mock": {"mock": mock_positioner_model}}


def test_factory_unregister(mocker):
    mock_positioner_model = mocker.Mock()
    positioner.register("mock", "mock", mock_positioner_model)
    positioner.unregister("mock", "mock")

    assert positioner.factory._MODELS == {"mock": {}}


def test_factory_connect(mocker):
    mock_positioner_model = mocker.MagicMock()
    positioner.register("mock", "mock", mock_positioner_model)
    positioner.connect("mock", "mock", address="COM0")

    print(positioner.available_models())
    mock_positioner_model.assert_called_once_with(address="COM0")
