from __future__ import annotations
import argparse
from pathlib import Path

import matplotlib.pyplot as plt
from astropy.time import Time
from astroplan import FixedTarget
import astropy.units as u

from .backups import rank_backup_targets
from .plotting import plot_best_backups_next_hours
from .config import site_from_latlon
from .io import read_targets_csv
from .planning import make_observer, plan_night, to_fixed_targets
from .plotting import plot_targets_altitude


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--targets", required=True, help="CSV file with targets")
    ap.add_argument("--date", required=True, help="Night date/time (e.g. 2026-02-15 12:00:00)")
    ap.add_argument("--lat", type=float, required=True)
    ap.add_argument("--lon", type=float, required=True)
    ap.add_argument("--height", type=float, default=0.0)
    ap.add_argument("--outdir", default="out")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    site = site_from_latlon("site", args.lat, args.lon, args.height, timezone="UTC")
    observer = make_observer(site.name, site.location, timezone=site.timezone)

    targets = read_targets_csv(args.targets)
    night = Time(args.date)

    # Primary schedule uses "primary" group rows:
    primary_rows = [t for t in targets if t.group == "primary"]
    backup_rows = [t for t in targets if t.group != "primary"]

    plan = plan_night(observer, night, primary_rows)

    # Plot primaries:
    ax = plot_targets_altitude(
        observer,
        to_fixed_targets(primary_rows),
        plan.start,
        plan.end,
        title=f"Primary targets altitudes ({night.isot.split('T')[0]})",
    )
    plt.tight_layout()
    plt.savefig(outdir / "primary_altitudes.png", dpi=200)
    plt.close()

    # Plot backups:
    if backup_rows:
        ax = plot_targets_altitude(
            observer,
            to_fixed_targets(backup_rows),
            plan.start,
            plan.end,
            title=f"Backup targets altitudes ({night.isot.split('T')[0]})",
        )
        plt.tight_layout()
        plt.savefig(outdir / "backup_altitudes.png", dpi=200)
        plt.close()

    # Save a human-readable schedule:
    with open(outdir / "schedule.txt", "w", encoding="utf-8") as f:
        f.write(str(plan.schedule))

    now = Time.now()  # or Time(args.date) if you want a planned "now"
    backup_fixed = to_fixed_targets(backup_rows)

    ranked, ax = plot_best_backups_next_hours(
        observer,
        backup_fixed,
        now,
        hours=2.0,
        n_best=10,
        step=2*u.min,
        max_airmass=2.5,
        min_moon_sep=10*u.deg,
        twilight_mode="civil",   # or "nautical" for science-only mode
        title="Best backups for the next 2 hours",
    )
    plt.tight_layout()
    plt.savefig(outdir / "best_backups_next2h.png", dpi=200)
    plt.close()

    with open(outdir / "best_backups_next2h.txt", "w", encoding="utf-8") as f:
        for s in ranked:
            f.write(f"{s.target.name}\tbest_airmass={s.best_airmass:.3f}\tfrac_good={s.frac_good:.2f}\tbest_time={s.best_time.isot}\n")


if __name__ == "__main__":
    main()
