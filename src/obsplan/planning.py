from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable

import astropy.units as u
from astropy.time import Time
from astroplan import Observer, FixedTarget
from astroplan.scheduling import ObservingBlock, Schedule, PriorityScheduler
from astroplan.constraints import (
    AltitudeConstraint,
    AirmassConstraint,
    AtNightConstraint,
    MoonSeparationConstraint,
)


@dataclass(frozen=True)
class NightPlan:
    start: Time
    end: Time
    schedule: Schedule


def make_observer(site_name: str, location, timezone: str = "UTC") -> Observer:
    return Observer(name=site_name, location=location, timezone=timezone)


def to_fixed_targets(target_rows) -> list[FixedTarget]:
    return [FixedTarget(name=t.name, coord=t.coord) for t in target_rows]


def make_blocks(target_rows) -> list[ObservingBlock]:
    blocks: list[ObservingBlock] = []
    for t in target_rows:
        ft = FixedTarget(name=t.name, coord=t.coord)
        blocks.append(
            ObservingBlock.from_exposures(
                target=ft,
                priority=t.priority,
                time_per_exposure=t.exptime_min * u.min,
                number_exposures=1,
                readout_time=0 * u.s,
                configuration={"group": t.group},
            )
        )
    return blocks


def plan_night(
    observer: Observer,
    night: Time,
    target_rows,
    *,
    horizon_alt: u.Quantity = 25 * u.deg,
    max_airmass: float | None = None,
    min_moon_sep: u.Quantity = 20 * u.deg,
    twilight: str = "astronomical",
    slot_size: u.Quantity = 5 * u.min,
) -> NightPlan:
    """
    Build a constraint-based schedule for a single night using astroplan's PriorityScheduler.
    - `night` can be any Time during the date; we compute sunset->sunrise for that night.
    """
    # Define observing window:
    start = observer.twilight_evening_astronomical(night, which="nearest") if twilight == "astronomical" \
        else observer.twilight_evening_civil(night, which="nearest")
    end = observer.twilight_morning_astronomical(night, which="next") if twilight == "astronomical" \
        else observer.twilight_morning_civil(night, which="next")

    constraints = [AltitudeConstraint(min=horizon_alt)]
    if max_airmass is not None:
        constraints.append(AirmassConstraint(max=max_airmass))
    constraints += [
        AtNightConstraint(observer, max_solar_altitude=-18 * u.deg),
        MoonSeparationConstraint(min=min_moon_sep),
    ]

    blocks = make_blocks(target_rows)
    sched = Schedule(start, end)
    scheduler = PriorityScheduler(constraints=constraints, observer=observer, time_resolution=slot_size)
    scheduler(blocks, sched)

    return NightPlan(start=start, end=end, schedule=sched)
