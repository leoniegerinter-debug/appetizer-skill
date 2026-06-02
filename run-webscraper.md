---
description: Tech-RSS-Feeds scrapen und Artikel in Google Sheets schreiben
allowed-tools: Bash, Read
---

Führe den Webscraper aus: liest aktuelle Tech-Artikel aus 9 RSS-Feeds (letzte 7 Tage) und schreibt neue Einträge ins Google Sheet.

## Schritt 1 — Script ausführen

```bash
python ~/claude-skills/webscraper/webscraper_sheets.py
```

Beim ersten Start öffnet sich ein Browser-Fenster für die Google-Anmeldung.
Danach läuft es vollautomatisch ohne weitere Eingabe.

## Schritt 2 — Ergebnis melden

Berichte dem Nutzer:
- Wie viele Artikel gefunden wurden (aufgeteilt nach Quelle)
- Wie viele neue Zeilen ins Sheet geschrieben wurden
- Die direkte Sheet-URL aus dem Script-Output

Bei Fehler: zeige die relevante Fehlerzeile und schlage eine Lösung vor.
