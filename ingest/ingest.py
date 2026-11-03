import asyncio
import logging
import os
import asyncpg

logger = logging.getLogger(__name__)
BORNES = {"wifi_signal" : [-100, 0], "temperature" : [15, 30], "humidity" : [20, 80], "pressure" : [800, 1200], "co2" : [350, 5000]}
UNITES = {"wifi_signal" : "dBm", "temperature" : "°C", "humidity" : "%", "pressure" : "hPa", "co2" : "ppm"}

def valider(capteur, texte):
    if capteur not in BORNES:
        raise ValueError("Capteur inconnu")
    valeur_valide = float(texte)
    minimum = BORNES[capteur][0]
    maximum = BORNES[capteur][1]
    if valeur_valide > maximum:
        raise ValueError("Valeur trop grande")
    elif valeur_valide < minimum:
        raise ValueError("Valeur trop petite")
    return valeur_valide

async def inserer(conn, mesure, valeur_valide):
    unite = UNITES[mesure["capteur"]]
    await conn.execute(
        "INSERT INTO measurements (ts, building, space, point, value, unit) "
        "VALUES (now(), $1, $2, $3, $4, $5)",
        mesure["building"], mesure["space"], mesure["capteur"], valeur_valide, unite)
    logger.info("mesure insérée %s : %s %s", mesure["capteur"], valeur_valide, unite)    

async def consommateur(queue):
    erreurs = {}
    conn = await asyncpg.connect(
            host=os.environ.get("POSTGRES_HOST", "localhost"), port=5432, user="valfld",
            password=os.environ["POSTGRES_PASSWORD"], database="building_twin",
        )
    logger.info("connexion à la base ouverte")
    try:
        while True:
            mesure = await queue.get()             
            if mesure is None:
                break                   
            try:
                valeur = valider(mesure["capteur"], mesure["valeur"])         
            except ValueError as e:
                logger.warning("erreur détecté %s : %s (%s)", mesure["capteur"], mesure["valeur"], e)
                erreurs[mesure["capteur"]] = erreurs.get(mesure["capteur"], 0) + 1
                continue
            try:
                await inserer(conn, mesure, valeur)
            except asyncpg.PostgresError as f:
                logger.error("mesure perdue %s : %s (%s)", mesure["capteur"], mesure["valeur"], f)
                erreurs[mesure["capteur"]] = erreurs.get(mesure["capteur"], 0) + 1
    finally:
        await conn.close()
        logger.info("connexion à la base fermée, erreurs : %s", erreurs)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                    format="%(name)s %(asctime)s %(levelname)s %(message)s")
    async def test():
        mesures = [
    {"capteur": "co2", "valeur": "abc"},
    {"capteur": "co2", "valeur": "abc"},
    {"capteur": "co2", "valeur": "50000"}, 
    {"capteur": "co2", "valeur": "850"},
    {"capteur": "co2", "valeur": "950"},
    {"capteur": "co2", "valeur": "870"},]
        queue = asyncio.Queue()
        for m in mesures:
            queue.put_nowait(m)
        queue.put_nowait(None)   
        await consommateur(queue)         

    asyncio.run(test())