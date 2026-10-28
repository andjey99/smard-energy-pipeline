from pipeline import config
from pipeline.extract import extract, index_url, series_url


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self.payload


class FakeSession:
    def __init__(self):
        self.urls = []

    def get(self, url, timeout):
        self.urls.append(url)
        if url.endswith("index_hour.json"):
            return FakeResponse({"timestamps": [3000, 1000, None, 2000]})
        ts = int(url.rsplit("_", 1)[1].removesuffix(".json"))
        return FakeResponse({"series": [[ts, 1.0], [ts + 1, None]]})


def test_url_patterns():
    assert index_url(410, "DE", "hour") == f"{config.SMARD_BASE_URL}/chart_data/410/DE/index_hour.json"
    assert series_url(410, "DE", "hour", 123).endswith("/chart_data/410/DE/410_DE_hour_123.json")


def test_extract_takes_latest_blocks():
    session = FakeSession()
    raw = extract(session=session, blocks=2, region="DE", resolution="hour")
    assert set(raw) == set(config.SERIES)
    # pro Serie: neueste zwei Blöcke (2000, 3000), je 2 Punkte
    assert [p[0] for p in raw["netzlast"]] == [2000, 2001, 3000, 3001]
    assert not any(u.endswith("_1000.json") for u in session.urls)
