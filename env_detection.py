import importlib.util
import platform
import os
import subprocess

def detect_environment():
    env_info = {
        "os": platform.platform(),
        "is_raspberry_pi": False,
        "is_headless": False,
        "is_vnc": False,
        "sensehat_available": False,
        "neopixel_available": False,
        "sensehat_emulator": False,
    }

    # Check for Raspberry Pi
    try:
        with open('/proc/cpuinfo') as f:
            cpuinfo = f.read()
            env_info["is_raspberry_pi"] = "BCM" in cpuinfo or "Raspberry Pi" in cpuinfo
    except:
        pass

    # Check for VNC
    env_info["is_vnc"] = "VNCSESSION" in os.environ or any("vnc" in l.lower() for l in os.popen("who").readlines())

    # Check for headless
    env_info["is_headless"] = not os.environ.get("DISPLAY")

    # Check for sense_hat (real hardware)
    env_info["sensehat_available"] = importlib.util.find_spec("sense_hat") is not None

    # Check for sense_emu (emulator)
    env_info["sensehat_emulator"] = importlib.util.find_spec("sense_emu") is not None

    # Check for neopixel
    env_info["neopixel_available"] = importlib.util.find_spec("neopixel") is not None

    return env_info

env = detect_environment()
for k, v in env.items():
    print(f"{k:20}: {v}")
