import websocket
import json
import os
import sys
import time

def load_settings():
    with open("settings.json") as f:
        return json.load(f)

def get_client_key(settings):
    if os.path.exists(settings["client_key_file"]):
        with open(settings["client_key_file"]) as f:
            return json.load(f)["client-key"]
    return None

def send_poweroff_command(tv_ip, client_key):
    try:
        ws = websocket.create_connection(f"ws://{tv_ip}:3000/")
        
        payload = {
            "type": "register",
            "payload": {
                "pairingType": "PROMPT",
                "client-key": client_key or ""
            }
        }
        ws.send(json.dumps(payload))

        time.sleep(1)

        payload = {
            "id": "power_off",
            "type": "request",
            "uri": "ssap://system/turnOff"
        }
        ws.send(json.dumps(payload))
        
        ws.close()
    except Exception as e:
        print(f"Error sending poweroff: {e}")

if __name__ == "__main__":
    settings = load_settings()
    client_key = get_client_key(settings)
    tv_ip = settings["tv_ip"]
    if tv_ip == "auto":
        from discover_tv import discover_tv
        tv_ip = discover_tv()
    send_poweroff_command(tv_ip, client_key)
