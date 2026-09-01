# Wiring

## Module pinout

The AHT20+BMP280 board's pads run **VDD · SDA · GND · SCL** — ground sits
third, not at an edge. Read the silkscreen; do not assume a sane order.
The upside is that in a flat cable this puts ground between the two
signals, which is exactly where you want it.

## To the Pi

| Module | Signal | Header pin | Colour |
|---|---|---:|---|
| VDD | 3V3 | **1** | red |
| SDA | I2C data | **3** | blue |
| GND | ground | **6** | black |
| SCL | I2C clock | **5** | green |

Same physical pins on every Pi. **VDD to pin 1, never pin 2 (5 V).**
Wire with the Pi unplugged. Count the pins twice from the board edge.

Colour convention is shared with newton-instrumentation — red and black
are reserved for power and never carry a signal. Full table and the
reasoning live in that repo's `hardware/wiring.md`.

## Bus number

Unresolved until the board is identified:

- 26-pin header, full-size SD, 2 USB → 2011 Model B → **`i2cdetect -y 0`**
- 40-pin header, microSD, 4 USB → Pi 3 or later → **`i2cdetect -y 1`**

`cat /proc/device-tree/model` settles it. Expect `38` and `76`.

## Cable length

I2C is capacitance-limited, 400 pF for the bus at 100 kHz. Under 50 cm
needs no thought. Past ~1 m, drop the bus to 50 kHz
(`dtparam=i2c_arm_baudrate=50000`) and use twisted pair — SDA with a
ground, SCL with a ground. A stripped length of CAT5 works.

## Outdoors

The bare module is not weatherproof: condensation drifts the humidity
reading and eventually kills it. It needs a ventilated radiation shield —
a stacked-plate Stevenson screen, printable in PETG.
