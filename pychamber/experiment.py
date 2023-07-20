from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from skrf.vi.vna import VNA

import numpy as np
import skrf

from .experiment_result import ExperimentResult
from .positioner import Positioner


class Experiment:
    """An abstraction class that simplifies running experiments from scripts.

    The Experiment class is effectively a wrapper around a function that
    performs a single measurement. This class should only be used during
    scripting. In the GUI, it's related class, ExperimentWorker is used, which
    does various thread / Qt related things.
    """

    def __init__(
        self,
        analyzer: VNA,
        positioner: Positioner,
        thetas: np.ndarray,
        phis: np.ndarray,
        polarizations: list[tuple[str, int, int]],
        frequency: skrf.Frequency,
    ) -> None:
        """
        Args:
            analyzer: Network Analyzer
            positioner: Positioner instance
            thetas: Array of theta locations (in degrees)
            phis: Array of phi locations (in degrees)
            polarizations:
                List of (name, a, b), where a, b are port numbers representing which S parameters correspond to the polarization.
        """
        self._analyzer = analyzer
        self._positioner = positioner
        self._thetas = thetas
        self._phis = phis
        self._polarizations = polarizations
        self._frequency = frequency

        self._result = ExperimentResult(self._thetas, self._phis, [pol[0] for pol in polarizations], self._frequency)

    def run(self) -> ExperimentResult:
        """Run the experiment.

        Runs the experiment as defined. This command will display status
        information using the rich library.

        Returns:
            ExperimentResult: Measured data from the experiment
        """
        from rich import progress
        from rich.console import Console, Group
        from rich.live import Live
        from rich.padding import Padding
        from rich.panel import Panel
        from rich.progress import Progress
        from rich.rule import Rule
        from rich.table import Table

        pro = Progress(
            progress.TextColumn("[progress.description]{task.description}"),
            progress.BarColumn(complete_style="plum1"),
            progress.TaskProgressColumn(),
            progress.TimeRemainingColumn(),
            progress.TimeElapsedColumn(),
        )
        total = pro.add_task("Total Progress", total=len(self._thetas) * len(self._phis))
        cut = pro.add_task("Cut Progress", total=len(self._thetas))
        status = Console().status("", spinner="toggle6")
        group = Group(pro, Padding(Rule("Status"), (1, 0, 0, 0)), status)
        progress_table = Table.grid(expand=True)
        progress_table.add_row(Panel.fit(group, title="Current Experiment", padding=(1, 0, 0, 0)))

        with Live(progress_table, refresh_per_second=10):
            for theta in self._thetas:
                status.update(f"Moving theta to {theta}")
                self._positioner.move_theta_absolute(theta)
                for phi in self._phis:
                    status.update(f"Moving phi to {phi}")
                    self._positioner.move_phi_absolute(phi)
                    for pol_name, a, b in self._polarizations:
                        status.update(f"Capturing {pol_name} polarization")
                        ntwk = self._analyzer.ch1.get_sdata(a, b)
                        ntwk.params = {"phi": phi, "theta": theta, "polarization": pol_name, "calibrated": False}

                        self._result.append(ntwk)
                    pro.update(cut, advance=1)
                    pro.update(total, advance=1)
                pro.reset(cut)

        return self._result
