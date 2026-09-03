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

Resolved: **`i2c-1`**.

The board is a **Model B Rev 2** — 26-pin header, full-size SD, 2 USB,
micro-USB power, no WiFi, BCM2835 (ARMv6). Note that *both* 26-pin
revisions exist and they differ on exactly this point:

| | Rev 1 | Rev 2 |
|---|---|---|
| Header pins 3 / 5 | GPIO0 / GPIO1 | GPIO2 / GPIO3 |
| Bus | `i2c-0` | **`i2c-1`** |
| Mounting holes | none | **two** |
| Fifth LED silkscreen | `10M` | `100` |

Mounting holes are the quick tell — Rev 1 has none at all, which was a
real complaint at the time. The `(c) 2011.12` silkscreen is a copyright
line, not a date code; it appears on both and settles nothing.

`grep Revision /proc/cpuinfo` is definitive: `0002`/`0003` are Rev 1,
`0004` and later are Rev 2.

The wiring table above is unaffected — the physical header pins are the
same on both revisions, only the GPIO numbering behind them changes.

So: **`i2cdetect -y 1`**. Expect `38` and `77`.

`0x38` is the AHT20. The BMP280 answers on **`0x77`, not `0x76`** — its
address is set by the SDO pin, low gives `0x76` and high gives `0x77`,
and this module ties it high. Both are correct BMP280 addresses; which
one you get is a board-layout decision the vendor made for you. Confirmed
by `i2cdetect` on this unit, so `0x77` is what the code must use.

`dtparam=i2c_arm=on` is only half of enabling the bus. It brings up the
controller but leaves out the `i2c-dev` module, so `/dev/i2c-1` never
appears and `i2cdetect` dies with `No such file or directory`. Run
`sudo raspi-config nonint do_i2c 0` — it adds `i2c-dev` to `/etc/modules`
as well. `/dev/i2c-2` also shows up; ignore it, it belongs to the HDMI
port.

## Cable length

I2C is capacitance-limited, 400 pF for the bus at 100 kHz. Under 50 cm
needs no thought. Past ~1 m, drop the bus to 50 kHz
(`dtparam=i2c_arm_baudrate=50000`) and use twisted pair — SDA with a
ground, SCL with a ground. A stripped length of CAT5 works.

## Outdoors

The bare module is not weatherproof: condensation drifts the humidity
reading and eventually kills it. It needs a ventilated radiation shield —
a stacked-plate Stevenson screen, printable in PETG.

## Power

Not wiring, but it lands here because it looks like wiring. The Model B
needs **5 V at 2 A** through a short, thick micro-USB cable. Undervolted,
it does not fail cleanly: it half-boots, resets in a loop, or reaches a
login prompt with no USB and no Ethernet at all. The full symptom table
is in the README.

Add the sensor's own draw on top. A supply that just barely boots a bare
board will not boot one with a sensor hanging off the 3V3 rail.
