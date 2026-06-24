import importlib
import json
from pathlib import Path


def _write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data))


def _settings_payload() -> dict:
    return {
        "Game Options": {
            "Record Replays": True,
            "Automatically Record Telemetry": True,
            "Some Other Option": 42,
        },
        "Graphic Options": {
            "Whatever": 1,
        },
    }


def _make_manager(tmp_path: Path, monkeypatch, settings_data=None, file_path=None):
    """Builds a GameSettingsManager against a temp Settings.JSON.

    Mirrors the env-reload pattern used in test_lmu_settings_debug so importing
    the settings package does not trigger interactive setup.
    """
    trace_path = tmp_path / "trace.txt"
    trace_path.write_text("trace")
    direct_input_path = tmp_path / "direct_input.json"
    _write_json(direct_input_path, {"Devices": {}})

    settings_json_path = tmp_path / "Settings.JSON"
    if settings_data is not None:
        _write_json(settings_json_path, settings_data)

    monkeypatch.setenv("TRACE_PATH", str(trace_path))
    monkeypatch.setenv("DIRECT_INPUT", str(direct_input_path))

    import sys

    import settings as settings_pkg

    # Rebuild the settings singleton from the env set above, then rebind it on
    # the package so `from settings import settings` sees the fresh object.
    # The package rebinds the name `settings` to the object, so the submodule
    # must be fetched via sys.modules rather than attribute access.
    importlib.reload(sys.modules["settings.settings"])
    importlib.reload(settings_pkg)

    from lmu_settings_debug.core import game_settings as game_settings_module

    importlib.reload(game_settings_module)

    manager = game_settings_module.GameSettingsManager(file_path=file_path)
    return manager, settings_json_path


def test_disable_replay_recording_sets_false_and_persists(tmp_path, monkeypatch):
    manager, settings_json_path = _make_manager(
        tmp_path, monkeypatch, _settings_payload(), file_path=tmp_path / "Settings.JSON"
    )

    manager.disable_replay_recording()

    data = json.loads(settings_json_path.read_text())
    assert data["Game Options"]["Record Replays"] is False
    # unrelated keys untouched
    assert data["Game Options"]["Automatically Record Telemetry"] is True
    assert data["Game Options"]["Some Other Option"] == 42


def test_disable_telemetry_recording_sets_false_and_persists(tmp_path, monkeypatch):
    manager, settings_json_path = _make_manager(
        tmp_path, monkeypatch, _settings_payload(), file_path=tmp_path / "Settings.JSON"
    )

    manager.disable_telemetry_recording()

    data = json.loads(settings_json_path.read_text())
    assert data["Game Options"]["Automatically Record Telemetry"] is False
    assert data["Game Options"]["Record Replays"] is True


def test_set_game_option_missing_section_does_not_crash(tmp_path, monkeypatch):
    manager, settings_json_path = _make_manager(
        tmp_path,
        monkeypatch,
        {"Graphic Options": {"Whatever": 1}},
        file_path=tmp_path / "Settings.JSON",
    )

    # Should warn and skip, not raise.
    manager.disable_replay_recording()

    data = json.loads(settings_json_path.read_text())
    assert "Game Options" not in data


def test_set_game_option_missing_key_does_not_crash(tmp_path, monkeypatch):
    manager, settings_json_path = _make_manager(
        tmp_path,
        monkeypatch,
        {"Game Options": {"Some Other Option": 42}},
        file_path=tmp_path / "Settings.JSON",
    )

    manager.disable_replay_recording()

    data = json.loads(settings_json_path.read_text())
    assert "Record Replays" not in data["Game Options"]
    assert data["Game Options"]["Some Other Option"] == 42


def test_create_backup_creates_file(tmp_path, monkeypatch):
    manager, settings_json_path = _make_manager(
        tmp_path, monkeypatch, _settings_payload(), file_path=tmp_path / "Settings.JSON"
    )

    assert manager.create_backup() is True

    backups = list(settings_json_path.parent.glob("Settings.bak_*"))
    assert len(backups) == 1


def test_default_path_derived_from_direct_input_sibling(tmp_path, monkeypatch):
    # file_path=None -> resolve Settings.JSON next to direct_input.json
    manager, settings_json_path = _make_manager(
        tmp_path, monkeypatch, _settings_payload(), file_path=None
    )

    assert Path(manager.file_path) == settings_json_path

    manager.disable_replay_recording()
    data = json.loads(settings_json_path.read_text())
    assert data["Game Options"]["Record Replays"] is False
