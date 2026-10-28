import pandas as pd

from pipeline.transform import daily_mix, to_long
from tests.conftest import T0


def test_to_long_drops_missing_and_converts(raw_sample):
    df = to_long(raw_sample)
    assert list(df.columns) == ["ts_utc", "serie", "wert_mwh"]
    # 3 + 2 + 2 + 2 + 3 Rohpunkte, davon 2 ohne Wert/Zeitstempel
    assert len(df) == 10
    assert df["ts_utc"].dt.tz is not None
    assert df["ts_utc"].min() == pd.Timestamp(T0, unit="ms", tz="UTC")


def test_to_long_removes_duplicates_keeps_last():
    raw = {"netzlast": [[T0, 1.0], [T0, 2.0]]}
    df = to_long(raw)
    assert len(df) == 1
    assert df.loc[0, "wert_mwh"] == 2.0


def test_to_long_empty():
    assert to_long({"netzlast": []}).empty


def test_daily_mix_renewable_share(raw_sample):
    mix = daily_mix(to_long(raw_sample))
    assert len(mix) == 1  # beide Stunden fallen auf denselben deutschen Kalendertag
    row = mix.iloc[0]
    # erneuerbar: Wind 22000 + PV 0; Erzeugung: 22000 + Braunkohle 16000 + Gas 2000 = 40000
    assert row["erneuerbar_mwh"] == 22000
    assert row["erzeugung_mwh"] == 40000
    assert row["anteil_erneuerbar_pct"] == 55.0
    # Netzlast zählt nicht als Erzeugung
    assert row["netzlast"] == 98000
