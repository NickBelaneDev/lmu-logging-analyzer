import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union

from settings import settings

GAME_OPTIONS = "Game Options"
KEY_TELEMETRY = "Automatically Record Telemetry"
KEY_REPLAY = "Record Replays"

# Candidate filenames for the game-wide settings file (casing varies by install).
_SETTINGS_FILENAMES = ["Settings.JSON", "settings.json"]


class GameSettingsManager:
    """
    Manages LMU's game-wide ``Settings.JSON`` (distinct from ``direct input.json``).

    Used to toggle options that live flat under the ``"Game Options"`` section,
    such as replay and telemetry recording.
    """

    def __init__(self, file_path: Optional[Union[str, Path]] = None):
        """
        Initializes the manager.

        Args:
            file_path: Path to ``Settings.JSON``. If omitted, it is resolved as a
                sibling of the configured ``direct input.json``.
        """
        self.file_path = Path(file_path) if file_path else self._default_path()
        self.raw_data = self._read_json(self.file_path)

    def disable_replay_recording(self) -> None:
        """Disables replay (Wiederholung) recording."""
        self.set_game_option(KEY_REPLAY, False)

    def disable_telemetry_recording(self) -> None:
        """Disables automatic telemetry recording."""
        self.set_game_option(KEY_TELEMETRY, False)

    def set_game_option(self, key: str, value: Any) -> None:
        """
        Sets a single option under the ``"Game Options"`` section and persists it.

        Missing section or key are reported and skipped rather than raising, so a
        malformed/older Settings.JSON never aborts the run.

        Args:
            key: The option name within ``"Game Options"``.
            value: The value to assign.
        """
        game_options = self.raw_data.get(GAME_OPTIONS)
        if not isinstance(game_options, dict):
            print(f"  Section '{GAME_OPTIONS}' not found. Skipping '{key}'.")
            return
        if key not in game_options:
            print(f"  Option '{key}' not found in '{GAME_OPTIONS}'. Skipping.")
            return

        print(f"  Updating [{GAME_OPTIONS}][{key}]: {game_options[key]} -> {value}")
        game_options[key] = value
        self._write_json(self.file_path, self.raw_data)

    def create_backup(self) -> bool:
        """
        Creates a timestamped backup of ``Settings.JSON`` next to the original.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.file_path.with_suffix(f".bak_{timestamp}")
        shutil.copy2(self.file_path, backup_path)
        print(f"Backup created: {backup_path}")
        return True

    @staticmethod
    def _default_path() -> Path:
        """Resolves Settings.JSON as a sibling of the configured direct input file."""
        player_dir = settings.direct_input.parent
        for name in _SETTINGS_FILENAMES:
            candidate = player_dir / name
            if candidate.is_file():
                return candidate
        # Fall back to the canonical name; _read_json raises a clear error if missing.
        return player_dir / _SETTINGS_FILENAMES[0]

    @staticmethod
    def _read_json(file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Reads a JSON file and returns its content as a dictionary.
        """
        if not Path(file_path).exists():
            raise FileNotFoundError(f"The file {file_path} does not exist.")
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _write_json(file_path: Union[str, Path], data: Dict[str, Any]) -> None:
        """
        Writes a dictionary to a JSON file.
        """
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
