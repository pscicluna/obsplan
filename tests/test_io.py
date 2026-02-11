import tempfile
from pathlib import Path
from obsplan.io import read_targets_csv

def test_read_targets_csv_minimal():
    csv = "name,ra_deg,dec_deg\nA,10,20\nB,30,40\n"
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "t.csv"
        p.write_text(csv, encoding="utf-8")
        rows = read_targets_csv(p)
        assert len(rows) == 2
        assert rows[0].name == "A"
        assert rows[0].coord.ra.deg == 10.0
        assert rows[0].coord.dec.deg == 20.0
