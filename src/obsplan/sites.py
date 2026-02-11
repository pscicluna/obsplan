from __future__ import annotations

from astroplan import Observer
from astropy.coordinates import EarthLocation


def observer_at_site(site_name: str, *, timezone: str = "UTC") -> Observer:
    """
    Create an astroplan.Observer using Astropy's named site registry.

    Examples of site_name might include "IRTF" (if present in the registry)
    or other observatory names registered in astropy-data.

    If the site string isn't found, EarthLocation.of_site will raise an exception.
    """
    loc = EarthLocation.of_site(site_name)
    return Observer(name=site_name, location=loc, timezone=timezone)
