# logger

Reads the sensor and writes to `../data/`.

Milestones, in order:

1. **AHT20** at `0x38` — trigger a measurement, wait, read 6 bytes,
   convert. The easy one.
2. **BMP280** at `0x77` — read the calibration coefficients out of the
   chip and apply the compensation formula from the datasheet.
3. **Dew point** from temperature and humidity, appended to a daily CSV
   with a timestamp, plus a small `latest.json`.

Datasheets: *AHT20 datasheet*, *BST-BMP280-DS001*.

Completed. `logger.py` successfully reads the AHT20 and the BMP280 (including full datasheet compensation formulas), calculates the dew point, logs to CSV/JSON, and auto-pushes to GitHub.
