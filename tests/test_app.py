from pychamber.app.main_window import MainWindow


def test_main_window_construction(qtbot):
    main_window = MainWindow()
    main_window.show()
    qtbot.addWidget(main_window)

    controls = main_window.controls_area
    exp = controls.experiment_controls
    ana = controls.analyzer_controls
    pos = controls.positioner_controls

    assert exp.section.toggle_button.text() == "Experiment"
    assert ana.section.toggle_button.text() == "Analyzer"
    assert pos.section.toggle_button.text() == "Positioner"

    assert not main_window.total_progress_gb.isVisible()
    assert not main_window.cut_progress_gb.isVisible()
    assert not main_window.time_remaining_gb.isVisible()
