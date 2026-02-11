import astropy.units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord
from obsplan.config import site_from_latlon
from obsplan.planning import make_observer
from obsplan.plotting import plot_targets_altitude
from astroplan import FixedTarget

def test_plot_targets_altitude_runs():
    site = site_from_latlon("test", lat_deg=0.0, lon_deg=0.0, height_m=0)
    obs = make_observer(site.name, site.location)

    t = FixedTarget(name="X", coord=SkyCoord(0*u.deg, 0*u.deg, frame="icrs"))
    start = Time("2026-02-15 00:00:00")
    end = Time("2026-02-15 02:00:00")
    ax = plot_targets_altitude(obs, [t], start, end, step=30*u.min, title="smoke")
    assert ax is not None
