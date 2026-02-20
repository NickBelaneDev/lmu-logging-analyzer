import pprint

from manager import DeviceControlManager
from settings import settings


PERIPHERY_DEVICES_CONFIG = {
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

WHEEL_BASE_CONFIG = {
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

_first_step_explanation = f"""Your devices likely have a few default settings, that are causing cpu usage while lowering your game's overall performance.
If you are experiencing slight stutters here and there, there is likely a chance, that your 'direct input.json' is a bit corrupted.
Overall it is a good idea to run this setup, because it won't break anything but can only improve your performance.
The following setup will configure your wheel base and disable the Force Feedback on devices like your brakes, steering wheel, haptic motors (yes the FFB is likely activated by default!) and more devices.
If you want to exclude any device from the settings, the setup will tell you how. 
If you want to see what's going on behind, open the src/lmu_settings_debug/main_local.py file and see the settings payloads."""

if __name__ == "__main__":

    # Example_Usage
    manager = DeviceControlManager()

    print("Welcome to LMU Device-Settings Debugger!")
    print("-----------------------------------------------")
    print(_first_step_explanation) # Explain what the problem is and

    print(f"Your trace.txt path is: {settings.trace_path}")
    print(f"Your direct input.json path is: {settings.direct_input}")
    print("")
    print(f"\nThese are your devices:")
    user_device_map = {}
    for i, device in enumerate(manager.get_devices()):
        user_device_map[i + 1] = device
        print(f"{i + 1}  - {device}")

    # Show what will be changed
    choice = input("Do you want to see what will be changed before starting? (y/n)\n -> ")
    if choice.lower() == "y":
        print(f"\n -- PERIPHERY_DEVICES_CONFIG -- ")
        pprint.pprint(PERIPHERY_DEVICES_CONFIG)
        print("")
        print(f"\n -- WHEEL_BASE_CONFIG -- ")
        pprint.pprint(WHEEL_BASE_CONFIG)
        print("")

    # Choose the wheelbase
    while True:
        try:
            user_wb_idx = int(input("Paste the number of your wheelbase:\n -> "))
            break  # Exit loop if successful
        except (ValueError, KeyError):
            print(f"Invalid selection. Please enter a number between 1 and {len(user_device_map)}.")


    user_wheelbase = user_device_map[user_wb_idx]
    manager.apply_to_device(user_wheelbase, WHEEL_BASE_CONFIG)

    print("")

    print("\n--- Peripheral Devices Update ---")
    choice = input("Do you want to autocorrect the rest of your devices? (y/n)\n -> ")
    if choice.lower() == "y":
        manager.apply_to_all(PERIPHERY_DEVICES_CONFIG, to_exclude=[user_wheelbase])

    print("\nCongrats! You have successfully updated your LMU Device Settings!\nIt's highly recommended to run the lmu_log_checker/main.py after a few laps to check if everything is working now.\n\n Good luck racing!")

