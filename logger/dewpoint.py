"""Punto de rocío a partir de temperatura y humedad relativa.

Fórmula de Magnus, coeficientes de la OMM (a = 17.62, b = 243.12),
precisa a mejor de 0,1 °C entre -45 y +60 °C.

    gamma = ln(RH / 100) + (a * T) / (b + T)
    Td    = (b * gamma) / (a - gamma)

Esta misma función irá a newton-instrumentation: la resistencia del
secundario se enciende cuando (T - Td) se hace pequeño.
"""

import math

a = 17.62
b = 243.12


def dew_point(temp_c: float, humidity_pct: float) -> float:
    """Devuelve el punto de rocío en grados Celsius.

    temp_c        temperatura del aire, grados Celsius
    humidity_pct  humedad relativa, 0-100

    Humedad <= 0 lanza ValueError. Ningún aire real produce esa lectura en
    un sensor de ±3 puntos, así que es avería o lectura corrupta, no un
    dato con error.

    Humedad > 100 se recorta a 100. Ahí el sensor no está roto, está
    saturado y mojado, y es su error de medida lo que saca el valor del
    rango físico. Con 100 la fórmula devuelve Td = T exactamente, que es
    justo lo que significa aire saturado.
    """
    if humidity_pct <= 0:
        raise ValueError(
            f"Humedad relativa {humidity_pct}, <= 0: punto de rocío indefinido."
        )

    if humidity_pct > 100:
        humidity_pct = 100

    gamma = math.log(humidity_pct / 100) + (a * temp_c) / (b + temp_c)
    Td = (b * gamma) / (a - gamma)
    return Td
