# MicroPython + LVGL Build System

![Build Status](https://github.com/youruser/lvgl-micropy/actions/workflows/build.yml/badge.svg)
![Update Check](https://github.com/youruser/lvgl-micropy/actions/workflows/check_updates.yml/badge.svg)

This project provides glue scripts and CI workflows to build MicroPython with [LVGL](https://lvgl.io/) integrated for various architectures.

## Supported Architectures

- **RP2040**: Raspberry Pi Pico and similar.
- **RP2350**: Raspberry Pi Pico 2.
- **ESP32**: Generic ESP32, ESP32-S2, ESP32-S3.
- **nRF52/nRF54**: Nordic Semiconductor boards.

## Prerequisites

- **Docker or Podman** (Recommended: handles all toolchains and dependencies automatically).
- **Python 3** and **Git**.
- **Doxygen** (Required for generating LVGL bindings).

## Getting Started

### 1. Clone the repository with submodules
```bash
git clone --recursive https://github.com/youruser/lvgl-micropy.git
cd lvgl-micropy
```

### 2. Build via Container (Recommended)

Docker or Podman ensures you have the correct compiler versions and dependencies (like `doxygen` and `pyelftools`) without polluting your host system.

First, build the required image for your target:

```bash
# Using Docker
docker build -t lvgl-build-arm -f docker/Dockerfile.arm .
# Using Podman
podman build -t lvgl-build-arm -f docker/Dockerfile.arm .
```

Then run the build script:

```bash
# Automatically detects docker or podman
./scripts/build.py --target rp2040 --docker

# Or force podman specifically
./scripts/build.py --target rp2040 --podman
```

### 3. Build Locally

If you prefer to run natively, ensure you have the following installed:
- **Build Tools**: `make`, `cmake`, `gcc`, `g++`.
- **Doxygen**: `sudo apt install doxygen`.
- **Python Libs**: `pip install pyelftools`.
- **Cross-Compilers**: `gcc-arm-none-eabi` (for RP2/nRF) or `ESP-IDF` (for ESP32).

```bash
./scripts/build.py --target rp2040
```

## Automation & CI/CD

### GitHub Actions
- **Build Workflow**: Triggered on push or manually. It builds firmware for all targets and uploads them as artifacts.
- **Automated Releases**: When triggered by the update checker, it creates a formal GitHub Release tagged as `MICROPYTHONVERSION_LVGLVERSION`.

### Automated Update Polling
The `Check for Updates` workflow runs daily. It:
1. Polls the official MicroPython and LVGL repositories for new releases.
2. Compares them against the latest release in this repository.
3. If an update is found, it automatically triggers a new build and release.

## Adding New Platforms

To add support for a new microcontroller architecture or board:

1.  **Update `scripts/build.py`**:
    *   Add the new architecture to the `TARGETS` dictionary. Define its `port` (as named in `submodules/micropython/ports`), default `board`, and the `docker` toolchain it should use (`arm` or `esp32`).
2.  **Toolchains**:
    *   If the platform requires a new cross-compiler, add it to a new `docker/Dockerfile.<name>` and update the `TARGETS` dictionary in `build.py` to reference it.
3.  **CI Matrix**:
    *   To include the new board in automated builds, add it to the `CI_BOARDS` list in `scripts/build.py`.
4.  **Hardware Profile**:
    *   Create a new JSON file in `profiles/` with the pinout and display settings for the new board.

## Professional Features

### 1. Hardware Profiles
Define display and pin configurations in `profiles/*.json`. The build script generates a `hardware_config.py` frozen module that you can use in your code.
```bash
./scripts/build.py --target rp2040 --profile profiles/pico_st7789.json
```

### 2. Asset Pipeline
Drop fonts and images into the `assets/` directory. They are processed and placed into the frozen `modules/assets/` directory during build.

### 3. Code Quality (Ruff)
The project uses [Ruff](https://github.com/astral-sh/ruff) for lightning-fast linting.
- **Local check**: `ruff check scripts/ modules/`
- **Auto-fix**: `ruff check --fix scripts/ modules/`
- **CI**: GitHub Actions automatically rejects PRs with linting errors.

### 4. Expanded CI Matrix
The GitHub Actions workflow now dynamically builds for a range of popular boards beyond the generics, including:
- Raspberry Pi Pico / Pico W / Pico 2
- ESP32 / ESP32-S3
- nRF variants

## Advanced Features

### 1. Unix Simulator
Build and run MicroPython + LVGL on your PC using SDL2. This is the fastest way to develop UI layouts.
```bash
# Build and run immediately
./scripts/build.py --target unix --flash
```

### 2. Custom Configuration
Place a custom `lv_conf.h` in the `config/` directory. The build script will automatically detect and use it, overriding the default LVGL settings.

### 3. Frozen Modules
Any `.py` files placed in the `modules/` directory will be "frozen" into the MicroPython firmware. This saves RAM and speeds up execution.
- Edit `modules/manifest.py` to customize what gets included.

### 4. Build Caching (ccache)
The build system automatically uses a hidden `.ccache` directory in the project root. This significantly speeds up subsequent builds by only compiling changed files.

### 5. Flashing
Use the `--flash` flag to automatically deploy the build:
- **ESP32**: Invokes `esptool.py`.
- **Unix**: Runs the generated executable.
- **RP2/nRF**: Prints instructions for file deployment.

```bash
./scripts/build.py --target esp32 --flash
```
