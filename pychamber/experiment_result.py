from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

import pathlib
import uuid
from datetime import datetime
from typing import cast

import numpy as np
import skrf
from qtpy.QtCore import QObject, QReadWriteLock, Signal

from pychamber import Calibration


class InvalidFileError(Exception):
    """Exception raised when an attempt to load a result file fails.

    If a valid .mdif file was passed, this error was likely the result of the
    file not containing all the requisite data (thetas, phis, etc).
    """

    pass


class ExperimentResult(QObject):
    """Results from an experiment.

    This class contains the data from running an experiment. It can be appended
    to, have calibrations applied to it, and provides methods to get particular
    subsets of the data like particular cuts or data from a particular
    frequency.

    Attributes:
        dataAppended (PySide6.QtCore.Signal):
            PyQt signal emitted when a data append operation has completed
    """

    dataAppended = Signal()

    def __init__(
        self,
        thetas: np.ndarray,
        phis: np.ndarray,
        polarizations: list[str],
        frequency: skrf.Frequency,
        parent: QObject | None = None,
    ) -> None:
        """
        Args:
            thetas: Array of theta locations (in degrees)
            phis: Array of phi locations (in degrees)
            polarizations:
                List of (name, a, b), where a, b are port numbers representing
                which S parameters correspond to the polarization.
            frequency (skrf.frequency.Frequency): The frequency range of this measurement
        """
        super().__init__(parent)

        self.rw_lock = QReadWriteLock()
        self._ntwk_set = skrf.NetworkSet()
        self._thetas = np.sort(thetas)
        self._phis = np.sort(phis)
        self._polarizations = polarizations
        self._frequency = frequency
        self._s_data = {
            pol: np.full((len(frequency), len(phis), len(thetas)), np.nan, dtype=complex) for pol in polarizations
        }
        self._caled_s_data = {
            pol: np.full((len(frequency), len(phis), len(thetas)), np.nan, dtype=complex) for pol in polarizations
        }

        self._created = datetime.now()
        self._uuid = uuid.uuid4()

    def __str__(self) -> str:
        return (
            f"ExperimentResult(frequencies={self.frequency}, polarizations={self.polarizations}, azimuths={self.phis},"
            f" elevations={self.thetas}) [created {self._created}]"
        )

    def __len__(self) -> int:
        return len(self._ntwk_set)

    def __iter__(self):
        return iter(self._ntwk_set)

    def __getitem__(self, index: int):
        return self._ntwk_set[index]

    @classmethod
    def load(cls, path: str | pathlib.Path) -> ExperimentResult:
        """Load an experiment result from a file.

        This loads an .mdif file and attempts to construct an ExperimentResult
        from it.

        Args:
            path (str | pathlib.Path): path to file

        Returns:
            ExperimentResult:
                The loaded data

        Raises:
            InvalidFileError: When the file is not a valid PyChamber results file
        """
        ns = skrf.NetworkSet.from_mdif(str(path))
        if not ns.has_params():
            raise InvalidFileError(f"{path} is an invalid pychamber results file")

        try:
            thetas = np.array(list(set(ns.params_values["theta"])))
            phis = np.array(list(set(ns.params_values["phi"])))
            pols = list(set(ns.params_values["polarization"]))
            frequency = ns[0].frequency
        except (TypeError, KeyError) as e:
            raise InvalidFileError(f"{path} is an invalid pychamber results file") from e

        for ntwk in ns:
            ntwk.params["calibrated"] = ntwk.params["calibrated"] == "True"

        ret = cls(thetas=thetas, phis=phis, polarizations=pols, frequency=frequency)

        for ntwk in ns:
            pol = ntwk.params["polarization"]
            phi_idx = np.where(ret._phis == ntwk.params["phi"])[0]
            theta_idx = np.where(ret._thetas == ntwk.params["theta"])[0]
            if ntwk.params["calibrated"]:
                ret._caled_s_data[pol][:, phi_idx, theta_idx] = ntwk.s.reshape((-1, 1))
            else:
                ret._s_data[pol][:, phi_idx, theta_idx] = ntwk.s.reshape((-1, 1))
        ret._ntwk_set = ns

        comments = [c.strip() for c in ns.comments.split("@")[:-1]]
        for comment in comments:
            var, val, *_ = comment.split("=")
            if var == "created":
                ret._created = datetime.strptime(val, "%d %b %Y - %H:%M")
            elif var == "uuid":
                ret._uuid = uuid.UUID(val)

        return ret

    def save(self, path: str | pathlib.Path) -> None:
        """Save the result to a file.

        Saves this result to a .mdif file. This is a text-based file format.

        Args:
            path (str | pathlib.Path): The file to save the results to
        """
        # Saving to MDIF fails if networks dont have a name, so just set the names to ""
        for ntwk in self._ntwk_set:
            if ntwk.name is None:
                ntwk.name = ""

        self._ntwk_set.write_mdif(path, comments=[f"created={self.created}@", f"uuid={self.uuid}@"])

    def get_unique_param_vals(self, param: str) -> list[Any]:
        """Get a list of unique values for the specified parameter.

        This is mostly useful internally, but as an example, consider a result
        with 4 data points (skrf.Network) with the following params:

        ```
        [
            {
                'theta': 0,
                'phi': 0,
                'polarization': 'Vertical',
                'calibrated': False,
            },
            {
                'theta': 0,
                'phi': 0,
                'polarization': 'Horizontal',
                'calibrated': False,
            },
            {
                'theta': 0,
                'phi': 5,
                'polarization': 'Vertical',
                'calibrated': False,
            },
            {
                'theta': 0,
                'phi': 5,
                'polarization': 'Horizontal',
                'calibrated': False,
            },
        ]
        ```

        calling `get_unique_param_vals('phi')` would return [0, 5]

        Args:
            param (str): The parameter of interest.

        Returns:
            list[Any]:
                List of unique values associated with the specified parameter.
        """
        if len(self._ntwk_set) == 0:
            return []
        if self._ntwk_set.params_values is None:
            return []
        try:
            return list(set(self._ntwk_set.params_values[param]))
        except KeyError:
            return []

    def _find_nearest(self, array, value) -> tuple:
        idx = np.nanargmin(np.abs(array - value))
        return (idx, array[idx])

    @property
    def frequency(self) -> skrf.Frequency:
        """The frequency range of this result."""
        return self._frequency

    @property
    def f(self) -> np.ndarray:
        """An array of all frequency points in this result"""
        return self.frequency.f

    @property
    def polarizations(self) -> list[str]:
        """A list of polarizations in this result"""
        return self._polarizations

    @property
    def phis(self) -> np.ndarray:
        """A list of phis in this result"""
        return self._phis

    @property
    def thetas(self) -> np.ndarray:
        """A list of thetas in this result"""
        return self._thetas

    @property
    def params(self) -> list | None:
        """The parameter names in this result"""
        return self._ntwk_set.params

    @property
    def raw_data(self) -> skrf.NetworkSet:
        """The subset of this result that has not been calibrated"""
        return self._ntwk_set.sel({"calibrated": False})

    @property
    def calibrated_data(self) -> skrf.NetworkSet:
        """The subset of this result that has been calibrated"""
        return self._ntwk_set.sel({"calibrated": True})

    @property
    def uuid(self) -> str:
        """This result's unique identifier."""
        return str(self._uuid)

    @property
    def created(self) -> str:
        """The time this result object was created"""
        return self._created.strftime("%d %b %Y - %H:%M")

    @property
    def has_calibrated_data(self) -> bool:
        """Whether or not this result contains calibrated data"""
        calibrated = self._ntwk_set.params_values["calibrated"]
        return True in calibrated

    def get_theta_cut(self, polarization: str, frequency: float, phi: float, calibrated: bool = False):
        """Get a subset of data for all thetas and a specific phi.

        Args:
            polarization (str): The name of the polarization you want data for
            frequency (float): What frequency you want data for
            phi (float): The phi value you want a theta cut for
            calibrated (bool): Pass True to request calibrated data

        Returns:
            (np.ndarray): A numpy array of the requested data
        """
        f_idx, _ = self._find_nearest(self.f, frequency)
        phi_idx, _ = self._find_nearest(self._phis, phi)

        if calibrated:
            return self._caled_s_data[polarization][f_idx, phi_idx, :]

        return self._s_data[polarization][f_idx, phi_idx, :]

    def get_phi_cut(self, polarization: str, frequency: float, theta: float, calibrated: bool = False):
        """Get a subset of data for all phis and a specific theta.

        Args:
            polarization (str): The name of the polarization you want data for
            frequency (float): What frequency you want data for
            theta (float): The theta value you want a phi cut for
            calibrated (bool): Pass True to request calibrated data

        Returns:
            (np.ndarray): A numpy array of the requested data
        """
        f_idx, _ = self._find_nearest(self.f, frequency)
        theta_idx, _ = self._find_nearest(self._thetas, theta)

        if calibrated:
            return self._caled_s_data[polarization][f_idx, :, theta_idx]

        return self._s_data[polarization][f_idx, :, theta_idx]

    def get_over_freq_vals(self, polarization: str, theta: float, phi: float, calibrated: bool = False):
        """Get a subset of data for all frequencies at the specified theta and phi.

        Args:
            polarization (str): The name of the polarization you want data for
            theta (float): The theta value you want a phi cut for
            phi (float): The phi value you want a theta cut for
            calibrated (bool): Pass True to request calibrated data

        Returns:
            (np.ndarray): A numpy array of the requested data
        """
        phi_idx, _ = self._find_nearest(self._phis, phi)
        theta_idx, _ = self._find_nearest(self._thetas, theta)

        if calibrated:
            return self._caled_s_data[polarization][:, phi_idx, theta_idx]

        return self._s_data[polarization][:, phi_idx, theta_idx]

    def get_3d_data(self, polarization: str, frequency: float, calibrated: bool = False):
        """Get a subset of data for all thetas and phis at the specified frequency.

        Args:
            polarization (str): The name of the polarization you want data for
            frequency (float): What frequency you want data for
            calibrated (bool): Pass True to request calibrated data

        Returns:
            (np.ndarray): A 2D numpy array of the requested data
        """
        f_idx, _ = self._find_nearest(self.f, frequency)

        if calibrated:
            return self._caled_s_data[polarization][f_idx]

        return self._s_data[polarization][f_idx]

    def append(self, ntwk: skrf.Network, calibration: Calibration | None = None) -> None:
        """Append a data point to the result.

        This command locks the internal QReadWriteLock, which really only
        matters when running in a QApplication.

        Args:
            ntwk (skrf.network.Network): The data to append
            calibration (Calibration | None):
                If a calibration is passed, the raw data and the data after
                applying the calibration will be appended to the result
        """
        name = self._ntwk_set.name
        pol = ntwk.params["polarization"]
        phi_idx = np.where(self._phis == ntwk.params["phi"])[0]
        theta_idx = np.where(self._thetas == ntwk.params["theta"])[0]
        new_ns_list = [*self._ntwk_set, ntwk]

        caled_ntwk: skrf.Network | None = None

        if calibration is not None:
            cal = cast(skrf.Network, calibration.get_polarization(pol))
            calibrated = ntwk / cal.interpolate(self.frequency, kind="nearest")
            caled_ntwk = calibrated.copy()
            caled_ntwk.params = calibrated.params.copy()
            caled_ntwk.params["calibrated"] = True

        if caled_ntwk is not None:
            new_ns_list.append(caled_ntwk)
        new_ns = skrf.NetworkSet(new_ns_list, name=name)

        self.rw_lock.lockForWrite()

        self._ntwk_set = new_ns
        if caled_ntwk is not None:
            self._caled_s_data[pol][:, phi_idx, theta_idx] = caled_ntwk.s.reshape((-1, 1))
        self._s_data[pol][:, phi_idx, theta_idx] = ntwk.s.reshape((-1, 1))

        self.rw_lock.unlock()

        self.dataAppended.emit()

    def apply_calibration(self, calibration: Calibration) -> None:
        """Applies a calibration to this result.

        This method applies the calibration to this result and **appends** the
        calibrated data. In other words, after this method, the result will
        contain both raw and calibrated data.

        Args:
            calibration (Calibration): The calibration to apply to this result

        Raises:
            ValueError: Raised if the calibration does not contain data for any
                of the polarizations in this result
        """
        for pol in self.polarizations:
            if pol not in calibration.polarizations:
                raise ValueError(f"Cannot apply this calibration. It does not contain data for polarization: {pol}.")

        calibrated_ntwks = []
        for pol in self.polarizations:
            uncalibrated = self._ntwk_set.sel({"polarization": pol})
            cal_ntwk = cast(skrf.Network, calibration.get_polarization(pol))
            calibrated = uncalibrated / cal_ntwk.interpolate(self.frequency, kind="nearest")
            # Fix when skrf #887 merged
            for ntwk in calibrated:
                caled_ntwk = ntwk.copy()
                caled_ntwk.params = ntwk.params.copy()
                caled_ntwk.params["calibrated"] = True
                calibrated_ntwks.append(caled_ntwk)

        name = self._ntwk_set.name
        new_ns_list = [*self._ntwk_set.ntwk_set, *calibrated_ntwks]
        new_ns = skrf.NetworkSet(new_ns_list, name=name)

        self.rw_lock.lockForWrite()

        self._ntwk_set = new_ns
        for ntwk in calibrated_ntwks:
            pol = ntwk.params["polarization"]
            phi_idx = np.where(self._phis == ntwk.params["phi"])[0]
            theta_idx = np.where(self._thetas == ntwk.params["theta"])[0]

            self._caled_s_data[pol][:, phi_idx, theta_idx] = ntwk.s.reshape((-1, 1))

        self.rw_lock.unlock()
