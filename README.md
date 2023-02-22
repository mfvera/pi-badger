# pi-badger
A headless badge reading application for Raspberry Pi.

## Installation
1. Setup your RPi for headless operation by enabling SSH and booting to the terminal rather than starting the graphical environment.
2. Install CircuitPython by following [this Adafruit guide](https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi).
3. After rebooting, run `pipenv install` to install the dependencies for this project.
    * You may need to install [`pipenv`](https://pypi.org/project/pipenv/) if you don't already have it.
4. Place the following into `~/.bashrc` after replacing the path to match your system:
    ```bash
    if [ -z "$SSH_CLIENT" ] && [ -z "$SSH_TTY" ]; then
        python3 ~/projects/pi-badger/src/main.py
    fi
    ```
5. Reboot the RPi