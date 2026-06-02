#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║              appetizer Webscraper → Google Sheets                           ║
║  Liest aktuelle Tech-Artikel aus RSS-Feeds und schreibt sie ins Google Sheet║
╚══════════════════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EINMALIGE EINRICHTUNG (nur beim ersten Mal)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1) Python-Pakete installieren
   Öffne das Terminal und führe aus:

       pip install feedparser beautifulsoup4 google-api-python-client google-auth-oauthlib

2) Google-Zugangsdaten holen
   a) Gehe zu https://console.cloud.google.com/
   b) Neues Projekt erstellen (oder bestehendes wählen)
   c) APIs & Dienste → Bibliothek → "Google Sheets API" aktivieren
   d) APIs & Dienste → Anmeldedaten → "+ Anmeldedaten erstellen" → OAuth-Client-ID
   e) Anwendungstyp: "Desktop-App" → Erstellen
   f) JSON herunterladen → Datei umbenennen in: credentials.json
   g) credentials.json in denselben Ordner legen wie dieses Script

   ODER: Lass dir die credentials.json von der Person schicken,
         die dieses Script erstellt hat, und lege sie in denselben Ordner.

3) Script starten
   Im Terminal:

       python webscraper_sheets.py

   Beim ersten Start öffnet sich ein Browser-Fenster → mit Google-Konto anmelden
   → Zugriff erlauben. Danach läuft das Script vollautomatisch.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WAS DAS SCRIPT MACHT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Liest 9 Tech-RSS-Feeds (TechCrunch, The Verge, t3n, Heise, ...)
- Filtert Artikel der letzten 7 Tage nach App/Mobile/KI-Relevanz
- Schreibt neue Artikel ins Google Sheet (Duplikate werden übersprungen)
- Das Sheet wird beim ersten Start automatisch angelegt
"""

import os
import sys
import json
import pickle
import time
from pathlib import Path
from datetime import datetime, timedelta, timezone

# ── Abhängigkeiten prüfen ──────────────────────────────────────────────────────
FEHLENDE_PAKETE = []
try:
    import feedparser
except ImportError:
    FEHLENDE_PAKETE.append("feedparser")
try:
    from bs4 import BeautifulSoup
except ImportError:
    FEHLENDE_PAKETE.append("beautifulsoup4")
try:
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
except ImportError:
    FEHLENDE_PAKETE.append("google-api-python-client")
try:
    from google_auth_oauthlib.flow import InstalledAppFlow
except ImportError:
    FEHLENDE_PAKETE.append("google-auth-oauthlib")

if FEHLENDE_PAKETE:
    print("━" * 60)
    print("FEHLER: Fehlende Python-Pakete. Bitte im Terminal ausführen:")
    print()
    print(f"    pip install {' '.join(FEHLENDE_PAKETE)}")
    print()
    print("Danach dieses Script erneut starten.")
    print("━" * 60)
    sys.exit(1)

# ── Pfade (relativ zum Script-Ordner — funktioniert auf jedem Laptop) ──────────
SCRIPT_DIR    = Path(__file__).parent
CREDENTIALS   = SCRIPT_DIR / "credentials.json"
TOKEN_PICKLE  = SCRIPT_DIR / "token_sheets.pickle"
SHEET_ID_FILE = SCRIPT_DIR / "sheet_id.json"

LOOKBACK_DAYS = 7
SHEETS_SCOPE  = ["https://www.googleapis.com/auth/spreadsheets"]

# ── RSS-Quellen ────────────────────────────────────────────────────────────────
RSS_FEEDS = [
    ("TechCrunch",        "https://techcrunch.com/feed/"),
    ("The Verge",         "https://www.theverge.com/rss/index.xml"),
    ("9to5Mac",           "https://9to5mac.com/feed/"),
    ("Android Authority", "https://androidauthority.com/feed/"),
    ("AppleInsider",      "https://appleinsider.com/rss/news/"),
    ("MacRumors",         "https://feeds.macrumors.com/MacRumors-All"),
    ("t3n",               "https://t3n.de/rss.xml"),
    ("Heise",             "https://www.heise.de/rss/heise.rdf"),
    ("Mobilbranche",      "https://mobilbranche.de/feed/"),
]

RELEVANCE_KEYWORDS = [
    "app", "mobile", "ios", "android", "iphone", "smartphone", "play store",
    "app store", "ki ", "ai ", "artificial intelligence", "ux", "user experience",
    "developer", "sdk", "api", "subscription", "monetization", "monetarisierung",
    "app-entwicklung", "digital", "platform", "google", "apple", "meta",
    "samsung", "openai", "gemini", "llm", "generative", "künstliche intelligenz",
]


# ── Schritt 1: RSS fetchen ─────────────────────────────────────────────────────
def fetch_articles() -> list:
    seit    = datetime.now(tz=timezone.utc) - timedelta(days=LOOKBACK_DAYS)
    artikel = []
    gesehen = set()

    for quelle, url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            neu  = 0
            for entry in feed.entries:
                ts = getattr(entry, "published_parsed", None) or getattr(entry, "updated_parsed", None)
                if ts:
                    dt = datetime.fromtimestamp(time.mktime(ts), tz=timezone.utc)
                    if dt < seit:
                        continue
                    datum_str = dt.strftime("%d.%m.%Y")
                else:
                    datum_str = datetime.now().strftime("%d.%m.%Y")

                link  = getattr(entry, "link", "").strip()
                titel = getattr(entry, "title", "").strip()
                if not titel or not link or link in gesehen:
                    continue

                summary = getattr(entry, "summary", "") or getattr(entry, "description", "") or ""
                inhalt  = BeautifulSoup(summary, "html.parser").get_text(" ", strip=True)[:600]
                check   = (titel + " " + inhalt).lower()
                if not any(kw in check for kw in RELEVANCE_KEYWORDS):
                    continue

                gesehen.add(link)
                artikel.append({
                    "titel":     titel,
                    "quelle":    quelle,
                    "link":      link,
                    "inhalt":    inhalt,
                    "datum_str": datum_str,
                })
                neu += 1
            print(f"  {quelle}: {neu} Artikel")
        except Exception as e:
            print(f"  Warnung {quelle}: {e}")

    return artikel


# ── Schritt 2: Artikel für Sheet vorbereiten ──────────────────────────────────
def bereite_vor(artikel: list) -> list:
    return [
        {
            "datum":           art["datum_str"],
            "quelle":          art["quelle"],
            "kategorie":       "",
            "titel":           art["titel"],
            "zusammenfassung": art["inhalt"],
            "link":            art["link"],
        }
        for art in artikel
    ]


# ── Schritt 3: Google Sheets ───────────────────────────────────────────────────
def _sheets_service():
    if not CREDENTIALS.exists():
        print("━" * 60)
        print("FEHLER: credentials.json nicht gefunden!")
        print()
        print("Bitte die credentials.json in denselben Ordner legen wie dieses Script:")
        print(f"  {SCRIPT_DIR}")
        print()
        print("Anleitung zum Erstellen steht ganz oben in dieser Datei.")
        print("━" * 60)
        sys.exit(1)

    creds = None
    if TOKEN_PICKLE.exists():
        with open(TOKEN_PICKLE, "rb") as fh:
            creds = pickle.load(fh)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print()
            print("  → Browser öffnet sich zur Google-Anmeldung …")
            print("  → Bitte mit deinem Google-Konto anmelden und Zugriff erlauben.")
            print()
            flow  = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS), SHEETS_SCOPE)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PICKLE, "wb") as fh:
            pickle.dump(creds, fh)
    return build("sheets", "v4", credentials=creds)


def _get_or_create_sheet(service) -> str:
    if SHEET_ID_FILE.exists():
        gespeichert = json.loads(SHEET_ID_FILE.read_text())
        sheet_id    = gespeichert.get("sheet_id", "")
        if sheet_id:
            return sheet_id

    spreadsheet = {
        "properties": {"title": "appetizer – Artikel-Übersicht"},
        "sheets": [{"properties": {"title": "Artikel"}}],
    }
    result   = service.spreadsheets().create(body=spreadsheet).execute()
    sheet_id = result["spreadsheetId"]
    grid_id  = result["sheets"][0]["properties"]["sheetId"]

    SHEET_ID_FILE.write_text(json.dumps({"sheet_id": sheet_id}, indent=2))

    service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range="Artikel!A1:F1",
        valueInputOption="RAW",
        body={"values": [["Datum", "Quelle", "Kategorie", "Titel", "Zusammenfassung (DE)", "Link"]]},
    ).execute()

    requests = [
        {"updateDimensionProperties": {
            "range": {"sheetId": grid_id, "dimension": "COLUMNS", "startIndex": i, "endIndex": i + 1},
            "properties": {"pixelSize": w},
            "fields": "pixelSize",
        }}
        for i, w in enumerate([90, 130, 130, 280, 420, 320])
    ]
    try:
        service.spreadsheets().batchUpdate(
            spreadsheetId=sheet_id, body={"requests": requests}
        ).execute()
    except Exception:
        pass

    print(f"  Neues Sheet angelegt: https://docs.google.com/spreadsheets/d/{sheet_id}")
    return sheet_id


def schreibe_in_sheets(artikel: list) -> str:
    service  = _sheets_service()
    sheet_id = _get_or_create_sheet(service)

    result         = service.spreadsheets().values().get(
        spreadsheetId=sheet_id, range="Artikel!F:F"
    ).execute()
    existing_links = {row[0] for row in result.get("values", []) if row}

    neue_zeilen = [
        [art["datum"], art["quelle"], art["kategorie"],
         art["titel"], art["zusammenfassung"], art["link"]]
        for art in artikel
        if art["link"] not in existing_links
    ]

    if not neue_zeilen:
        print("  Keine neuen Artikel – alle bereits im Sheet.")
        return sheet_id

    service.spreadsheets().values().append(
        spreadsheetId=sheet_id,
        range="Artikel!A:F",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": neue_zeilen},
    ).execute()

    print(f"  {len(neue_zeilen)} neue Zeilen geschrieben.")
    return sheet_id


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    print("appetizer Webscraper → Google Sheets")
    print("━" * 40)

    print("\nRSS-Feeds fetchen …")
    artikel = fetch_articles()
    if not artikel:
        print("Keine relevanten Artikel gefunden.")
        return
    print(f"\n  Gesamt: {len(artikel)} Artikel")

    analysiert = bereite_vor(artikel)

    print("\nIn Google Sheets schreiben …")
    sheet_id = schreibe_in_sheets(analysiert)

    print(f"\nFertig!")
    print(f"Sheet: https://docs.google.com/spreadsheets/d/{sheet_id}")


if __name__ == "__main__":
    main()
