import aiomqtt


async def ecouter(queue):
    async with aiomqtt.Client("localhost") as client:
        await client.subscribe("bt/home/space-101/sensor/+/state")          
        async for message in client.messages:
            topic = message.topic.value.split("/")
            capteur = topic[4]
            building = topic[1]
            space = topic[2]
            mesure = {"building": building, "space": space, "capteur": capteur, "valeur": message.payload.decode()}
            if capteur == "uptime" or message.retain:
                continue
            await queue.put(mesure)