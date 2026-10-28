"""Integrationstest gegen echtes PostgreSQL. Läuft nur, wenn TEST_DATABASE_URL gesetzt ist (z. B. in CI)."""
import os

import pytest
from sqlalchemy import text

from pipeline.load import get_engine, init_db, upsert
from pipeline.transform import to_long

URL = os.getenv("TEST_DATABASE_URL")


@pytest.mark.skipif(not URL, reason="TEST_DATABASE_URL nicht gesetzt")
def test_postgres_upsert_and_view(raw_sample):
    engine = get_engine(URL)
    init_db(engine)
    init_db(engine)
    df = to_long(raw_sample)
    upsert(engine, df)
    upsert(engine, df)
    with engine.connect() as c:
        assert c.execute(text("SELECT COUNT(*) FROM energy_hourly")).scalar() == len(df)
        assert c.execute(text("SELECT COUNT(*) FROM v_energy_daily")).scalar() > 0
