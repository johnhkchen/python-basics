import asyncio
import pytest
from unittest.mock import Mock, MagicMock
import random

import websockets
import nest_asyncio

nest_asyncio.apply()

from ws_client.client import Client


@pytest.fixture
def hostname():
    return "localhost"


@pytest.fixture
def port():
    return 8765


@pytest.fixture
def uri(hostname, port):
    yield "ws://{}:{}".format(hostname, port)


@pytest.fixture
def my_client():
    yield Client()


@pytest.fixture
def mock_websocket():
    socket = Mock()
    socket.last_message_out = None

    def record_outgoing_message(message):
        socket.last_message_out = message

    socket.send = MagicMock(side_effect=record_outgoing_message)
    yield socket


@pytest.fixture
@pytest.mark.asyncio
async def echo_serve(hostname, port, event_loop):
    # for testing basic connection
    async def echo(websocket, path):
        msg = await websocket.recv()
        await websocket.send(msg)

    echo_server = await websockets.serve(echo, hostname, port)
    yield echo_server
    echo_server.close()
    await asyncio.sleep(0.05)


def test_client_importable(my_client):
    assert my_client is not None


def test_project_request_message(my_client):
    project_id = random.randint(1, 20)
    expected_msg = '{"type": "project", "project_id": ' + str(project_id) + "}"
    assert my_client.project_request(project_id) == expected_msg


def test_echo_server(echo_serve):
    assert echo_serve is not None


def test_echo_server_echo(echo_serve, uri, event_loop):
    async def hello():
        async with websockets.connect(uri) as websocket:
            await websocket.send("hey")
            response = await websocket.recv()
            assert response == "hey"

    event_loop.run_until_complete(hello())


@pytest.mark.asyncio
async def test_client_request_project(echo_serve, my_client, uri):
    project_id = random.randint(1, 20)
    response = await my_client.connect_and_request_project(uri, project_id)
    assert response == '{"type": "project", "project_id": ' + str(project_id) + "}"
