"""Transform: Rohdaten bereinigen und Kennzahlen berechnen."""

import pandas as pd

from pipeline import config


def to_long(raw: dict) -> pd.DataFrame:
    """Wandelt {serie: [[ms, wert], ...]} in eine Tabelle (ts_utc, serie, wert_mwh).

    - Werte ohne Zeitstempel oder ohne Messwert (z. B. Stunden in der Zukunft) fliegen raus.
    - Doppelte Einträge (überlappende Blöcke) werden entfernt, der letzte Wert gewinnt.
    """
    frames = []
    for key, points in raw.items():
        if not points:
            continue
        df = pd.DataFrame(points, columns=["ts_ms", "wert_mwh"])
        df["serie"] = key
        frames.append(df)
    if not frames:
        return pd.DataFrame(columns=["ts_utc", "serie", "wert_mwh"])

    df = pd.concat(frames, ignore_index=True)
    df = df.dropna(subset=["ts_ms", "wert_mwh"])
    df["ts_utc"] = pd.to_datetime(df["ts_ms"].astype("int64"), unit="ms", utc=True)
    df["wert_mwh"] = df["wert_mwh"].astype(float)
    df = df.drop_duplicates(subset=["ts_utc", "serie"], keep="last")
    return df[["ts_utc", "serie", "wert_mwh"]].sort_values(["ts_utc", "serie"]).reset_index(drop=True)


def daily_mix(long_df: pd.DataFrame) -> pd.DataFrame:
    """Tageswerte (deutsche Zeit) je Quelle plus Anteil Erneuerbarer an der erfassten Erzeugung."""
    if long_df.empty:
        return pd.DataFrame()
    df = long_df.copy()
    df["tag"] = df["ts_utc"].dt.tz_convert("Europe/Berlin").dt.date
    wide = df.pivot_table(index="tag", columns="serie", values="wert_mwh", aggfunc="sum")

    ren = [c for c in config.RENEWABLE_KEYS if c in wide.columns]
    gen = [c for c in config.GENERATION_KEYS if c in wide.columns]
    wide["erneuerbar_mwh"] = wide[ren].sum(axis=1) if ren else 0.0
    wide["erzeugung_mwh"] = wide[gen].sum(axis=1) if gen else 0.0
    wide["anteil_erneuerbar_pct"] = (
        (wide["erneuerbar_mwh"] / wide["erzeugung_mwh"]).where(wide["erzeugung_mwh"] > 0) * 100
    ).round(1)
    return wide.reset_index()
