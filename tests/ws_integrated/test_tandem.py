""" Test server and client together """
import asyncio
import pytest
import random
from unittest.mock import Mock, MagicMock

import websockets
from ws_client.client import Client
from ws_server.server import Server

import nest_asyncio

nest_asyncio.apply()


@pytest.fixture
def my_server():
    yield Server()


@pytest.fixture
def my_client():
    yield Client()


@pytest.fixture
def port():
    port = None
    forbidden_ports = set()
    while port in forbidden_ports or port is None:
        port = random.randint(1000, 30000)
    return port


def uri(port):
    return "ws://{}:{}".format("localhost", port)


@pytest.mark.asyncio
async def test_init_server(my_server, port):
    server = await my_server.start_server(port)
    assert server is not None


@pytest.mark.asyncio
async def test_init_server_client(my_server, my_client, port):
    server = await my_server.start_server(port)
    await my_client.connect(uri(port))
    await asyncio.sleep(0.2)  # Wait a bit
    assert my_server.num_connections() > 0
    await asyncio.sleep(0.2)  # Wait a bit
