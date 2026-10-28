"""Load: Daten idempotent in die Datenbank schreiben (PostgreSQL oder SQLite)."""

import pandas as pd
from sqlalchemy import (Column, DateTime, Float, MetaData, String, Table,
                        create_engine, text)
from sqlalchemy.dialects import postgresql, sqlite

metadata = MetaData()
BATCH_SIZE = 1000

energy_hourly = Table(
    "energy_hourly",
    metadata,
    Column("ts_utc", DateTime(timezone=True), primary_key=True),
    Column("serie", String(40), primary_key=True),
    Column("wert_mwh", Float, nullable=False),
)

# Tagessicht für Power BI: Summen je Quelle und Tag (UTC-Tag, für einfache Auswertung).
VIEW_SQL = """
CREATE VIEW v_energy_daily AS
SELECT CAST(ts_utc AS DATE) AS tag, serie, SUM(wert_mwh) AS wert_mwh
FROM energy_hourly
GROUP BY CAST(ts_utc AS DATE), serie
"""


def get_engine(url: str):
    return create_engine(url, future=True)


def init_db(engine) -> None:
    metadata.create_all(engine)
    with engine.begin() as conn:
        if engine.dialect.name == "postgresql":
            conn.execute(text("CREATE OR REPLACE" + VIEW_SQL.strip()[len("CREATE"):]))
        else:
            conn.execute(text(VIEW_SQL.replace("CREATE VIEW", "CREATE VIEW IF NOT EXISTS")))


def upsert(engine, long_df: pd.DataFrame) -> int:
    """Schreibt Zeilen; vorhandene (ts_utc, serie) werden aktualisiert statt doppelt angelegt."""
    if long_df.empty:
        return 0
    rows = long_df.to_dict(orient="records")
    for r in rows:
        r["ts_utc"] = r["ts_utc"].to_pydatetime()
    insert_fn = postgresql.insert if engine.dialect.name == "postgresql" else sqlite.insert
    with engine.begin() as conn:
        # In Paketen schreiben: Datenbanken begrenzen die Zahl der Parameter pro Befehl.
        for start in range(0, len(rows), BATCH_SIZE):
            stmt = insert_fn(energy_hourly).values(rows[start:start + BATCH_SIZE])
            stmt = stmt.on_conflict_do_update(
                index_elements=["ts_utc", "serie"],
                set_={"wert_mwh": stmt.excluded.wert_mwh},
            )
            conn.execute(stmt)
    return len(rows)
