''' Websocket Message Passing Server '''

import asyncio
import json
import websockets


class Server():
    version = '0.2.0'

    def __init__(self):
        self.connections = set()

    def connections_event(self):
        return json.dumps({"type": "connections", "count": len(self.connections)})

    def project_event(self):
        return json.dumps({"type": "project"})

    def broadcast_users(self):
        if self.connections:
            for client in self.connections:
                client.send(self.connections_event())

    def unregister(self, client):
        self.connections.remove(client)
        self.broadcast_users()

    def register(self, client):
        self.connections.add(client)
        self.broadcast_users()

    def start(self):
        raise NotImplementedError
