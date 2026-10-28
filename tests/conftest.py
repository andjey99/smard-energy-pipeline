import pytest

# Feste Beispielzeitpunkte (UTC): 2026-10-19 00:00, 01:00, 02:00
T0 = 1792368000000
H = 3_600_000


@pytest.fixture
def raw_sample():
    return {
        "netzlast": [[T0, 50000.0], [T0 + H, 48000.0], [T0 + 2 * H, None]],
        "wind_onshore": [[T0, 10000.0], [T0 + H, 12000.0]],
        "photovoltaik": [[T0, 0.0], [T0 + H, 0.0]],
        "braunkohle": [[T0, 8000.0], [T0 + H, 8000.0]],
        "erdgas": [[T0, 2000.0], [T0 + H, 0.0], [None, 5.0]],
    }
