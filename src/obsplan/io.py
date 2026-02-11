from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import pandas as pd
from astropy.coordinates import SkyCoord
import astropy.units as u


@dataclass(frozen=True)
class TargetRow:
    name: str
    coord: SkyCoord
    priority: int = 1
    exptime_min: float = 20.0
    group: str = "primary"  # "primary" or "backup" or "night2" etc.


def read_targets_csv(path: str | Path) -> list[TargetRow]:
    """
    CSV columns (minimum):
      name, ra_deg, dec_deg
    Optional:
      priority, exptime_min, group
    """
    df = pd.read_csv(path)
    required = {"name", "ra_deg", "dec_deg"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    rows: list[TargetRow] = []
    for _, r in df.iterrows():
        coord = SkyCoord(ra=float(r["ra_deg"]) * u.deg, dec=float(r["dec_deg"]) * u.deg, frame="icrs")
        rows.append(
            TargetRow(
                name=str(r["name"]),
                coord=coord,
                priority=int(r.get("priority", 1)),
                exptime_min=float(r.get("exptime_min", 20.0)),
                group=str(r.get("group", "primary")),
            )
        )
    return rows
