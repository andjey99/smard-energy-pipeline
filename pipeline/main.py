"""Einstiegspunkt: python -m pipeline.main [--weeks 4] [--export data]"""

import argparse
import logging
from pathlib import Path

from pipeline import config
from pipeline.extract import extract
from pipeline.load import get_engine, init_db, upsert
from pipeline.transform import daily_mix, to_long

log = logging.getLogger("pipeline")


def run(weeks: int, export_dir: str | None) -> None:
    raw = extract(blocks=weeks)
    long_df = to_long(raw)
    log.info("Bereinigt: %d Zeilen", len(long_df))

    engine = get_engine(config.DATABASE_URL)
    init_db(engine)
    written = upsert(engine, long_df)
    log.info("In die Datenbank geschrieben: %d Zeilen (%s)", written, engine.dialect.name)

    mix = daily_mix(long_df)
    if not mix.empty:
        last = mix.dropna(subset=["anteil_erneuerbar_pct"]).tail(7)
        log.info("Anteil Erneuerbare, letzte 7 Tage:\n%s",
                 last[["tag", "anteil_erneuerbar_pct"]].to_string(index=False))

    if export_dir:
        out = Path(export_dir)
        out.mkdir(parents=True, exist_ok=True)
        long_df.to_csv(out / "energy_hourly.csv", index=False)
        mix.to_csv(out / "daily_mix.csv", index=False)
        log.info("CSV-Export nach %s", out.resolve())


def main() -> None:
    parser = argparse.ArgumentParser(description="SMARD-Energiedaten laden")
    parser.add_argument("--weeks", type=int, default=4, help="Anzahl Wochenblöcke (Standard 4)")
    parser.add_argument("--export", dest="export_dir", default=None, help="Ordner für CSV-Export")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    run(args.weeks, args.export_dir)


if __name__ == "__main__":
    main()
