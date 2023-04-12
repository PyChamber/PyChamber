# Taking Measurements with Python

In addition to the graphical user interface, pychamber can in Python scripts.
This can be extremely useful when measuring things like antenna arrays where you
want to take a measurement, change the state of the array, take another
measurement, etc.

Shown below are examples of various kinds of measurements.

## Basic Measurement

This example shows how you can take a simple measurement with the following
setup and save it to `result.mdif`:

- One polarization (Horizontal) that corresponds to S21
- No calibration
- $-90 \leq \theta \leq 90$ in 1 degree increments
- $-180 \leq \varphi \leq 180$ in 1 degree increments
- Frequency: 1 GHz - 3 GHz, 401 points

```python
import pychamber
import skrf
from skrf.vi.vna import keysight
import numpy as np

analyzer = keysight.PNA('GPIB0::16::INSTR')
positioner = pychamber.positioner.connect("Diamond", "D6050", "COM3")

polarizations = [("Horizontal", 2, 1)] # Name, S(a, b)
thetas = np.arange(-90, 91, 1)
phis = np.arange(-180, 181, 1)
freq = skrf.Frequency(start=1_000_000_000, stop=3_000_000_000, npoints=401, unit='Hz')

analyzer.ch1.frequency = freq

experiment = pychamber.Experiment(positioner, thetas, phis, polarizations, f)
result = experiment.run()
result.save('result.mdif')
```

## Calibrated Measurement

This example shows how you can take a simple measurement as above, but this time
applying a calibration. Applying a calibration does not edit the raw data,
instead appending the calibrated values to the existing data.

```python
import pychamber
import skrf
from skrf.vi.vna import keysight
import numpy as np

analyzer = keysight.PNA('GPIB0::16::INSTR')
positioner = pychamber.positioner.connect("Diamond", "D6050", "COM3")

polarizations = [("Horizontal", 2, 1)]
thetas = np.arange(-90, 91, 1)
phis = np.arange(-180, 181, 1)
freq = skrf.Frequency(start=1_000_000_000, stop=3_000_000_000, npoints=401, unit='Hz')

analyzer.ch1.frequency = freq

experiment = pychamber.Experiment(positioner, thetas, phis, polarizations, f)
result = experiment.run()

cal = pychamber.Calibration.load("example_calibration.pycal")
result.apply_calibration(cal)

result.save('result.mdif')
```

## Measurement One Cut Plane

Again, using the same setup as above, but only measuring the theta cut.

```python
import pychamber
import skrf
from skrf.vi.vna import keysight
import numpy as np

analyzer = keysight.PNA('GPIB0::16::INSTR')
positioner = pychamber.positioner.connect("Diamond", "D6050", "COM3")

polarizations = [("Horizontal", 2, 1)]
thetas = np.arange(-90, 91, 1)
phis = np.array([0]) # <-- CHANGED!
freq = skrf.Frequency(start=1_000_000_000, stop=3_000_000_000, npoints=401, unit='Hz')

analyzer.ch1.frequency = freq

experiment = pychamber.Experiment(positioner, thetas, phis, polarizations, f)
result = experiment.run()

cal = pychamber.Calibration.load("example_calibration.pycal")
result.apply_calibration(cal)

result.save('result.mdif')
```

## Array Measurement

Similar setup to the previous, but with multiple polarizations, and changing
array weights. This is accomplished by iterating over array weights, and saving
to a new file for each state. This example assumes you have some other Python
module providing an interface to changing a phased array's weights.

```python
import pychamber
import skrf
from skrf.vi.vna import keysight
import numpy as np

analyzer = keysight.PNA('GPIB0::16::INSTR')
positioner = pychamber.positioner.connect("Diamond", "D6050", "COM3")

polarizations = [("Horizontal", 2, 1)]
thetas = np.arange(-90, 91, 1)
phis = np.arange(-180, 181, 1)
freq = skrf.Frequency(start=1_000_000_000, stop=3_000_000_000, npoints=401, unit='Hz')

experiment = pychamber.Experiment(positioner, thetas, phis, polarizations, f)
analyzer.ch1.frequency = freq

array = # Some class that provides an interface to an array
weights = np.array([
    # first array of weights
    # second array of weights
    ...
])

for i, weight in enumerate(weights):
    array.set_weights(weight) # Example weight setting

    experiment = pychamber.Experiment(positioner, thetas, phis, polarizations, f)
    result = experiment.run()
    result.apply_calibration(cal)
    result.save(f"run{i}.mdif")
```
