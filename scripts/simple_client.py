""" WebSocket Client """

import json
import asyncio
import websockets


def project_request(project_id):
    return json.dumps({"type": "project", "project_id": project_id})


async def request_project(project_id):
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        await websocket.send(project_request(project_id))


import random
import time

for x in range(1000):
    time.sleep(0.3)
    project_id = random.randint(0, 15)
    responses = asyncio.run(request_project(project_id))
