# Energiemix Deutschland – Datenpipeline

Python-Pipeline, die öffentliche Strommarktdaten der Bundesnetzagentur (SMARD) abruft, bereinigt, in PostgreSQL speichert und für ein Power-BI-Dashboard bereitstellt. Läuft lokal mit Docker und optional täglich automatisch über GitHub Actions gegen eine Cloud-Datenbank.

**Leitfrage:** Wie hoch ist der Anteil erneuerbarer Energien an der Stromerzeugung in Deutschland, Tag für Tag, und wie verhält er sich zur Netzlast?

## Architektur

```
SMARD-API (JSON)
      │  extract.py   – Index + Wochenblöcke abrufen, Retries, Timeouts
      ▼
  transform.py        – bereinigen (fehlende Werte, Duplikate), UTC-Zeitstempel,
      │                 Tageswerte und Anteil Erneuerbare berechnen
      ▼
  load.py             – idempotenter Upsert in PostgreSQL (oder SQLite),
      │                 View v_energy_daily
      ▼
PostgreSQL ──► Power BI Dashboard        CSV-Export (data/) ──► Power BI
      ▲
GitHub Actions: CI (Tests gegen echtes PostgreSQL) + täglicher Abruf
```

## Daten

| Zeitreihe | SMARD-Filter |
|---|---|
| Netzlast (Gesamtverbrauch) | 410 |
| Wind Onshore / Offshore | 4067 / 1225 |
| Photovoltaik | 4068 |
| Biomasse / Wasserkraft | 4066 / 1226 |
| Braunkohle / Steinkohle / Erdgas | 1223 / 4069 / 4071 |

Werte in MWh, stündlich, Region Deutschland. „Anteil Erneuerbare" bezieht sich auf die hier erfassten Erzeugungsarten, nicht auf die gesamte Erzeugung.

Quelle: Bundesnetzagentur | SMARD.de. Bitte die Nutzungsbedingungen auf smard.de beachten.

## Schnellstart mit Docker

```powershell
copy .env.example .env      # danach in .env ein eigenes Passwort setzen
docker compose up --build
```

Die Pipeline lädt die letzten vier Wochen, schreibt sie in PostgreSQL (`localhost:5432`, Datenbank `energie`) und legt CSV-Dateien in `data/` ab.

## Ohne Docker

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
python -m pipeline.main --weeks 4 --export data
```

Ohne gesetzte `DATABASE_URL` wird eine lokale SQLite-Datei `energie.db` verwendet.

## Tests

```powershell
pytest -q
```

Die Unit-Tests laufen ohne Netzwerk mit Beispieldaten. Der Integrationstest gegen PostgreSQL läuft, wenn `TEST_DATABASE_URL` gesetzt ist, in der CI automatisch.

## Dashboard

Anleitung: [docs/powerbi.md](docs/powerbi.md). Screenshot folgt.

## Cloud (optional)

Anleitung für Azure Database for PostgreSQL und den täglichen Abruf per GitHub Actions: [docs/azure.md](docs/azure.md).

## Sicherheit

Zugangsdaten stehen nur in `.env` (lokal) bzw. in GitHub Secrets, nie im Code oder im Repository.

## Projektstruktur

```
pipeline/   config.py  extract.py  transform.py  load.py  main.py
tests/      Unit-Tests + PostgreSQL-Integrationstest
docs/       Power BI, Azure
.github/workflows/   ci.yml (Tests), refresh.yml (täglicher Abruf)
```

## Was ich dabei gelernt habe

<!-- Hier selbst in 3 bis 5 Sätzen ergänzen: was schwierig war, was du entschieden hast und warum. -->

## Nächste Schritte

- Großhandelspreise ergänzen und Zusammenhang zu Wind/PV auswerten
- Dashboard veröffentlichen und Screenshot einbinden
