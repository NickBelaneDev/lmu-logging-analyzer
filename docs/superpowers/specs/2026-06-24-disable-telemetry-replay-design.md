# Design: Telemetrie- & Wiederholungsaufzeichnung abschaltbar machen

**Datum:** 2026-06-24
**Status:** Approved

## Ziel

Der Settings-Debugger soll den Nutzer fragen, ob er die **Telemetrie-Aufzeichnung** und die **Wiederholungsaufzeichnung (Replay)** ausschalten will. Letztere verursacht in der Praxis spürbare Ruckler. Die Funktion muss in **beiden** Varianten existieren:

1. Das Python-Tool (`src/lmu_settings_debug/main.py`)
2. Das PowerShell-Standalone-Skript (`src/lmu_settings_debug/auto_correct_ffb_settings.ps1`)

## Datenlage

Die beiden Schalter liegen **nicht** in `direct input.json`, sondern flach unter der Top-Level-Sektion `"Game Options"` in `Settings.JSON` (gleicher Ordner: `UserData/player/`):

| JSON-Key (in `"Game Options"`) | Bedeutung | Ausschalten = |
|---|---|---|
| `"Automatically Record Telemetry"` | Telemetrie-Aufzeichnung | `false` |
| `"Record Replays"` | Wiederholungsaufzeichnung | `false` |

## Architektur (Option A)

`Settings.JSON` hat eine andere Struktur als `direct input.json` (flache Keys unter Sektionen statt pro Gerät). Der bestehende `DeviceControlManager` ist fest auf `direct input.json` / `Devices` ausgelegt und wird **nicht** erweitert. Stattdessen: eine neue, isolierte Klasse.

### Python-Komponente: `GameSettingsManager`

Neue Datei: `src/lmu_settings_debug/core/game_settings.py`

Modul-Konstanten:
- `GAME_OPTIONS = "Game Options"`
- `KEY_TELEMETRY = "Automatically Record Telemetry"`
- `KEY_REPLAY = "Record Replays"`

Klasse `GameSettingsManager`:
- `__init__(file_path: Optional[Union[str, Path]] = None)`
  - Default-Pfad: Geschwister-Datei von `settings.direct_input`, d. h. `settings.direct_input.parent`, dort den ersten existierenden Kandidaten aus `["Settings.JSON", "settings.json"]` wählen (Casing-Robustheit).
  - Liest die JSON-Datei via `_read_json`. Existiert die Datei nicht → `FileNotFoundError` (der aufrufende Flow fängt das ab und überspringt den Abschnitt).
- `set_game_option(key: str, value: Any) -> None`
  - Setzt `data[GAME_OPTIONS][key] = value` und schreibt via `_write_json` zurück.
  - Fehlt die Sektion `"Game Options"` oder der Key → Warnung ausgeben (`print`), **nicht** abbrechen.
- `disable_telemetry_recording() -> None` → `set_game_option(KEY_TELEMETRY, False)`
- `disable_replay_recording() -> None` → `set_game_option(KEY_REPLAY, False)`
- `create_backup() -> bool`
  - Timestamped Kopie `Settings.bak_<YYYYMMDD_HHMMSS>` (gleiche Mechanik wie `DeviceControlManager.create_backup`, eigene Sicherung getrennt von `direct input.json`).
- statische Helfer `_read_json` / `_write_json` (gleicher Stil/`indent=2` wie `DeviceControlManager`).

**Pfad-Begründung:** Ableitung aus `settings.direct_input.parent` vermeidet ein neues Pflichtfeld in `Settings`/`.env`. Bestehende Nutzer müssen ihre `.env` nicht neu einrichten.

### Interaktiver Flow (`main.py`)

Neuer Abschnitt **nach** dem Geräte-Update (`apply_to_all`) und **vor** der Abschluss-Glückwunsch-Meldung:

1. Überschrift „--- Game Options ---".
2. `GameSettingsManager` instanziieren in `try/except FileNotFoundError`: wird `Settings.JSON` nicht gefunden → freundliche Meldung, Abschnitt überspringen, Tool läuft normal weiter.
3. Frage 1 (**Replay zuerst**, mit Hinweis, dass das oft Ruckler verursacht): „Wiederholungsaufzeichnung ausschalten? (y/n)".
4. Frage 2: „Automatische Telemetrie-Aufzeichnung ausschalten? (y/n)".
5. Wird mindestens eine Frage mit „y" beantwortet: **einmalig** `create_backup()` von `Settings.JSON`, danach die gewählten `disable_*`-Methoden aufrufen.

### PowerShell-Komponente (`auto_correct_ffb_settings.ps1`)

Neuer Abschnitt **nach** dem Speichern von `direct input.json` (nach aktueller Zeile 68):

- Pfad: `$gameSettingsPath = Join-Path $gameRoot "UserData\player\Settings.JSON"` (nutzt vorhandenes `$gameRoot`).
- Validierung: existiert die Datei nicht → `Write-Warning` + Abschnitt überspringen (Skript läuft sauber zu Ende, inkl. `Pause`).
- Zwei `Read-Host` y/n-Abfragen, **Replay zuerst** mit Ruckler-Hinweis — gleiche Reihenfolge und gleicher Wortlaut wie im Python-Tool.
- Backup beim ersten „y": `Copy-Item $gameSettingsPath "$gameSettingsPath.bak_$timestamp"` (eigene Sicherung, getrennt von der FFB-Sicherung; `$timestamp` analog vorhandenem Muster neu bilden).
- Setzen nur bei existierendem Key:
  - `$gameSettings.'Game Options'.'Record Replays' = $false`
  - `$gameSettings.'Game Options'.'Automatically Record Telemetry' = $false`
- Speichern: `$gameSettings | ConvertTo-Json -Depth 50 | Set-Content $gameSettingsPath`.
  - ⚠️ **`-Depth 50`** ist Pflicht: `Settings.JSON` ist deutlich tiefer verschachtelt als `direct input.json`; bei zu niedriger Tiefe schneidet `ConvertTo-Json` verschachtelte Objekte ab und zerstört die Datei. Encoding/`Set-Content`-Aufruf wie im bestehenden, funktionierenden FFB-Teil (Konsistenz).

## Fehlerbehandlung

- `Settings.JSON` fehlt → Meldung ausgeben, Abschnitt überspringen, restliches Tool/Skript läuft normal weiter.
- Sektion `"Game Options"` oder einzelner Key fehlt → pro Key warnen, nicht abbrechen.

## Parität (Python ↔ PowerShell)

Beide Implementierungen müssen synchron bleiben:
- dieselben zwei Keys (`KEY_TELEMETRY`, `KEY_REPLAY`),
- dieselbe Frage-Reihenfolge (Replay zuerst),
- derselbe Wortlaut inkl. Ruckler-Hinweis.

## Tests

Neue Datei `tests/test_game_settings.py`, gleiches Muster wie `tests/test_lmu_settings_debug.py`
(monkeypatch `TRACE_PATH`/`DIRECT_INPUT`, `importlib.reload` von `settings` und Manager-Modul, temporäre `Settings.JSON` mit `"Game Options"`-Sektion):

1. `disable_replay_recording()` setzt `"Record Replays"` auf `false` und persistiert.
2. `disable_telemetry_recording()` setzt `"Automatically Record Telemetry"` auf `false` und persistiert.
3. `set_game_option` mit fehlender Sektion/fehlendem Key crasht nicht (nur Warnung).
4. `create_backup()` legt eine `Settings.bak_*`-Datei an und gibt `True` zurück.

Das PowerShell-Skript wird nicht automatisiert getestet (kein bestehendes Test-Harness dafür); manuelle Verifikation gegen eine Kopie der `Settings.JSON`.

## Bewusst ausgeschlossen (YAGNI)

- Kein neues `.env`-Feld / kein Resolver für `Settings.JSON` (Pfad wird abgeleitet).
- Keine Externalisierung der Keys in eine Config-Datei (zwei feste Schalter genügen, als Konstanten).
- Keine generische „beliebige Game Option setzen"-UI; nur die zwei konkreten Schalter werden im Flow angeboten (`set_game_option` bleibt aber generisch als interne Basis).
