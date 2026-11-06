import aiomqtt
import os


async def ecouter(queue):
    async with aiomqtt.Client(os.environ.get("MQTT_HOST", "localhost")) as client:
        await client.subscribe("bt/+/+/+")
        async for message in client.messages:
            topic = message.topic.value.split("/")
            capteur = topic[3]
            building = topic[1]
            space = topic[2]
            mesure = {"building": building, "space": space, "capteur": capteur, "valeur": message.payload.decode()}
            if message.retain:
                continue
            elif capteur == 'status':
                continue
            await queue.put(mesure)