"""Toma una medición del sensor y la escribe en data/latest.json y un CSV diario.

Una sola pasada: lee, calcula, escribe y termina. De repetirla cada
5 minutos se encargará el temporizador de systemd, no este fichero.
"""

import json
import csv
from datetime import datetime, timezone
from pathlib import Path

import aht20
import bmp280
from dewpoint import dew_point


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def main():
    temperatura_aht, humedad = aht20.read()
    temperatura_bmp, presion = bmp280.read()
    
    # Podemos hacer una media de las dos temperaturas o usar la del AHT20
    # Usaremos la del AHT20 para el punto de rocío y los registros principales,
    # ya que suele estar mejor ventilado, pero guardaremos también la presión.
    temperatura = temperatura_aht

    rocio = dew_point(temperatura, humedad)
    
    ahora = datetime.now(timezone.utc)
    momento_iso = ahora.isoformat()
    dia_str = ahora.strftime("%Y-%m-%d")

    datos = {
        "timestamp": momento_iso,
        "temp_c": round(temperatura, 2),
        "humidity_pct": round(humedad, 2),
        "pressure_hpa": round(presion, 2),
        "dew_point_c": round(rocio, 2),
    }

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Escribir latest.json
    (DATA_DIR / "latest.json").write_text(json.dumps(datos, indent=2))

    # Añadir a CSV
    csv_path = DATA_DIR / f"{dia_str}.csv"
    file_exists = csv_path.exists()
    
    with open(csv_path, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "temp_c", "humidity_pct", "pressure_hpa", "dew_point_c"])
        writer.writerow([
            datos["timestamp"],
            datos["temp_c"],
            datos["humidity_pct"],
            datos["pressure_hpa"],
            datos["dew_point_c"]
        ])

    print(datos)


if __name__ == "__main__":
    main()
