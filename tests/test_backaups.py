import astropy.units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord
from astroplan import FixedTarget

from obsplan.sites import observer_at_site
from obsplan.backups import rank_backup_targets


def test_rank_backup_targets_returns_sorted_list():
    # Use a generic named site if available on your system.
    # Replace "IRTF" with the site string you use in production once confirmed.
    obs = observer_at_site("IRTF", timezone="US/Hawaii")

    start = Time("2026-02-15 08:00:00")  # arbitrary UTC time
    targets = [
        FixedTarget("A", SkyCoord(0*u.deg, 0*u.deg, frame="icrs")),
        FixedTarget("B", SkyCoord(120*u.deg, 20*u.deg, frame="icrs")),
        FixedTarget("C", SkyCoord(240*u.deg, -10*u.deg, frame="icrs")),
    ]

    ranked = rank_backup_targets(
        obs, targets, start,
        duration=2*u.hour, step=10*u.min,
        max_airmass=2.5, min_moon_sep=10*u.deg,
        twilight_mode="none",
        n_best=10,
        min_good_fraction=0.0,
    )

    assert isinstance(ranked, list)
    # If any are feasible, ensure sorted by best_airmass increasing
    for i in range(1, len(ranked)):
        assert ranked[i-1].best_airmass <= ranked[i].best_airmass
