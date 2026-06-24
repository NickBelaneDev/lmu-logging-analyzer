# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

A toolkit for **Le Mans Ultimate (LMU)** sim racing. Two independent command-line tools share a common settings/path-resolution layer:

- **`lmu_log_checker`** — parses the game's `trace.txt` against a YAML ruleset to report hardware info, physics/FFB throttling spikes, and missing assets.
- **`lmu_settings_debug`** — interactively rewrites the game's `direct input.json` to disable FFB on non-wheel devices and fix the wheelbase config. A standalone PowerShell port (`src/lmu_settings_debug/auto_correct_ffb_settings.ps1` + `run.bat`) exists for non-Python users.

Package manager is **uv**; Python **3.11+**.

## Commands

```bash
uv sync                              # install deps (use --all-extras --dev to match CI)
uv run pytest                        # run all tests
uv run pytest tests/test_settings.py # run one test file
uv run pytest tests/test_lmu_settings_debug.py::test_create_backup_creates_file  # single test
make quality                         # ruff check + black --check + mypy src  (CI gate)
make fix                             # ruff --fix + black + mypy

uv run python src/lmu_log_checker/main.py      # run the log analyzer
uv run python src/lmu_settings_debug/main.py   # run the interactive settings debugger
```

CI (`.github/workflows/ci.yml`) runs the `quality` checks first, then `pytest`. `mypy` is only run against `src`, not `tests`.

## Architecture

**Source layout is `src/`-based** (`pyproject.toml` sets `pythonpath = ["src"]` for pytest). Imports are absolute from the `src` root, e.g. `from settings import settings`, `from lmu_log_checker.core.log_analyzer import LogAnalyzer`. The four top-level packages are `settings`, `_helper`, `lmu_log_checker`, `lmu_settings_debug`.

**Settings are a module-load-time singleton.** `src/settings/settings.py` runs `settings = get_settings()` at import time, so *importing the settings package validates configuration and can trigger interactive setup*. `Settings` (pydantic-settings `BaseSettings`) reads `TRACE_PATH` and `DIRECT_INPUT` from a `.env`. If they're missing/invalid, `get_settings()` calls `_helper.create_env.create_env()`, which:
1. Tries auto-detection via `_helper/resolve_game_path.py` (scans Steam libraries — `libraryfolders.vdf`, drive roots via `psutil` — for `Le Mans Ultimate`), then
2. Falls back to interactive prompts, and writes `.env`.

Because of this import-time side effect, **tests must inject env vars and reload the module**: see `_make_manager` in `tests/test_lmu_settings_debug.py`, which sets `TRACE_PATH`/`DIRECT_INPUT` via `monkeypatch`, then `importlib.reload(settings_pkg)` and the manager module. Follow this pattern when writing tests that touch settings.

**Log analyzer is rule-driven.** `lmu_log_checker/core/patterns.yaml` defines rules (id, category, regex `pattern`, optional `trigger_file`, `solution`). `LogAnalyzer` (`core/log_analyzer.py`) splits each line with a fixed `LOG_PATTERN`, then runs the per-rule compiled regexes; the **first** matching rule per line wins (`break`). Models (`LogLine`, `AnalysisRule`, `AnalysisEvent`) are pydantic in `core/models.py`. `main.py` aggregates events into the printed report. To add a detection, add a rule to `patterns.yaml` — no code change needed.

**Settings debugger applies JSON payloads.** `DeviceControlManager` (`lmu_settings_debug/core/manager.py`) loads device config from `direct input.json` and default payloads from `src/lmu_settings_debug/direct_input_config.json` (`periphery_defaults` / `wheelbase_defaults`). Payloads are `{category: {key: value}}` and are applied per-device into matching categories (e.g. `options`, `Force Feedback`). `create_backup()` copies the file to a timestamped `.bak_*` before changes. Always create a backup before mutating `direct input.json`.
