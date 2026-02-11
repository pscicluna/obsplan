from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
import astropy.units as u
from astropy.time import Time
from astroplan import Observer, FixedTarget
from astroplan.moon import moon_illumination
from astropy.coordinates import get_body


@dataclass(frozen=True)
class BackupScore:
    target: FixedTarget
    best_airmass: float
    frac_good: float
    best_time: Time


def _time_grid(start: Time, duration: u.Quantity, step: u.Quantity) -> Time:
    n = int(np.floor((duration / step).to_value(u.dimensionless_unscaled))) + 1
    return start + np.arange(n) * step


def _night_mask(
    observer: Observer,
    times: Time,
    *,
    twilight_mode: str,  # "none" | "civil" | "nautical"
) -> np.ndarray:
    """
    Returns a boolean mask for times considered 'observable' by twilight constraint.
    """
    if twilight_mode == "none":
        return np.ones(len(times), dtype=bool)

    # Observer.is_night expects a solar altitude threshold.
    # civil: sun < 0 deg, nautical: sun < -12 deg
    if twilight_mode == "civil":
        max_solar_alt = 0 * u.deg
    elif twilight_mode == "nautical":
        max_solar_alt = -12 * u.deg
    else:
        raise ValueError("twilight_mode must be one of: 'none', 'civil', 'nautical'")

    return observer.is_night(times, horizon=max_solar_alt)


def rank_backup_targets(
    observer: Observer,
    targets: Sequence[FixedTarget],
    start: Time,
    *,
    duration: u.Quantity = 2 * u.hour,
    step: u.Quantity = 2 * u.min,
    max_airmass: float = 2.5,
    min_moon_sep: u.Quantity = 10 * u.deg,
    twilight_mode: str = "civil",
    n_best: int = 10,
    min_good_fraction: float = 0.2,
) -> list[BackupScore]:
    """
    Rank backup targets for the next `duration` starting at `start`.

    Scoring:
      - Filter time points that satisfy:
          airmass <= max_airmass,
          moon separation >= min_moon_sep,
          and twilight constraint (optional).
      - Compute:
          best_airmass = minimum airmass achieved during "good" times
          frac_good = fraction of time points that are good
      - Rank primarily by best_airmass (lower is better), then by frac_good (higher better).

    min_good_fraction avoids selecting targets that are only barely feasible for a moment.
    """
    if len(targets) == 0:
        return []

    times = _time_grid(start, duration, step)
    twilight_ok = _night_mask(observer, times, twilight_mode=twilight_mode)

    # Moon position at each time for separation test
    # (Using get_body('moon', times, location=...) is robust and avoids extra dependencies)
    moon = get_body("moon", times, location=observer.location)

    scores: list[BackupScore] = []
    for t in targets:
        altaz = observer.altaz(times, t)
        airmass = altaz.secz  # sec(z). May be inf below horizon.
        sep = t.coord.separation(moon)

        good = (
            twilight_ok
            & np.isfinite(airmass)
            & (airmass <= max_airmass)
            & (sep >= min_moon_sep)
        )

        frac_good = float(np.mean(good))
        if frac_good < min_good_fraction:
            continue

        # Best (minimum) airmass among good times
        best_idx = np.argmin(airmass[good])
        good_times = times[good]
        best_time = good_times[best_idx]
        best_airmass = float(np.min(airmass[good]))

        scores.append(BackupScore(target=t, best_airmass=best_airmass, frac_good=frac_good, best_time=best_time))

    scores.sort(key=lambda s: (s.best_airmass, -s.frac_good))
    return scores[:n_best]
