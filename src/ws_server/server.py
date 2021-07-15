''' Websocket Message Passing Server '''

import asyncio
import json
import websockets


class Server():
    version = '0.2.0'

    def __init__(self):
        self.connections = set()
        self.project_id = None

    def connections_event(self):
        return json.dumps({"type": "connections", "count": len(self.connections)})

    def project_event(self):
        return json.dumps({"type": "project", "project_id": self.project_id})

    def notify_connections(self):
        if self.connections:
            for client in self.connections:
                client.send(self.connections_event())

    def notify_project(self):
        if self.project_id:
            for client in self.connections:
                client.send(self.project_event())

    def register(self, client):
        self.connections.add(client)
        self.notify_connections()

    def unregister(self, client):
        self.connections.remove(client)
        self.notify_connections()

    def request_project(self, project_id):
        self.project_id = project_id
        self.notify_project()

    def start(self):
        raise NotImplementedError
