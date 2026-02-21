import importlib
import json
from pathlib import Path


def _write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data))


def _make_manager(tmp_path: Path, monkeypatch):
    devices_data = {
        "Devices": {
            "Wheel": {
                "options": {"Damper": 1},
                "Force Feedback": {"Gain": 50},
            },
            "Pedals": {
                "options": {"Damper": 2},
                "Force Feedback": {"Gain": 75},
            },
        }
    }
    config_data = {
        "periphery_defaults": {"options": {"Damper": 0}},
        "wheelbase_defaults": {"Force Feedback": {"Gain": 0}},
    }

    trace_path = tmp_path / "trace.txt"
    trace_path.write_text("trace")
    direct_input_path = tmp_path / "direct_input.json"
    _write_json(direct_input_path, devices_data)
    config_path = tmp_path / "direct_input_config.json"
    _write_json(config_path, config_data)

    monkeypatch.setenv("TRACE_PATH", str(trace_path))
    monkeypatch.setenv("DIRECT_INPUT", str(direct_input_path))

    import settings as settings_pkg

    importlib.reload(settings_pkg)

    from lmu_settings_debug.core import manager as manager_module

    importlib.reload(manager_module)
    monkeypatch.setattr(
        manager_module.DeviceControlManager,
        "_get_config_path",
        staticmethod(lambda: config_path),
    )

    return (
        manager_module.DeviceControlManager(file_path=direct_input_path),
        direct_input_path,
    )


def test_get_devices_excludes(tmp_path: Path, monkeypatch) -> None:
    manager, _ = _make_manager(tmp_path, monkeypatch)

    devices = manager.get_devices()
    assert set(devices) == {"Wheel", "Pedals"}

    remaining = manager.get_devices(to_exclude=["Wheel"])
    assert remaining == ["Pedals"]


def test_apply_to_device_updates_and_persists(tmp_path: Path, monkeypatch) -> None:
    manager, direct_input_path = _make_manager(tmp_path, monkeypatch)

    manager.apply_to_device("Wheel", {"options": {"Damper": 0}})

    data = json.loads(direct_input_path.read_text())
    assert data["Devices"]["Wheel"]["options"]["Damper"] == 0
    assert data["Devices"]["Pedals"]["options"]["Damper"] == 2


def test_apply_to_all_respects_exclude(tmp_path: Path, monkeypatch) -> None:
    manager, direct_input_path = _make_manager(tmp_path, monkeypatch)

    manager.apply_to_all({"Force Feedback": {"Gain": 0}}, to_exclude=["Pedals"])

    data = json.loads(direct_input_path.read_text())
    assert data["Devices"]["Wheel"]["Force Feedback"]["Gain"] == 0
    assert data["Devices"]["Pedals"]["Force Feedback"]["Gain"] == 75


def test_update_device_option_updates_single_device(
    tmp_path: Path, monkeypatch
) -> None:
    manager, direct_input_path = _make_manager(tmp_path, monkeypatch)

    manager.update_device_option("Damper", 0, device_name="Wheel")

    data = json.loads(direct_input_path.read_text())
    assert data["Devices"]["Wheel"]["options"]["Damper"] == 0


def test_create_backup_creates_file(tmp_path: Path, monkeypatch) -> None:
    manager, direct_input_path = _make_manager(tmp_path, monkeypatch)

    assert manager.create_backup() is True

    backups = list(direct_input_path.parent.glob("direct_input.bak_*"))
    assert len(backups) == 1
