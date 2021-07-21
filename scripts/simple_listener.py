""" WebSocket Client """

import json
import asyncio
import websockets


def project_request(project_id):
    return json.dumps({"type": "project", "project_id": project_id})


async def consumer(message):
    if json.loads(message)["type"] == "project":
        print("< " + message)


async def listener():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        async for message in websocket:
            await consumer(message)


responses = asyncio.run(listener())
