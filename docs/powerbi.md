# Power-BI-Dashboard

Power BI Desktop ist kostenlos (Windows, Microsoft Store oder Microsoft-Website).

## Variante A: CSV (am schnellsten)

1. Pipeline mit Export ausführen: `python -m pipeline.main --weeks 8 --export data`
2. Power BI Desktop → *Daten abrufen* → *Text/CSV* → `data/daily_mix.csv`
3. Spalte `tag` als Datum, Zahlenspalten als Dezimalzahl prüfen.

## Variante B: direkt aus PostgreSQL

1. `docker compose up` muss laufen.
2. *Daten abrufen* → *PostgreSQL-Datenbank* → Server `localhost`, Datenbank `energie`.
3. Benutzer und Passwort aus deiner `.env`.
4. Tabelle `energy_hourly` und View `v_energy_daily` laden.

Falls Power BI beim Verbinden einen zusätzlichen Treiber verlangt, folge dem Hinweis im Dialog oder nimm Variante A.

## Vorschlag für die Seite

| Visual | Felder |
|---|---|
| Liniendiagramm | `tag` × `anteil_erneuerbar_pct` |
| Gestapeltes Flächendiagramm | `tag` × Wind, PV, Biomasse, Kohle, Gas |
| Karte (KPI) | Durchschnitt Anteil Erneuerbare, letzte 7 Tage |
| Liniendiagramm | `tag` × `netzlast` und `erneuerbar_mwh` |

Beispiel-Measure (DAX), wenn du mit `daily_mix` arbeitest:

```
Anteil Erneuerbar % =
DIVIDE ( SUM ( daily_mix[erneuerbar_mwh] ), SUM ( daily_mix[erzeugung_mwh] ) ) * 100
```

Datei als `docs/dashboard.pbix` speichern und einen Screenshot `docs/dashboard.png` ins README einbinden.
