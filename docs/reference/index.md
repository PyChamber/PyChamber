# API Reference

PyChamber includes an API that allows easier scripting. This pages summarizes
that API and provides some helpful examples.

The goal is to eventually provide functions to allow the user to script
measurements entirely. This would allow users to make adjustments external to
the operation of the chamber like changing weights in a phased array without
having to continuously enter the chamber or switch back and forth between programs.

!!! note "PyChamber is deeply integrated with scikit-rf. Information about scikit-rf objects should be found in [their documentation](scikit-rf.readthedocs.io/)"

## Measurement Results

When a measurement is taken, it is tagged with the corresponding label (user
provided but "Polarization 1" or "Polarization 2" by default) and stored in a
dictionary of NetworkModels. NetworkModels are simply extensions of scikit-rf's
NetworkSet that provides helpful functions that are relevant to chamber
measurements. Roughly:

```py
{
    "Polarization 1": NetworkModel,
    "Polarization 2": NetworkModel,
}
```

which is what the object that will be returned when loading measurements from a
previous experiment.

## Loading Measurements

Loading measurements is as simple as importing pychamber and calling `load`.

```python
import pychamber

data = pychamber.load("path/to/data")
```
