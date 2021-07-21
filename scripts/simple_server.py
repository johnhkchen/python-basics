""" Websocket Message Passing Server """

import json
import asyncio
import websockets

CLIENTS = set()


def project_event(project_id):
    return json.dumps({"type": "project", "PROJECT_ID": project_id})


async def project_request_service(websocket, path):
    # This is the main server process
    CLIENTS.add(websocket)
    try:
        project_id = json.loads(await websocket.recv())["project_id"]
        for client in CLIENTS:
            await client.send(project_event(project_id))
    finally:
        CLIENTS.remove(websocket)


server = websockets.serve(project_request_service, "localhost", 8765)
asyncio.get_event_loop().run_until_complete(server)
asyncio.get_event_loop().run_forever()
