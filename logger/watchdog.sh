#!/bin/bash
# Avisa al movil si el logger deja de escribir.
#
# Vive fuera de logger.py a proposito: lo que mata al logger (un rebase
# en conflicto, el I2C caido, la SD llena) no debe poder matar tambien al
# aviso. Por eso es su propio timer, su propio proceso, y no importa nada
# del logger.

set -u

FICHERO="/home/david/pi-weather-logger/data/latest.json"
MAX_MIN=45                                  # tres ciclos de 15 min perdidos
CONF="/home/david/.weatherpi-ntfy"          # una linea: el nombre del canal
ESTADO="/tmp/weatherpi-watchdog-avisado"

# El canal de ntfy es publico para quien sepa su nombre, asi que no puede
# entrar en el repo. Vive fuera, en el home.
if [ ! -r "$CONF" ]; then
    echo "Falta $CONF con el nombre del canal de ntfy. Sin avisos."
    exit 1
fi
CANAL=$(head -n 1 "$CONF" | tr -d '[:space:]')

avisar() {
    curl -s -m 10 \
         -H "Title: WeatherPi" \
         -H "Tags: warning" \
         -d "$1" \
         "https://ntfy.sh/$CANAL" > /dev/null
}

if [ ! -f "$FICHERO" ]; then
    EDAD_MIN=999999
else
    EDAD_S=$(( $(date +%s) - $(date -r "$FICHERO" +%s) ))
    EDAD_MIN=$(( EDAD_S / 60 ))
fi

# El fichero de estado evita repetir el aviso cada 15 min mientras dure la
# averia: uno al caer, uno al recuperarse. Vive en /tmp a proposito, para
# que un reinicio vuelva a avisar si sigue rota.
if [ "$EDAD_MIN" -gt "$MAX_MIN" ]; then
    if [ ! -f "$ESTADO" ]; then
        avisar "Sin datos desde hace ${EDAD_MIN} min. Mira: journalctl -u logger.service -n 30"
        touch "$ESTADO"
        echo "Aviso enviado: ${EDAD_MIN} min sin datos."
    else
        echo "Sigue caido (${EDAD_MIN} min). Aviso ya enviado, no repito."
    fi
else
    if [ -f "$ESTADO" ]; then
        avisar "Recuperado. Ultimo dato hace ${EDAD_MIN} min."
        rm -f "$ESTADO"
        echo "Recuperado tras la averia."
    else
        echo "Todo bien: ultimo dato hace ${EDAD_MIN} min."
    fi
fi
