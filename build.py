#!/usr/bin/env python3

import sys
import subprocess
import os


def check_python():
    print("Checking Python version...")
    if sys.version_info < (3, 10):
        print("Python 3.10+ is required!")
        sys.exit(1)
    print(f"Python OK: {sys.version.split()[0]}")


def install_requirements():
    if not os.path.exists("requirements.txt"):
        print("No requirements.txt found — skipping dependency installation")
        return

    print("Installing dependencies...")
    subprocess.check_call([
        sys.executable,
        "-m",
        "pip",
        "install",
        "-r",
        "requirements.txt"
    ])


def run_gui():
    print("Starting GUI application...")
    subprocess.check_call([
        sys.executable,
        os.path.join("src", "gui.py")
    ])


def main():
    print("==== UVM Build Script ====")

    try:
        check_python()
        install_requirements()
        run_gui()

        print("Build finished successfully!")

    except subprocess.CalledProcessError as e:
        print("Build failed:", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
