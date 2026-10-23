import asyncio
import logging

from ecoute import ecouter
from ingest import consommateur
        

async def main():
    queue = asyncio.Queue()
    await asyncio.gather(ecouter(queue), consommateur(queue))   

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                    format="%(name)s %(asctime)s %(levelname)s %(message)s")   
    asyncio.run(main())