import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from settings import settings

extended_config_updates = {
    "options": {
        "Steering Wheel Maximum Rotation From Driver": False,
        "Hardware 3Digit Display": 0,
        "Brake Bias Axis": False,
        "Gear Select Button Hold": False,
        "use leds": False
    },
    "Force Feedback": {
        "Enabled": False,
        "constant steering force": False
    }
}

wheelbase_config_updates = {
    "options": {
        "Steering Wheel Maximum Rotation From Driver": False,

        "Hardware 3Digit Display": 0,
        "Brake Bias Axis": False,
        "Gear Select Button Hold": False,
        "use leds": False
    },
    "Force Feedback": {
        "Enabled": True
    }
}


class DeviceControlManager:
    """
    Manages device configurations stored in a JSON file.
    """

    def __init__(self, file_path: Union[str, Path] = settings.direct_input):
        """
        Initializes the DeviceControlManager with a given file path.

        Args:
            file_path (Union[str, Path]): The path to the JSON configuration file.
        """
        self.file_path = Path(file_path)
        self.raw_data = self._read_json(self.file_path)

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

    def get_devices(self, to_exclude: Optional[List[str]] = None) -> List[str]:
        """
        Retrieves a list of device names.
        """
        devices = self.raw_data.get("Devices", {})
        exclude_list = to_exclude or []
        return [name for name in devices.keys() if name not in exclude_list]

    @staticmethod
    def _apply_payload_to_data(device_name: str, device_data: Dict[str, Any],
                               payload: Dict[str, Dict[str, Any]]) -> None:
        """
        Internal helper to apply a payload to a specific device's data dictionary.
        """
        print(f"Applying payload to {device_name}...")
        for category, updates in payload.items():
            if category in device_data:
                device_category = device_data[category]
                for key, value in updates.items():
                    print(f"  Updating [{category}][{key}]: {device_category.get(key)} -> {value}")
                    device_category[key] = value
            else:
                print(f"  Category '{category}' not found in {device_name}. Skipping category.")

    def apply_to_device(self, device_name: str, payload: Dict[str, Dict[str, Any]]) -> None:
        """
        Applies a configuration payload to a single specific device.

        Args:
            device_name (str): The name of the device to update.
            payload (Dict[str, Dict[str, Any]]): The configuration payload.
        """
        devices = self.raw_data.get("Devices", {})
        if device_name not in devices:
            print(f"Device '{device_name}' not found in configuration.")
            return

        self._apply_payload_to_data(device_name, devices[device_name], payload)
        self._write_json(self.file_path, self.raw_data)
        print(f"Update for '{device_name}' complete.")

    def apply_to_all(self, payload: Dict[str, Dict[str, Any]], to_exclude: Optional[List[str]] = None) -> None:
        """
        Applies a configuration payload to all devices, except those in the exclusion list.

        Args:
            payload (Dict[str, Dict[str, Any]]): The configuration payload.
            to_exclude (Optional[List[str]]): A list of device names to skip.
        """
        devices = self.raw_data.get("Devices", {})
        exclude_list = to_exclude or []

        for device_name, device_data in devices.items():
            if device_name in exclude_list:
                print(f"Skipping excluded device: {device_name}")
                continue
            self._apply_payload_to_data(device_name, device_data, payload)

        self._write_json(self.file_path, self.raw_data)
        print("\nGlobal update complete.")

    def update_device_option(
            self,
            option_name: str,
            value: Any,
            device_name: Optional[str] = None,
            to_exclude: Optional[List[str]] = None,
    ) -> None:
        """
        Updates a specific option for one or all devices.
        """
        payload = {"options": {option_name: value}}
        if device_name:
            self.apply_to_device(device_name, payload)
        else:
            self.apply_to_all(payload, to_exclude)

    def update_device_ffb(
            self,
            key_name: str,
            value: Any,
            device_name: Optional[str] = None,
            to_exclude: Optional[List[str]] = None
    ):
        """
        Updates a specific Force Feedback option for one or all devices.
        """
        payload = {"Force Feedback": {key_name: value}}
        if device_name:
            self.apply_to_device(device_name, payload)
        else:
            self.apply_to_all(payload, to_exclude)


if __name__ == "__main__":
    # Example_Usage
    manager = DeviceControlManager()

    print("\n--- Single Device Update ---")
    manager.apply_to_device("Simucube 2 Pro-4FCD75134409FC89", wheelbase_config_updates)

    print("\n--- Global Update ---")
    manager.apply_to_all(extended_config_updates, to_exclude=["Simucube 2 Pro-4FCD75134409FC89"])

    print("\n--- Single Option Update ---")
    manager.update_device_option("use leds", True, device_name="CONSPIT 300GT-B84DF9363E4C8D84")
