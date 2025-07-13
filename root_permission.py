import os

def is_root():
    return os.geteuid() == 0  # Only works on Unix-like systems

try:
    from sense_emu import SenseHat
    if is_root():
        hat = SenseHat()
        hat.show_message("Hi!")
        print("Hardware Sense HAT initialized.")
    else:
        print("Warning: Not running as root. Some features may be restricted.")
except ImportError:
    print("Sense HAT module not installed.")

"""
If You Want Full Root Access:
If a script must run with hardware control:

sudo python3 your_script.py

Or create a systemd service that runs your game/app on boot with root access.
"""