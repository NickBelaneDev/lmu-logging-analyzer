from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Iterable, List

import psutil


def resolve_path() -> Path:
    game_root = _resolve_game_root()
    if game_root is None:
        raise FileNotFoundError(
            "Could not locate 'Le Mans Ultimate' in any Steam library. "
            "Set TRACE_PATH or DIRECT_INPUT in .env if auto-detection fails."
        )
    return game_root


def resolve_trace_path() -> Path:
    game_root = resolve_path()
    candidates = [
        game_root / "UserData" / "Log" / "trace.txt",
        game_root / "UserData" / "Log" / "Trace.txt",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate

    log_dir = game_root / "UserData" / "Log"
    if log_dir.is_dir():
        matches = sorted(
            log_dir.glob("trace*.txt"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if matches:
            return matches[0]

    raise FileNotFoundError(
        f"Could not locate trace file under {game_root}. "
        "Expected UserData/Log/trace.txt or a trace*.txt file.\n"
        "Make sure, that your trace.txt exists or add its path to .env."
    )


def resolve_direct_input_path() -> Path:
    game_root = resolve_path()
    candidates = [
        game_root / "UserData" / "player" / "direct input.json",
        game_root / "UserData" / "player" / "DirectInput.json",
        game_root / "UserData" / "player" / "direct_input.json",
        game_root / "UserData" / "player" / "Direct Input.json",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate

    raise FileNotFoundError(
        f"Could not locate direct input file under {game_root}. "
        "Expected UserData/player/direct input.json.\n"
        "Make sure, that your direct_input.json exists or add its path to .env."
    )


def _resolve_game_root() -> Path | None:
    for library_path in _iter_library_paths():
        game_dir = library_path / "steamapps" / "common" / "Le Mans Ultimate"
        if game_dir.is_dir():
            return game_dir
    return None


def _iter_library_paths() -> Iterable[Path]:
    candidates: List[Path] = []

    for steam_root in _iter_candidate_steam_roots():
        candidates.append(steam_root)
        candidates.extend(_read_library_paths(steam_root))

    for root in _iter_drive_roots():
        for name in ["SteamLibrary", "Steam", "Games"]:
            candidates.append(root / name)

    return _unique_paths(candidates)


def _iter_candidate_steam_roots() -> Iterable[Path]:
    roots: List[Path] = []
    env_pf86 = os.environ.get("PROGRAMFILES(X86)")
    env_pf = os.environ.get("PROGRAMFILES")

    if env_pf86:
        roots.append(Path(env_pf86) / "Steam")
    if env_pf:
        roots.append(Path(env_pf) / "Steam")

    roots.append(Path("C:/Steam"))

    for drive_root in _iter_drive_roots():
        roots.append(drive_root / "Steam")
        roots.append(drive_root / "Program Files (x86)" / "Steam")
        roots.append(drive_root / "Program Files" / "Steam")

    return _unique_paths(roots)


def _iter_drive_roots() -> Iterable[Path]:
    for partition in psutil.disk_partitions():
        yield Path(partition.mountpoint)


_VDF_PATH_RE = re.compile(r'"path"\s+"([^"]+)"', re.IGNORECASE)
_VDF_NUMERIC_RE = re.compile(r'"\d+"\s+"([^"]+)"')


def _read_library_paths(steam_root: Path) -> List[Path]:
    library_file = steam_root / "steamapps" / "libraryfolders.vdf"
    if not library_file.is_file():
        return []

    text = library_file.read_text(encoding="utf-8", errors="ignore")
    paths: List[Path] = []
    for line in text.splitlines():
        match = _VDF_PATH_RE.search(line) or _VDF_NUMERIC_RE.search(line)
        if not match:
            continue
        raw = match.group(1).replace("\\\\", "\\")
        if raw:
            paths.append(Path(raw))
    return paths


def _unique_paths(paths: Iterable[Path]) -> List[Path]:
    seen = set()
    unique: List[Path] = []
    for path in paths:
        key = str(path).lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(path)
    return unique


if __name__ == "__main__":
    print(resolve_direct_input_path())
