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
| Raspberry Pi Model B | **model unconfirmed** — decides `i2c-0` vs `i2c-1` |
| AHT20 + BMP280 module | spare from the telescope BOM. AHT20 `0x38`, BMP280 `0x76` |
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

Not started. Blocked on identifying the Pi model.
