"""Extract: Rohdaten von der SMARD-API holen."""

import logging

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from pipeline import config

log = logging.getLogger(__name__)


def make_session() -> requests.Session:
    """HTTP-Session mit Wiederholungen bei Netzwerk- und Serverfehlern."""
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=1, status_forcelist=(429, 500, 502, 503, 504))
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


def index_url(filter_id: int, region: str, resolution: str) -> str:
    return f"{config.SMARD_BASE_URL}/chart_data/{filter_id}/{region}/index_{resolution}.json"


def series_url(filter_id: int, region: str, resolution: str, timestamp_ms: int) -> str:
    # Die API verlangt Filter und Region doppelt im Pfad.
    return (
        f"{config.SMARD_BASE_URL}/chart_data/{filter_id}/{region}/"
        f"{filter_id}_{region}_{resolution}_{timestamp_ms}.json"
    )


def fetch_index(session, filter_id: int, region: str, resolution: str) -> list[int]:
    """Liefert die Startzeitpunkte (ms) aller verfügbaren Datenblöcke, aufsteigend."""
    resp = session.get(index_url(filter_id, region, resolution), timeout=config.HTTP_TIMEOUT_SECONDS)
    resp.raise_for_status()
    timestamps = [ts for ts in resp.json().get("timestamps", []) if ts is not None]
    return sorted(timestamps)


def fetch_series(session, filter_id: int, region: str, resolution: str, timestamp_ms: int) -> list:
    """Liefert eine Liste von [timestamp_ms, wert]-Paaren für einen Datenblock."""
    url = series_url(filter_id, region, resolution, timestamp_ms)
    resp = session.get(url, timeout=config.HTTP_TIMEOUT_SECONDS)
    resp.raise_for_status()
    return resp.json().get("series", [])


def extract(session=None, blocks: int = 4, region: str = None, resolution: str = None) -> dict:
    """Holt die letzten `blocks` Datenblöcke für alle konfigurierten Zeitreihen.

    Rückgabe: {serien_name: [[timestamp_ms, wert], ...]}
    """
    session = session or make_session()
    region = region or config.REGION
    resolution = resolution or config.RESOLUTION
    raw = {}
    for key, (filter_id, label, _) in config.SERIES.items():
        stamps = fetch_index(session, filter_id, region, resolution)[-blocks:]
        points = []
        for ts in stamps:
            points.extend(fetch_series(session, filter_id, region, resolution, ts))
        log.info("%s (%s): %d Werte aus %d Blöcken", key, label, len(points), len(stamps))
        raw[key] = points
    return raw
