""" Websocket Message Passing Server """

import json
import websockets


class Server:
    version = "0.3.0"

    def __init__(self):
        self.connections = set()
        self.project_id = None

    def connections_event(self):
        return json.dumps({"type": "connections", "count": len(self.connections)})

    def project_event(self):
        return json.dumps({"type": "project", "project_id": self.project_id})

    async def notify_connections(self):
        if self.connections:
            for client in self.connections:
                client.send(self.connections_event())

    async def notify_project(self):
        if self.project_id:
            for client in self.connections:
                client.send(self.project_event())

    async def register(self, client):
        self.connections.add(client)
        await self.notify_connections()

    async def unregister(self, client):
        self.connections.remove(client)
        await self.notify_connections()

    async def request_project(self, project_id):
        self.project_id = project_id
        await self.notify_project()

    async def project_request_service(self, websocket, path):
        # This is the main server process
        await self.register(websocket)
        try:
            pass
        finally:
            await self.unregister(websocket)

    def get_service(self):
        return websockets.serve(self.project_request_service, "localhost", 6789)
