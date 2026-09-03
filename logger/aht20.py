""" En este módulo se implementa la lectura 
de datos del sensor AHT20 mediante el protocolo I2C. """

import time
from smbus2 import SMBus, i2c_msg


DIRECCION_AHT20 = 0x38  # Dirección I2C del sensor AHT20

def read():
    with SMBus(1) as bus:
        bus.write_i2c_block_data(DIRECCION_AHT20, 0xAC, [0x33, 0x00])

        time.sleep(0.08)

        msg = i2c_msg.read(DIRECCION_AHT20, 7)
        bus.i2c_rdwr(msg)
        datos = list(msg)

    raw_h = (datos[1] << 12) | (datos[2] << 4) | (datos[3] >> 4)
    raw_t = ((datos[3] & 0x0F) << 16) | (datos[4] << 8) | datos[5]
    humedad     = raw_h / 2**20 * 100
    temperatura = raw_t / 2**20 * 200 - 50

    return temperatura, humedad

if __name__ == "__main__":
    datos = read()
    print(datos)