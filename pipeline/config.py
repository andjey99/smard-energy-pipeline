"""Zentrale Konfiguration: Datenquelle, Zeitreihen und Datenbankverbindung."""

import os

# Öffentliche SMARD-API der Bundesnetzagentur (keine Anmeldung nötig).
# Alternativ: https://smard.api.proxy.bund.dev/app
SMARD_BASE_URL = os.getenv("SMARD_BASE_URL", "https://www.smard.de/app")

REGION = os.getenv("SMARD_REGION", "DE")
RESOLUTION = os.getenv("SMARD_RESOLUTION", "hour")

# Filter-IDs laut SMARD-API-Dokumentation (bundesAPI/smard-api).
# key: eigener, kurzer Name -> (Filter-ID, Beschreibung, erneuerbar?)
SERIES = {
    "netzlast": (410, "Stromverbrauch: Gesamt (Netzlast)", None),
    "wind_onshore": (4067, "Stromerzeugung: Wind Onshore", True),
    "wind_offshore": (1225, "Stromerzeugung: Wind Offshore", True),
    "photovoltaik": (4068, "Stromerzeugung: Photovoltaik", True),
    "biomasse": (4066, "Stromerzeugung: Biomasse", True),
    "wasserkraft": (1226, "Stromerzeugung: Wasserkraft", True),
    "braunkohle": (1223, "Stromerzeugung: Braunkohle", False),
    "steinkohle": (4069, "Stromerzeugung: Steinkohle", False),
    "erdgas": (4071, "Stromerzeugung: Erdgas", False),
}

RENEWABLE_KEYS = [k for k, (_, _, ren) in SERIES.items() if ren is True]
GENERATION_KEYS = [k for k, (_, _, ren) in SERIES.items() if ren is not None]

# Datenbank: Zugangsdaten kommen aus der Umgebung (.env), nie aus dem Code.
# Für Tests und schnelle Versuche ohne Docker: sqlite:///energie.db
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///energie.db")

HTTP_TIMEOUT_SECONDS = 20
