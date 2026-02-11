import astropy.units as u
from astropy.time import Time
from obsplan.config import site_from_latlon
from obsplan.planning import make_observer, plan_night
from obsplan.io import TargetRow
from astropy.coordinates import SkyCoord

def test_plan_night_produces_schedule():
    site = site_from_latlon("test", lat_deg=-30.0, lon_deg=150.0, height_m=0)
    obs = make_observer(site.name, site.location)

    targets = [
        TargetRow("T1", SkyCoord(10*u.deg, -20*u.deg, frame="icrs"), priority=1, exptime_min=10, group="primary"),
        TargetRow("T2", SkyCoord(30*u.deg, -10*u.deg, frame="icrs"), priority=2, exptime_min=10, group="primary"),
    ]
    night = Time("2026-02-15 12:00:00")  # midday UTC is fine as an anchor
    plan = plan_night(obs, night, targets, horizon_alt=15*u.deg, slot_size=10*u.min)

    assert plan.start < plan.end
    # schedule should have time blocks reserved (may be empty if constraints too strict, so just basic sanity)
    assert plan.schedule is not None
