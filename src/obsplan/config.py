from __future__ import annotations
from dataclasses import dataclass
from astropy.coordinates import EarthLocation
import astropy.units as u


@dataclass(frozen=True)
class SiteConfig:
    """Observing site definition."""
    name: str
    location: EarthLocation
    timezone: str = "UTC"  # only used for human-friendly labels


def site_from_latlon(name: str, lat_deg: float, lon_deg: float, height_m: float,
                     timezone: str = "UTC") -> SiteConfig:
    loc = EarthLocation(lat=lat_deg * u.deg, lon=lon_deg * u.deg, height=height_m * u.m)
    return SiteConfig(name=name, location=loc, timezone=timezone)
