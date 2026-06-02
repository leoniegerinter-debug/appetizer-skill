#!/bin/bash
# ─────────────────────────────────────────────────────────────
# apploft Claude Skills – Installer
# Führe dieses Script einmalig aus, nachdem du das Repo geklont hast.
# ─────────────────────────────────────────────────────────────

set -e

SKILL_DIR="$HOME/claude-skills/webscraper"
CLAUDE_COMMANDS="$HOME/.claude/commands"

echo ""
echo "apploft Claude Skills – Installation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 1) Zielordner anlegen
mkdir -p "$SKILL_DIR"
mkdir -p "$CLAUDE_COMMANDS"

# 2) Python-Script kopieren
cp webscraper/webscraper_sheets.py "$SKILL_DIR/webscraper_sheets.py"
echo "  Script kopiert nach: $SKILL_DIR"

# 3) Skill-Datei für Claude Code installieren
cp webscraper/run-webscraper.md "$CLAUDE_COMMANDS/run-webscraper.md"
echo "  Skill installiert in: $CLAUDE_COMMANDS"

# 4) Python-Pakete installieren
echo ""
echo "  Python-Pakete werden installiert …"
pip install feedparser beautifulsoup4 google-api-python-client google-auth-oauthlib --quiet
echo "  Pakete OK"

# 5) Hinweis credentials.json
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "WICHTIG: credentials.json noch einfügen"
echo ""
echo "  Lege die credentials.json in diesen Ordner:"
echo "  $SKILL_DIR/credentials.json"
echo ""
echo "  (Die Datei bekommst du von Leonie oder erstellst sie"
echo "   selbst unter https://console.cloud.google.com/)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Fertig! Bitte Claude Code neu starten."
echo "Danach steht der Befehl /run-webscraper zur Verfügung."
echo ""
