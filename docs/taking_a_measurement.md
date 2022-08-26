This page will walk you through the basic steps of taking a measurement.

First we'll walk through the controls in the plugin panel, then look at starting
the experiment and observing the progress with the plots.

## The Analyzer

First, you must connect to an analyzer and set it to take the measurements you
want. Start by choosing a model from the dropdown, then an address, and then
click connect. If the connection was successful, the frequency boxes will be
populated with the current settings of the analyzer.

??? question "Don't see your analyzer listed?"

    Internally, PyChamber uses scikit-rf's virtual instrument module to interfacea
    with a network analyzer. If your analyzer is not listed, consider contributing
    to scikit-rf!

Right now, PyChamber supports simultaneous dual polarization measurements. In
the future, it might support additional simultaneous polarizations, but for now
we just have the two.

You can specify a name or label for each of your two polarizations in the text
boxes, then the associated measurement parameter in the dropdown. The dropdown
should be populated with all measurement parameters possible with your analyzer.
If you only want to take one polarization, set the second to "OFF".

The frequency box allows you to change the frequency settings of your analzyer
and this may be expanded later to allow changing other settings like IF
bandwidth, but for now those other settings must be changed on the analyzer.

You can enter frequencies as a string such as "10 MHz" or as a number like
10000000. The text edit will only allow those two options. The setting on the
analyzer is only changed when you press "Enter" or the text box loses focus.

## Calibration

The process of calibration is covered in detail in
[Calibration](./calibration.md). For now, just now you can load a calibration
file with the "Browse" button, launch the calibration wizard, and view the
currently loaded calibration.

## The Positioner

Now you can select your positioner model and the serial port it's connected to.
Currently only positioners that communicate over serial are supported. Once
you've set the positioner model and port, click connect. If the connection is
successful, the rest of the plugin will become active.

??? question "Don't see your positioner model?"
    PyChamber is in its early stages of development! Please consider
    contributing by adding support for your specific positioner :D

When you first set up for your measurements, you should take care to use the jog
button to align your DUT and define it's origin point. A laser is helpful!
