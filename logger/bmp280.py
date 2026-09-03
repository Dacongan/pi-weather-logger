import time
import struct
from smbus2 import SMBus

DIRECCION_BMP280 = 0x77

def read():
    with SMBus(1) as bus:
        # Check ID
        chip_id = bus.read_byte_data(DIRECCION_BMP280, 0xD0)
        if chip_id != 0x58:
            raise RuntimeError(f"Chip ID not 0x58 (found {hex(chip_id)})")

        # Read calibration data (0x88 to 0xA1, 24 bytes)
        calib = bus.read_i2c_block_data(DIRECCION_BMP280, 0x88, 24)
        
        # Unpack calibration
        # T1 (H), T2 (h), T3 (h)
        # P1 (H), P2 (h), P3 (h), P4 (h), P5 (h), P6 (h), P7 (h), P8 (h), P9 (h)
        # H is unsigned short, h is signed short. All little-endian (<)
        dig = struct.unpack('<HhhHhhhhhhhh', bytes(calib))
        dig_T = dig[0:3]
        dig_P = dig[3:12]

        # Configure and start measurement
        # ctrl_meas (0xF4): osrs_t(2)=010, osrs_p(5)=101, mode(2)=01
        bus.write_byte_data(DIRECCION_BMP280, 0xF4, 0x27)
        
        # Wait for measurement to complete
        time.sleep(0.05)
        
        # Read raw data (0xF7 to 0xFC, 6 bytes)
        # press_msb, press_lsb, press_xlsb, temp_msb, temp_lsb, temp_xlsb
        data = bus.read_i2c_block_data(DIRECCION_BMP280, 0xF7, 6)

    raw_p = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
    raw_t = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)

    # Temperature compensation
    var1 = (((raw_t >> 3) - (dig_T[0] << 1)) * dig_T[1]) >> 11
    var2 = (((((raw_t >> 4) - dig_T[0]) * ((raw_t >> 4) - dig_T[0])) >> 12) * dig_T[2]) >> 14
    t_fine = var1 + var2
    T = ((t_fine * 5 + 128) >> 8) / 100.0

    # Pressure compensation
    var1 = t_fine - 128000
    var2 = var1 * var1 * dig_P[5]
    var2 = var2 + ((var1 * dig_P[4]) << 17)
    var2 = var2 + (dig_P[3] << 35)
    var1 = ((var1 * var1 * dig_P[2]) >> 8) + ((var1 * dig_P[1]) << 12)
    var1 = (((1 << 47) + var1)) * dig_P[0] >> 33

    if var1 == 0:
        P = 0
    else:
        p = 1048576 - raw_p
        p = (((p << 31) - var2) * 3125) // var1
        var1 = (dig_P[8] * (p >> 13) * (p >> 13)) >> 25
        var2 = (dig_P[7] * p) >> 19
        p = ((p + var1 + var2) >> 8) + (dig_P[6] << 4)
        P = (p / 256.0) / 100.0 # Convert to hPa

    return T, P

if __name__ == "__main__":
    t, p = read()
    print(f"Temp: {t} C, Pressure: {p} hPa")
