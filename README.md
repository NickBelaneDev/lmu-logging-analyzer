# LMU Log Checker & Settings Tool

A Python-based toolset for analyzing Le Mans Ultimate (LMU) log files and managing game settings.

## Features

- **Log Analysis**: Detect hardware info, state changes, and errors in LMU log files using customizable regex patterns.
- **Settings Management**: Easily read and modify LMU configuration files (e.g., `DirectInput.json`).
- **CLI Interface**: Run analysis directly from your terminal.

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

1. Clone the repository.
2. Install dependencies and set up the virtual environment:
   ```sh
   uv sync
   ```

## Configuration

The tools rely on a `.env` file to locate your game files. Create a `.env` file in the root directory:

```env
TRACE_PATH="C:/Pfad/zu/deiner/Trace.txt"
DIRECT_INPUT="C:/Pfad/zu/deiner/DirectInput.json"
```

- `TRACE_PATH`: Path to your LMU `.txt` log file.
- `DIRECT_INPUT`: Path to your `direct input.json` file.

## Usage

### 1. Log Analysis
Analyzes the log file specified in your `.env` and provides a detailed report on hardware, performance issues (e.g., Physics drops), and missing assets.

```sh
uv run python src/lmu_log_checker/main.py
```

### 2. Settings Debugging
Currently used to disable the automatic steering wheel rotation detection ("Steering Wheel Maximum Rotation From Driver") for all connected devices to prevent permanent polling and errors from not detecting the device's steering wheel radius.

```sh
uv run python src/lmu_settings_debug/main.py
```

## Example Log Report Output
The tool provides structured feedback like:
- **System Info**: CPU and detected Input Devices.
- **Critical Performance**: Physics drops and FFB reductions.
- **Detected Issues**: Missing textures, deprecated physics parameters, and state changes.

## Development

Run quality checks:
```sh
make quality
```

Fix formatting issues:
```sh
make fix
```
