from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence

import numpy as np
import matplotlib.pyplot as plt
import astropy.units as u
from astropy.time import Time
from astroplan import Observer, FixedTarget
from astroplan.plots import plot_altitude

from .plotting import plot_targets_altitude  # if in same module, omit this import
from .backups import rank_backup_targets


@dataclass(frozen=True)
class AltPlotConfig:
    min_alt: u.Quantity = 25 * u.deg
    show_grid: bool = True
    legend: bool = True


def time_grid(start: Time, end: Time, step: u.Quantity = 5 * u.min) -> Time:
    n = int(np.floor(((end - start).to(u.min) / step).value)) + 1
    return start + np.arange(n) * step


def plot_targets_altitude(
    observer: Observer,
    targets: Sequence[FixedTarget],
    start: Time,
    end: Time,
    *,
    step: u.Quantity = 5 * u.min,
    title: str = "",
    config: AltPlotConfig = AltPlotConfig(),
    ax=None,
):
    times = time_grid(start, end, step=step)
    if ax is None:
        fig, ax = plt.subplots()

    for t in targets:
        # astroplan's built-in convenience function:
        plot_altitude(t, observer, times, ax=ax)  # stacks lines if ax exists
        # See astroplan plot_altitude API
    ax.axhline(config.min_alt.to_value(u.deg), linestyle="--")
    ax.set_ylim(0, 90)
    ax.set_title(title)
    ax.set_ylabel("Altitude [deg]")
    if config.show_grid:
        ax.grid(True)
    if config.legend:
        ax.legend(loc="best", fontsize="small")
    return ax





def plot_best_backups_next_hours(
    observer: Observer,
    backup_targets: list[FixedTarget],
    start: Time,
    *,
    hours: float = 2.0,
    n_best: int = 10,
    step: u.Quantity = 2 * u.min,
    max_airmass: float = 2.5,
    min_moon_sep: u.Quantity = 10 * u.deg,
    twilight_mode: str = "civil",
    title: str | None = None,
    ax=None,
):
    ranked = rank_backup_targets(
        observer,
        backup_targets,
        start,
        duration=hours * u.hour,
        step=step,
        max_airmass=max_airmass,
        min_moon_sep=min_moon_sep,
        twilight_mode=twilight_mode,
        n_best=n_best,
    )
    best_targets = [s.target for s in ranked]

    end = start + hours * u.hour
    if title is None:
        title = f"Top {len(best_targets)} backups (next {hours:g}h) — twilight={twilight_mode}"

    ax = plot_targets_altitude(
        observer,
        best_targets,
        start,
        end,
        step=step,
        title=title,
        ax=ax,
    )
    return ranked, ax
