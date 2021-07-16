""" WebSocket Client """

import json
import logging
import websockets


class Client:
    version = "0.3.0"

    async def connect(self, uri):
        try:
            async with websockets.connect(uri) as websocket:
                self._websocket = websocket
        except ConnectionRefusedError:
            logging.warning("No connection available.")

    def project_request(self, project_id):
        return json.dumps({"type": "project", "project_id": project_id})

    async def connect_and_request_project(self, uri, project_id):
        async with websockets.connect(uri) as websocket:
            await websocket.send(self.project_request(project_id))
            response = await websocket.recv()
            return response
