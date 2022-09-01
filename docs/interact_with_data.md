# Interacting with Data in Python

!!! note "PyChamber is deeply integrated with scikit-rf. Information about scikit-rf objects should be found in [their documentation](https://scikit-rf.readthedocs.io/en/latest/)"

## Loading Measurements

Loading measurements is as simple as importing pychamber and calling `load`.

```python
import pychamber

data = pychamber.load("path/to/data")
```

## Measurement Results

Measurements are all saved to a single NetworkSet in the Experiment plugin's
NetworkModel. Each piece of data contains metadata indicating its:

- Polarization name
- Azimuth
- Elevation

Thankfully, scikit-rf's NetworkSet contains some helpful functions for filtering data.

```py
import pychamber
measurement = pychamber.load("C:/Path/To/Measurement/Data")

# Get all the data for the polarizations named "Vertical" and "Horizontal"
vertical = measurement.sel({
    'polarization': 'Vertical'
})
horizontal = measurement.sel({
    'polarization': 'Horizontal'
})

# Get the elevation=0 cut-plane for the Vertical polarization
el_0_cut = measurement.sel({
    'polarization': 'Vertical',
    'elevation': 0
})
```

Getting data for a range of frequencies is a bit different and it's easiest to
use a list comprehension and create a new NetworkSet. For example:

```python
# Assuming measurement is a NetworkSet with data from 18GHz-40GHz,
# this would be a way to get data for 18GHz - 20GHz
subset = skrf.NetworkSet([ntwk["18GHz-20GHz"] for ntwk in measurement])
```
