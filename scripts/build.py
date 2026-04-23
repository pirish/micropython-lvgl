#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import sys

# Configuration for supported targets
TARGETS = {
    "rp2040": {"port": "rp2", "board": "RPI_PICO", "docker": "arm", "ext": "uf2"},
    "rp2350": {"port": "rp2", "board": "RPI_PICO2", "docker": "arm", "ext": "uf2"},
    "esp32": {"port": "esp32", "board": "ESP32_GENERIC", "docker": "esp32", "ext": "bin"},
    "nrf52": {"port": "nrf", "board": "PCA10040", "docker": "arm", "ext": "hex"},
    "unix": {"port": "unix", "board": "", "docker": "arm", "ext": ""},
}

# Boards matrix for CI
CI_BOARDS = [
    {"target": "rp2040", "board": "RPI_PICO"},
    {"target": "rp2040", "board": "RPI_PICO_W"},
    {"target": "rp2350", "board": "RPI_PICO2"},
    {"target": "esp32", "board": "ESP32_GENERIC"},
    {"target": "esp32", "board": "ESP32_GENERIC_S3"},
]


def run_command(cmd, cwd=None, env=None):
    print(f"Executing: {' '.join(cmd)}")
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    result = subprocess.run(cmd, cwd=cwd, env=merged_env)
    if result.returncode != 0:
        print(f"Error executing command: {' '.join(cmd)}")
        sys.exit(1)


def build_mpy_cross():
    print("Building mpy-cross...")
    run_command(["make", "-C", "submodules/micropython/mpy-cross"])


def process_assets():
    print("Processing assets...")
    os.makedirs("modules/assets", exist_ok=True)


def apply_profile(profile_path):
    if not profile_path:
        return
    print(f"Applying hardware profile: {profile_path}")
    with open(profile_path, "r") as f:
        profile = json.load(f)

    # Generate a frozen python module with these settings
    os.makedirs("modules", exist_ok=True)
    with open("modules/hardware_config.py", "w") as f:
        f.write("# Generated hardware configuration\n")
        f.write(f"CONFIG = {json.dumps(profile, indent=4)}\n")


def flash_device(target, board):
    if target in ["rp2040", "rp2350"]:
        print("Please copy the UF2 file to your RPI-RP2 bootloader drive.")
    elif target == "esp32":
        bin_path = f"submodules/micropython/ports/esp32/build-{board}/micropython.bin"
        run_command(["esptool.py", "write_flash", "0x0", bin_path])
    elif target == "unix":
        run_command(["submodules/micropython/ports/unix/build-standard/micropython"])


def build_target(target, board=None, profile=None):
    config = TARGETS.get(target)
    port = config["port"]
    board = board or config["board"]

    process_assets()
    apply_profile(profile)

    lv_bindings = os.path.abspath("submodules/lv_binding_micropython")
    manifest = os.path.abspath("modules/manifest.py")
    ccache_dir = os.path.abspath(".ccache")
    os.makedirs(ccache_dir, exist_ok=True)

    env = {"CCACHE_DIR": ccache_dir, "MICROPY_CPYTHON3": "python3", "USER_C_MODULES": lv_bindings}
    cmd = ["make", "-C", f"submodules/micropython/ports/{port}"]

    if target == "unix":
        cmd.extend([f"FROZEN_MANIFEST={manifest}", "VARIANT=standard"])
    else:
        cmd.extend([f"BOARD={board}", f"FROZEN_MANIFEST={manifest}"])

    custom_conf = os.path.abspath("config/lv_conf.h")
    if os.path.exists(custom_conf):
        env["LV_CONF_PATH"] = custom_conf

    run_command(cmd, env=env)


def get_container_engine(prefer_podman=False):
    if prefer_podman:
        return "podman"
    try:
        subprocess.run(["docker", "--version"], capture_output=True)
        return "docker"
    except Exception:
        return "podman"


def main():
    parser = argparse.ArgumentParser(description="MicroPython + LVGL Build Glue Script")
    parser.add_argument("--target", choices=TARGETS.keys())
    parser.add_argument("--board", help="Specific board")
    parser.add_argument("--profile", help="Path to hardware profile JSON")
    parser.add_argument("--docker", action="store_true")
    parser.add_argument("--podman", action="store_true")
    parser.add_argument("--flash", action="store_true")
    parser.add_argument("--ci-matrix", action="store_true", help="Print CI matrix and exit")

    args = parser.parse_args()

    if args.ci_matrix:
        print(json.dumps(CI_BOARDS))
        return

    if not args.target:
        parser.error("the following arguments are required: --target")

    if args.docker or args.podman:
        engine = get_container_engine(args.podman)
        image = f"lvgl-build-{TARGETS[args.target]['docker']}"
        vol = f"{os.getcwd()}:/build" + (":Z" if engine == "podman" else "")
        os.makedirs(".ccache", exist_ok=True)

        cmd = [
            engine,
            "run",
            "--rm",
            "-v",
            vol,
            "-e",
            "CCACHE_DIR=/build/.ccache",
            image,
            "python3",
            "scripts/build.py",
            "--target",
            args.target,
        ]
        if args.board:
            cmd.extend(["--board", args.board])
        if args.profile:
            cmd.extend(["--profile", args.profile])
        run_command(cmd)
    else:
        if args.target != "unix":
            build_mpy_cross()
        build_target(args.target, args.board, args.profile)
        if args.flash:
            flash_device(args.target, args.board or TARGETS[args.target]["board"])


if __name__ == "__main__":
    main()
