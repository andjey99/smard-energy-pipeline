from sqlalchemy import text

from pipeline.load import get_engine, init_db, upsert
from pipeline.transform import to_long


def test_upsert_is_idempotent_and_updates(tmp_path, raw_sample):
    engine = get_engine(f"sqlite:///{tmp_path / 't.db'}")
    init_db(engine)
    df = to_long(raw_sample)
    assert upsert(engine, df) == len(df)
    upsert(engine, df)  # zweiter Lauf darf nichts verdoppeln
    with engine.connect() as c:
        assert c.execute(text("SELECT COUNT(*) FROM energy_hourly")).scalar() == len(df)

    df.loc[0, "wert_mwh"] = 999.0
    upsert(engine, df)
    with engine.connect() as c:
        vals = [r[0] for r in c.execute(text("SELECT wert_mwh FROM energy_hourly"))]
    assert 999.0 in vals


def test_view_exists(tmp_path, raw_sample):
    engine = get_engine(f"sqlite:///{tmp_path / 't.db'}")
    init_db(engine)
    init_db(engine)  # zweimal aufrufbar
    upsert(engine, to_long(raw_sample))
    with engine.connect() as c:
        rows = c.execute(text("SELECT serie, wert_mwh FROM v_energy_daily WHERE serie='netzlast'")).all()
    assert rows and rows[0][1] == 98000


def test_large_upsert_is_batched(tmp_path):
    # 9 Serien x 12 Wochen x 168 Stunden wäre zu groß für einen einzigen INSERT in SQLite
    import pandas as pd
    n = 20000
    df = pd.DataFrame({
        "ts_utc": pd.date_range("2026-01-01", periods=n, freq="h", tz="UTC"),
        "serie": "netzlast",
        "wert_mwh": 1.0,
    })
    engine = get_engine(f"sqlite:///{tmp_path / 'big.db'}")
    init_db(engine)
    assert upsert(engine, df) == n
    with engine.connect() as c:
        assert c.execute(text("SELECT COUNT(*) FROM energy_hourly")).scalar() == n
