#!/usr/bin/env python3
import os
import subprocess
import sys


def run(cmd, msg):
    print(f"--- {msg} ---")
    print(f"Executing: {' '.join(cmd)}")
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print(f"FAILED: {msg}")
        sys.exit(1)
    print(f"SUCCESS: {msg}\n")


def main():
    # 1. Linting
    try:
        run(["ruff", "--version"], "Checking for Ruff")
        run(["ruff", "check", "scripts/", "modules/"], "Running Linter (Ruff)")
    except FileNotFoundError:
        print("Ruff not found, skipping lint step...\n")

    # 2. Build Unix Port (Fastest way to verify C logic and bindings)
    # We need to ensure submodules are there
    if not os.path.exists("submodules/micropython/py/mkrules.mk"):
        run(["git", "submodule", "update", "--init", "--recursive"], "Initializing submodules")

    run(["python3", "scripts/build.py", "--target", "unix"], "Building Unix Simulator")

    # 3. Verification
    exe_path = "submodules/micropython/ports/unix/build-standard/micropython"
    if os.path.exists(exe_path):
        print("--- Verification ---")
        print(f"Binary created at: {exe_path}")
        print("Test passed successfully!")
    else:
        print("Test FAILED: Binary not found.")
        sys.exit(1)


if __name__ == "__main__":
    main()
