import pprint
from time import sleep
from lmu_settings_debug.core.manager import DeviceControlManager
from lmu_settings_debug.core.game_settings import GameSettingsManager
from settings import settings

_first_step_explanation = """Your devices likely have a few default settings, that are causing cpu usage while lowering your game's overall performance.
If you are experiencing slight stutters here and there, there is likely a chance, that your 'direct input.json' is a bit corrupted.
Overall it is a good idea to run this setup, because it won't break anything but can only improve your performance.
The following setup will configure your wheel base and disable the Force Feedback on devices like your brakes, steering wheel, haptic motors (yes the FFB is likely activated by default!) and more devices.
If you want to exclude any device from the settings, the setup will tell you how. 
If you want to see what's going on behind, open the src/lmu_settings_debug/main_local.py file and see the settings payloads."""


def configure_game_options() -> None:
    """
    Interactive step: optionally disable replay and telemetry recording in
    Settings.JSON. Replay recording in particular is a common stutter source.

    Skips gracefully if Settings.JSON cannot be located.
    """
    print("\n--- Game Options ---")
    try:
        game_settings = GameSettingsManager()
    except FileNotFoundError:
        print(
            "Could not locate your Settings.JSON, skipping this step. "
            "Your device settings above were still applied."
        )
        return

    disable_replay = (
        input("Disable replay recording? It often causes stutters. (y/n)\n -> ").lower()
        == "y"
    )
    disable_telemetry = (
        input("Disable automatic telemetry recording? (y/n)\n -> ").lower() == "y"
    )

    if not (disable_replay or disable_telemetry):
        print("Leaving Game Options unchanged.")
        return

    game_settings.create_backup()
    if disable_replay:
        game_settings.disable_replay_recording()
    if disable_telemetry:
        game_settings.disable_telemetry_recording()


def main():
    manager = DeviceControlManager()

    print("Welcome to LMU Device-Settings Debugger!")
    print("-----------------------------------------------")
    print(_first_step_explanation)  # Explain what the problem is and

    print(f"Your trace.txt path is: {settings.trace_path}")
    print(f"Your direct input.json path is: {settings.direct_input}")
    print("")
    print("\nThese are your devices:")
    user_device_map = {}
    for i, device in enumerate(manager.get_devices()):
        user_device_map[i + 1] = device
        print(f"{i + 1}  - {device}")

    sleep(0.3)

    # Show what will be changed
    choice = input(
        "\nDo you want to see what will be changed before starting? (y/n)\n -> "
    )
    if choice.lower() == "y":
        print("\n -- PERIPHERY_DEVICES_CONFIG -- ")
        pprint.pprint(manager.periphery_defaults)
        print("")
        print("\n -- WHEEL_BASE_CONFIG -- ")
        pprint.pprint(manager.wheelbase_defaults)
        print("")

    sleep(0.3)

    choice = input(
        "You should create a backup of your existing direct input.json. Do you want to do that automatically?(y/n)\n -> "
    )
    if choice.lower() == "y":
        manager.create_backup()

    # Choose the wheelbase
    while True:
        try:
            user_wb_idx = int(input("Paste the number of your wheelbase:\n -> "))
            user_wheelbase = user_device_map[user_wb_idx]
            break  # Exit loop if successful
        except (ValueError, KeyError):
            print(
                f"Invalid selection. Please enter a number between 1 and {len(user_device_map)}."
            )

    manager.apply_to_device(user_wheelbase, manager.wheelbase_defaults)

    print("")
    sleep(0.3)
    print("\n--- Peripheral Devices Update ---")
    choice = input("Do you want to autocorrect the rest of your devices? (y/n)\n -> ")
    if choice.lower() == "y":
        manager.apply_to_all(manager.periphery_defaults, to_exclude=[user_wheelbase])

    sleep(0.3)
    configure_game_options()

    print(
        "\nCongrats! You have successfully updated your LMU Device Settings!\nIt's highly recommended to run the lmu_log_checker/main.py after a few laps to check if everything is working now.\n\n Good luck racing!"
    )


if __name__ == "__main__":
    main()
