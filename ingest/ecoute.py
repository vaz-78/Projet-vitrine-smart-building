import aiomqtt


async def ecouter(queue):
    async with aiomqtt.Client("localhost") as client:
        await client.subscribe("bt/home/+/+")
        async for message in client.messages:
            topic = message.topic.value.split("/")
            capteur = topic[3]
            building = topic[1]
            space = topic[2]
            mesure = {"building": building, "space": space, "capteur": capteur, "valeur": message.payload.decode()}
            if capteur == message.retain:
                continue
            await queue.put(mesure)