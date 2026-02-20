from .manager import DeviceControlManager

if __name__ == "__main__":
    manager = DeviceControlManager()

    # print all devices.
    print(manager.get_devices())

