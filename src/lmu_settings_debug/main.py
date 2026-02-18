import json
from typing import Any, Dict

from settings import settings


def read_json(file_path) -> Dict[str, Any]:
    """Reads a JSON file and returns its content as a dictionary."""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(file_path, data: Dict[str, Any]) -> None:
    """Writes a dictionary to a JSON file."""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def main():
    # 1. Read
    data = read_json(settings.direct_input)

    # 2. Modify
    devices = data.get("Devices", {})
    for key, device_data in devices.items():
        print(f"Updating {key}...")
        # Set "Steering Wheel Maximum Rotation From Driver" to False
        if "options" in device_data:
            print(device_data["options"]["Steering Wheel Maximum Rotation From Driver"])
            device_data["options"]["Steering Wheel Maximum Rotation From Driver"] = False

    # 3. Write
    #write_json(settings.direct_input, data)
    print("Updated 'Steering Wheel Maximum Rotation From Driver' to False for all devices.")


if __name__ == "__main__":
    main()
