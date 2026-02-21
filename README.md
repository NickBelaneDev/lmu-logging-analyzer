# 🏎️ LMU Log Checker & Settings Tool

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](http://www.mypy-lang.org/static/badge.svg)](http://mypy-lang.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A performance toolkit for **Le Mans Ultimate (LMU)** enthusiasts and developers to analyze the ingame logs (trace.txt) and fine-tune hardware settings.

---

## ✨ Key Features

- **🔍 Deep Log Analysis**: Automatically scans LMU trace files for hardware specs, physics drops, and missing assets.
- **⚙️ Hardware Optimization**: Programmatically adjust `direct input.json` settings (e.g., fixing steering rotation issues).
- **📊 Structured Reporting**: Get a clean, categorized overview of critical performance spikes and game state transitions.
- **⚡ Powered by `uv`**: Ultra-fast dependency management and execution.

---

## 🚀 Quick Start

### 1. Prerequisites
Ensure you have [uv](https://github.com/astral-sh/uv) installed.

### 2. Installation
```bash
git clone https://github.com/NickBelaneDev/lmu-toolset.git
cd lmu-toolset
uv sync
```

### 3. Configuration
Create a `.env` file in the root directory to point to your LMU files:

---

## 🛠️ Usage

### 📈 Run Log Analysis
Get a detailed report on your last session, including physics performance and errors.
```bash
uv run python src/lmu_log_checker/main.py
```

### 🔧 Fix Steering Settings
Automatically disable "Steering Wheel Maximum Rotation From Driver" for all devices to prevent calibration issues.
```bash
uv run python src/lmu_settings_debug/main.py
```

---

## 📋 Example Report Output

```text
========================================
       LMU LOG ANALYSIS REPORT       
========================================

--- SYSTEM INFO ---
CPU: 12th Gen Intel(R) Core(TM) i5-12400F (12 cores)
Input Devices (4 found):
  - Simucube 2 Pro
  - VRS DirectForce Pro Pedals
  ...

!!! CRITICAL PERFORMANCE ISSUES (1x) !!!
  - At 134.79s: Physics dropped to 5.39Hz (FFB reduced by 1.34%)

[ERR_TEXTURE_MISSING]: 66 occurrences
    -> $DEPTH RT $RAINDROPMAP
    ...
```

---

## 🛠 Development

Maintain code quality with these simple commands:

| Command | Description |
| :--- | :--- |
| `make quality` | Run Ruff, Black, and Mypy checks |
| `make fix` | Automatically fix formatting and linting issues |

---
*Developed with ❤️ for the SimRacing Community.*
