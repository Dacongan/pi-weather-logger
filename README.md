# pi-weather-logger

Outdoor temperature, humidity and pressure logged on a Raspberry Pi and
published as a static page.

Practice run for the firmware of
[newton-instrumentation](https://github.com/Dacongan/newton-instrumentation):
the dew point calculated here is the same one that decides when the
telescope's secondary heater turns on.

## Hardware

| Part | Notes |
|---|---|
| Raspberry Pi Model B Rev 2 | 26-pin, BCM2835 (ARMv6), no WiFi — bus is `i2c-1` |
| 5 V 2 A PSU | not optional — see Status |
| AHT20 + BMP280 module | spare from the telescope BOM. AHT20 `0x38`, BMP280 `0x77` |
| 4-pin 2.54 mm header | soldered on; pads run VDD · SDA · GND · SCL |

Sensor sits outdoors, Pi indoors at the window. I2C run stays under
~50 cm — see `hardware/wiring.md`.

## Layout

```
hardware/   wiring, pinout, colour convention
logger/     reads the sensor, writes to data/
web/        static page served by GitHub Pages
data/       one CSV per day + latest.json
```

## Status

Board identified — Model B Rev 2, ARMv6, `i2c-1`, Ethernet only. The
32-bit build of Raspberry Pi OS is not a convenience here, it is the only
option: the 64-bit images need ARMv8.

SD card written with **Raspberry Pi OS Lite (32-bit, Trixie)**, headless:
hostname `weatherpi`, SSH by key, and `dtparam=i2c_arm=on` uncommented in
`config.txt` before first boot. Verified on the card that the image still
ships `kernel.img` and `bcm2708-rpi-b.dtb`, so it does boot on a 2012
board.

**Running.** Boots to a login in ~127 s, reachable as `weatherpi.local`
over SSH by key. Kernel `6.18.34+rpt-rpi-v6`, `armv6l` — Trixie does
still build for ARMv6. Both sensors answer on `i2c-1`.

### The power supply is the whole story

First boot failed four different ways, and all four were one fault: an
undersized supply. Worth writing down, because none of the symptoms says
"power" out loud.

| Symptom | Actual cause |
|---|---|
| 3 green ACT flashes, no boot | brownout reading `start.elf` — 3 MB in one go |
| rainbow → black → rainbow loop | reset the moment the kernel raises current draw |
| USB keyboard unpowered | LAN9512 never came up |
| no Ethernet, no DHCP, invisible to ARP | same LAN9512 — on a Model B the NIC *is* a USB device |

USB and Ethernet hang off the same chip, so a dead keyboard and a dead
network are one failure, not two. **5 V 2 A minimum, with a short thick
micro-USB cable.** A phone charger boots the CPU and nothing else.

### `dtparam` alone does not give you `/dev/i2c-1`

Enabling I2C by hand in `config.txt` loads the controller but not the
`i2c-dev` module, so the device node never appears and `i2cdetect` fails
with `No such file or directory`. `raspi-config nonint do_i2c 0` does
both halves; it appends `i2c-dev` to `/etc/modules`.

## Final Software Architecture

**1. Python Logger:** `logger.py` runs on a 15-minute `systemd` timer (`logger.timer`). It reads temperature and humidity from the AHT20 and pressure from the BMP280 via `smbus2`, calculates the dew point, and appends the data to a daily CSV (e.g. `data/YYYY-MM-DD.csv`), plus a `data/latest.json` file for quick access.

**2. Git Automation:** After writing the data, `logger.py` executes a `subprocess` to `git add`, `git commit`, and `git push` directly to GitHub using a passwordless SSH deploy key.

**3. Web UI:** A static page at `web/index.html` is hosted by GitHub Pages. It fetches `data/latest.json` to display the current weather metrics on dark-mode CSS cards, and parses the daily `.csv` file with Chart.js to plot the temperature and dew point trends over the day.

**Status:** Project completed and fully operational.
