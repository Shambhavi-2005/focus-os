import ctypes


class SYSTEM_POWER_STATUS(ctypes.Structure):

    _fields_ = [
        ("ACLineStatus", ctypes.c_ubyte),
        ("BatteryFlag", ctypes.c_ubyte),
        ("BatteryLifePercent", ctypes.c_ubyte),
        ("Reserved", ctypes.c_ubyte),
        ("BatteryLifeTime", ctypes.c_ulong),
        ("BatteryFullLifeTime", ctypes.c_ulong),
    ]


def get_power_status():

    status = SYSTEM_POWER_STATUS()

    result = ctypes.windll.kernel32.GetSystemPowerStatus(
        ctypes.byref(status)
    )

    if not result:
        return {
            "battery": "Unknown",
            "charging": False,
            "power": "Unknown"
        }

    battery = status.BatteryLifePercent

    if status.ACLineStatus == 1:
        charging = True
        power = "Plugged In"

    elif status.ACLineStatus == 0:
        charging = False
        power = "On Battery"

    else:
        charging = False
        power = "Unknown"

    return {
        "battery": battery,
        "charging": charging,
        "power": power
    }