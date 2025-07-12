import importlib.util
import platform
import os
import subprocess

def detect_environment():
    env_info = {
        "os": platform.platform(),
        "is_raspberry_pi": False,
        "is_headless": not bool(os.environ.get("DISPLAY")),
        "is_vnc": False,
        "sensehat_available": False,
        "neopixel_available": False,
        "sensehat_emulator": False,
    }

    # Detect Raspberry Pi
    try:
        with open('/proc/cpuinfo') as f:
            env_info["is_raspberry_pi"] = "Raspberry Pi" in f.read()
    except:
        pass

    # Check if running under VNC via X11 DISPLAY
    display = os.environ.get("DISPLAY", "")
    if display.startswith(":") and not env_info["is_headless"]:
        try:
            xoutput = subprocess.check_output(["xset", "-q"]).decode()
            env_info["is_vnc"] = "VNC" in xoutput
        except:
            env_info["is_vnc"] = False

    # Check for usable sense_hat module
    try:
        from sense_hat import SenseHat
        _ = SenseHat()
        env_info["sensehat_available"] = True
    except Exception:
        env_info["sensehat_available"] = False

    # Check for emulator presence
    try:
        from sense_emu import SenseHat as EmuSense
        _ = EmuSense()
        env_info["sensehat_emulator"] = True
    except Exception:
        env_info["sensehat_emulator"] = False

    # Check for neopixel
    env_info["neopixel_available"] = importlib.util.find_spec("neopixel") is not None

    return env_info


env = detect_environment()
for k, v in env.items():
    print(f"{k:20}: {v}")
