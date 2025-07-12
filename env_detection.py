import importlib.util
import platform
import os
import subprocess

def detect_vnc():
    try:
        display = os.environ.get("DISPLAY", "")
        if display.startswith(":") and display != ":0":
            return True

        output = subprocess.check_output(["ps", "aux"]).decode()
        vnc_keywords = ["Xvnc", "vncserver", "vncserver-virtual", "vncagent"]
        return any(any(k in line for k in vnc_keywords) for line in output.splitlines())
    except:
        return False

def detect_environment():
    env_info = {
        "os": platform.platform(),
        "is_raspberry_pi": False,
        "is_headless": not bool(os.environ.get("DISPLAY")),
        "is_vnc": detect_vnc(),
        "sensehat_available": False,
        "neopixel_available": False,
        "sensehat_emulator": False,
    }

    try:
        with open('/proc/cpuinfo') as f:
            env_info["is_raspberry_pi"] = "Raspberry Pi" in f.read()
    except:
        pass

    try:
        from sense_hat import SenseHat
        _ = SenseHat()
        env_info["sensehat_available"] = True
    except:
        env_info["sensehat_available"] = False

    try:
        from sense_emu import SenseHat as EmuSense
        _ = EmuSense()
        env_info["sensehat_emulator"] = True
    except:
        env_info["sensehat_emulator"] = False

    env_info["neopixel_available"] = importlib.util.find_spec("neopixel") is not None

    return env_info


env = detect_environment()
for k, v in env.items():
    print(f"{k:20}: {v}")
