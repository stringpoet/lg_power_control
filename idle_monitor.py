import time
import subprocess
import os
import json
import threading

def load_settings():
    with open("settings.json") as f:
        return json.load(f)

def get_idle_time():
    output = subprocess.check_output(
        ["ioreg", "-c", "IOHIDSystem"]
    ).decode("utf-8")
    idle_line = next(line for line in output.splitlines() if "HIDIdleTime" in line)
    nanoseconds = int(idle_line.split("=")[-1].strip())
    seconds = nanoseconds / 1_000_000_000
    return seconds

def send_notification(message, play_sound):
    try:
        notifier_path = os.path.join(os.getcwd(), "LGNotifier.app", "Contents", "MacOS", "LGNotifier")
        subprocess.run([notifier_path, message])
        if play_sound:
            subprocess.run(["afplay", "/System/Library/Sounds/Funk.aiff"])
    except Exception as e:
        print(f"Notification error: {e}")

def send_poweroff():
    subprocess.run(["python3", "send_poweroff.py"])

def send_wakeonlan(mac_address):
    addr_byte = bytes.fromhex(mac_address.replace(':', ''))
    magic_packet = b'\xff' * 6 + addr_byte * 16
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(magic_packet, ('<broadcast>', 9))

def main():
    settings = load_settings()
    idle_limit = settings["idle_timeout_minutes"] * 60
    warning_time = settings["warning_seconds"]
    warned = False
    poweroff_triggered = False

    print("Starting idle monitor...")

    while True:
        idle = get_idle_time()

        if idle > (idle_limit - warning_time) and not warned and not poweroff_triggered:
            print(f"Idle warning triggered at {idle} seconds.")
            send_notification("Turning off TV in 30 seconds unless activity", settings["play_warning_sound"])
            warned = True

        if idle > idle_limit and not poweroff_triggered:
            print(f"Idle timeout reached at {idle} seconds. Powering off TV.")
            send_poweroff()
            poweroff_triggered = True
            warned = False

        if idle < 5 and poweroff_triggered:
            print(f"Activity detected after TV off, waking TV.")
            # No Wake-on-LAN here for now (optional)
            poweroff_triggered = False
            warned = False

        time.sleep(5)

if __name__ == "__main__":
    main()
