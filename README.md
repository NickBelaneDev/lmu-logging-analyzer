# 🏎️ LMU Performance Toolkit

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](https://img.shields.io/badge/checked%20with-mypy-blue.svg)](https://mypy-lang.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A specialized toolkit for **Le Mans Ultimate (LMU)** to analyze performance logs and optimize hardware configurations. This project helps sim-racers identify micro-stutters, CPU bottlenecks, and incorrect Force Feedback (FFB) settings.

---

## ✨ Key Features

- **🔍 Deep Log Analysis**: Scans `trace.txt` for hardware specs, physics engine drops (throttling), and missing game assets.
- **⚙️ Smart Settings Debugger**: 
    - Automatically detects your LMU installation.
    - Creates backups of your `direct input.json`.
    - **Optimizes FFB**: Disables hidden FFB processing on non-wheel devices (pedals, shifters, etc.) to save CPU cycles and reduce stutters.
    - Fixes steering rotation issues.
- **📊 Performance Reporting**: Provides a clean summary of critical spikes and system health.
- **🚀 Standalone Mode**: Includes a PowerShell-based version for users who don't want to install Python.

---

## 📥 Easy Setup (Non-Python Users)

If you just want to fix your settings without dealing with Python code:

1. **Download the Tool**: [Click here to download the latest release](https://github.com/NickBelaneDev/lmu-toolset/releases/download/v1.0.0/lmu_auto_correct_ffb_settings.zip) 📦
2. **Unpack**: Extract the ZIP file to any folder.
3. **Run**: Double-click `run.bat`.
4. **Follow Instructions**: Select your wheelbase from the list, and the tool will handle the rest!

---

## 🚀 Developer Quick Start

### 1. Prerequisites
Ensure you have [uv](https://github.com/astral-sh/uv) installed.

### 2. Installation
```bash
git clone https://github.com/NickBelaneDev/lmu-toolset.git
cd lmu-toolset
uv sync
```

### 3. Usage

#### 📈 Run Log Analysis
Analyze your last session for errors and performance issues:
```bash
uv run python src/lmu_log_checker/main.py
```

#### 🔧 Interactive Settings Debugger
Fine-tune your `direct input.json` interactively:
```bash
uv run python src/lmu_settings_debug/main.py
```

---

## 📋 Example Analysis Report

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

[ERR_MAS_FILE_MISSING]: 2 occurrences
    -> Error opening MAS file "HUD\HUD.MAS"
```

---

## 🛠 Development

Maintain code quality with these commands:

| Command | Description |
| :--- | :--- |
| `make quality` | Run Ruff, Black, and Mypy checks |
| `make fix` | Automatically fix formatting and linting issues |

---
*Developed with ❤️ for the SimRacing Community.*
