# apploft Claude Skills

Geteilte Claude Code Skills für das apploft-Team.

---

## Was ist das hier?

Dieses Repository enthält Claude Code Skills, die ihr per Slash-Command in Claude Code aufrufen könnt.

Aktuell verfügbar:

| Skill | Befehl | Was er macht |
|-------|--------|--------------|
| Webscraper | `/run-webscraper` | Liest Tech-Artikel aus RSS-Feeds und schreibt sie ins Google Sheet |

---

## Einmalige Einrichtung (nur beim ersten Mal)

### 1. Repository klonen

```bash
git clone git@github.com:apploft/claude-skills.git
cd claude-skills
```

### 2. Installer ausführen

```bash
chmod +x install.sh
./install.sh
```

Das Script:
- kopiert das Python-Script nach `~/claude-skills/webscraper/`
- installiert den Skill in `~/.claude/commands/`
- installiert die nötigen Python-Pakete automatisch

### 3. credentials.json einfügen

Lege die `credentials.json` (Google OAuth) in diesen Ordner:

```
~/claude-skills/webscraper/credentials.json
```

> Die Datei bekommst du von Leonie Gerinter per privatem Kanal (niemals per E-Mail oder Chat mit sensiblen Daten).

### 4. Claude Code neu starten

Danach steht `/run-webscraper` in Claude Code zur Verfügung.

---

## Skill benutzen

Einfach in Claude Code eingeben:

```
/run-webscraper
```

Beim **ersten Start** öffnet sich ein Browser-Fenster → mit deinem Google-Konto anmelden → Zugriff erlauben.  
Ab dem zweiten Start läuft alles vollautomatisch.

Das Script legt beim ersten Mal automatisch ein neues Google Sheet an und gibt dir die URL.

---

## Updates installieren

Wenn neue Skills hinzukommen oder etwas geändert wurde:

```bash
git pull
./install.sh
```

Danach Claude Code neu starten.

---

## Wichtig: Keine API-Keys ins Repo

Lege API-Keys oder Zugangsdaten **niemals** in dieses Repository.  
Die `credentials.json` wird **nicht** eingecheckt (siehe `.gitignore`).

---


