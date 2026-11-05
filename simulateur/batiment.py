import asyncio
import os
from datetime import datetime

import aiomqtt

TOPIC_CO2 = "bt/sim/r0-bureau-01/co2"


CO2_EXTERIEUR = 420        # ppm
APPORT_PAR_PERSONNE = 10   # ppm par minute
VOLUME_BUREAU = 12 * 2.5 # m³
OCCUPANTS_PREVUS = 2
DEBIT_AIR_NEUF = OCCUPANTS_PREVUS * 25 # m³/h
RENOUVELLEMENT = DEBIT_AIR_NEUF / VOLUME_BUREAU / 60    # RSDT

def prochain_co2(co2, occupants):
    apport = occupants * APPORT_PAR_PERSONNE
    ecart = co2 - CO2_EXTERIEUR
    evacuation = ecart * RENOUVELLEMENT
    return co2 + apport - evacuation


def occupants_bureau(heure):
    if heure < 8:
        return 0
    elif heure < 12:
        return 2
    elif heure < 14:
        return 0
    elif heure < 18:
        return 2
    else:
        return 0

async def simuler():
    co2 = CO2_EXTERIEUR
    async with aiomqtt.Client(os.environ.get("MQTT_HOST", "localhost")) as client:
        while True:
            heure = datetime.now().hour
            co2 = prochain_co2(co2, occupants_bureau(heure))
            await client.publish(TOPIC_CO2, str((round(co2))))
            await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(simuler())
        
 