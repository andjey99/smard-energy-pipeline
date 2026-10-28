# Optional: Cloud-Datenbank auf Azure + täglicher Abruf

Ziel: Die Daten liegen in einer PostgreSQL-Datenbank in Azure, und GitHub Actions aktualisiert sie jeden Tag.

## Kosten zuerst

Prüfe vorher die aktuellen Bedingungen von „Azure for Students" bzw. dem kostenlosen Azure-Konto auf der Microsoft-Seite. Wähle die kleinste Serverstufe und **lösche die Ressourcen**, wenn du sie nicht mehr brauchst.

## Schritte

1. Im Azure-Portal: *Azure Database for PostgreSQL – Flexible Server* anlegen (kleinste Stufe, Region Westeuropa oder Deutschland).
2. Administratorname und ein starkes Passwort festlegen (nirgends im Code speichern).
3. Unter *Netzwerk* den Zugriff erlauben: deine eigene IP für Tests. Für GitHub Actions musst du den Zugriff aus dem Internet zulassen und bist dann auf ein starkes Passwort und SSL angewiesen. Das ist für ein Lernprojekt vertretbar, aber nicht für Produktivdaten.
4. Datenbank `energie` anlegen.
5. Verbindungs-URL bauen:
   `postgresql+psycopg2://BENUTZER:PASSWORT@SERVERNAME.postgres.database.azure.com:5432/energie?sslmode=require`
6. Lokal testen: `DATABASE_URL` in der Shell setzen und `python -m pipeline.main --weeks 2` ausführen.
7. In GitHub: *Settings → Secrets and variables → Actions → New repository secret*, Name `DATABASE_URL`, Wert = URL aus Schritt 5.
8. Unter *Actions* den Workflow „Daten aktualisieren" manuell starten. Danach läuft er täglich.

Power BI kann sich anschließend direkt mit dem Azure-Server verbinden (Variante B in `powerbi.md`, Server = Azure-Hostname).
