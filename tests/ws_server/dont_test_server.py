""" Tests for the prototype Piper messagine service """

import random
import pytest
import asyncio
from unittest.mock import Mock, MagicMock

import nest_asyncio

nest_asyncio.apply()

from ws_server.server import Server


@pytest.fixture
def my_server():
    my_server = Server()
    yield my_server


@pytest.fixture
def mock_client():
    class MockClientFactory:
        def get(self):
            mock_client = Mock()
            mock_client.message_count = 0
            mock_client.last_message = None

            def record_message(message):
                mock_client.message_count += 1
                mock_client.last_message = message

            mock_client.send = MagicMock(side_effect=record_message)

            return mock_client

    yield MockClientFactory()


@pytest.fixture
def pipercode_client(mock_client):
    yield mock_client.get()


@pytest.fixture
def storymode_client(mock_client):
    yield mock_client.get()


def test_server_connections_event(my_server):
    expected_msg = '{"type": "connections", "count": 0}'
    return_msg = my_server.connections_event()
    assert return_msg == expected_msg


@pytest.mark.asyncio
async def test_server_connections_after_registration(my_server, pipercode_client):
    expected_msg = '{"type": "connections", "count": 1}'
    await my_server.register(pipercode_client)
    assert my_server.connections_event() == expected_msg


def test_server_project_event(my_server):
    expected_msg = '{"type": "project", "project_id": null}'
    assert my_server.project_event() == expected_msg


def test_mock_client_send(pipercode_client):
    user_message = '{"type": "user"}'
    project_message = '{"type": "project"}'

    assert pipercode_client.message_count == 0
    assert pipercode_client.last_message is None

    pipercode_client.send(user_message)
    assert pipercode_client.message_count == 1
    assert pipercode_client.last_message == user_message

    pipercode_client.send(project_message)
    assert pipercode_client.message_count == 2
    assert pipercode_client.last_message == project_message


def test_mock_client_independence(pipercode_client, storymode_client):
    """Should be able to have multiple clients receive different messages"""
    user_message = '{"type": "user"}'
    project_message = '{"type": "project"}'

    assert pipercode_client.message_count is 0
    assert pipercode_client.last_message is None
    assert storymode_client.message_count is 0
    assert storymode_client.last_message is None

    pipercode_client.send(user_message)

    assert pipercode_client.message_count is 1
    assert pipercode_client.last_message is user_message
    assert storymode_client.message_count is 0
    assert storymode_client.last_message is None

    storymode_client.send(user_message)

    assert pipercode_client.message_count is 1
    assert pipercode_client.last_message is user_message
    assert storymode_client.message_count is 1
    assert storymode_client.last_message is user_message

    storymode_client.send(project_message)

    assert pipercode_client.message_count is 1
    assert pipercode_client.last_message is user_message
    assert storymode_client.message_count is 2
    assert storymode_client.last_message is project_message


@pytest.mark.asyncio
async def test_server_client_registration(my_server, pipercode_client):
    """Server should be able to register a new client"""
    await my_server.register(pipercode_client)
    assert pipercode_client in my_server.connections


@pytest.mark.asyncio
async def test_client_registration_confirmation(my_server, pipercode_client):
    """Client should get a message confirming new user"""
    await my_server.register(pipercode_client)
    assert pipercode_client.message_count > 0


@pytest.mark.asyncio
async def test_multi_client_regitration(my_server, pipercode_client, storymode_client):
    await my_server.register(pipercode_client)
    assert pipercode_client.message_count is 1
    await my_server.register(storymode_client)
    assert storymode_client.message_count is 1


@pytest.mark.asyncio
async def test_clients_receive_connections_update(
    my_server, pipercode_client, storymode_client
):
    await my_server.register(pipercode_client)
    await my_server.register(storymode_client)
    assert pipercode_client.message_count is 2
    assert storymode_client.message_count is 1


@pytest.mark.asyncio
async def test_client_unregister(my_server, pipercode_client, storymode_client):
    await my_server.register(pipercode_client)
    assert len(my_server.connections) == 1
    await my_server.register(storymode_client)
    assert len(my_server.connections) == 2
    await my_server.unregister(storymode_client)
    assert len(my_server.connections) == 1
    await my_server.unregister(pipercode_client)
    assert len(my_server.connections) == 0


@pytest.mark.asyncio
async def test_client_unregister_message(my_server, pipercode_client, storymode_client):
    await my_server.register(pipercode_client)
    await my_server.register(storymode_client)
    expected_msg = '{"type": "connections", "count": 2}'
    assert pipercode_client.last_message == expected_msg
    await my_server.unregister(storymode_client)
    expected_msg = '{"type": "connections", "count": 1}'
    assert pipercode_client.last_message == expected_msg
    await my_server.unregister(pipercode_client)
    assert len(my_server.connections) == 0
    # N messages expected:
    # 1: PiperCode registered
    # 2: StoryMode registered
    # 3: StoryMode unregistered
    assert pipercode_client.message_count == 3


@pytest.mark.asyncio
async def test_can_set_project_id(my_server):
    project_id_1, project_id_2 = random.randint(0, 20), random.randint(0, 20)
    expected_msg = '{"type": "project", "project_id": ' + str(project_id_1) + "}"
    await my_server.request_project(project_id_1)
    assert my_server.project_event() == expected_msg


@pytest.mark.asyncio
async def test_can_change_project_id(my_server):
    project_id_1, project_id_2 = random.randint(0, 20), random.randint(0, 20)
    expected_msg = '{"type": "project", "project_id": ' + str(project_id_2) + "}"

    await my_server.request_project(project_id_1)
    await my_server.request_project(project_id_2)
    assert my_server.project_event() == expected_msg


@pytest.mark.asyncio
async def test_project_request(my_server, pipercode_client, storymode_client):
    project_id = random.randint(0, 20)
    expected_msg = '{"type": "project", "project_id": ' + str(project_id) + "}"

    await my_server.register(pipercode_client)
    await asyncio.sleep(0.05)  # Resolve race conditions
    await my_server.register(storymode_client)
    await asyncio.sleep(0.05)  # Resolve race conditions
    await my_server.request_project(project_id)
    await asyncio.sleep(0.2)  # Resolve race conditions
    assert (
        pipercode_client.message_count == 3
        and pipercode_client.last_message == expected_msg
    )


@pytest.mark.asyncio
async def test_start_server(my_server):
    server = await my_server.start_server()
    assert server is not None


@pytest.mark.asyncio
async def test_start_server_port(my_server):
    port = random.randint(1, 30000)
    server = await my_server.start_server(port)
    assert server is not None


@pytest.mark.asyncio
async def test_start_server_port(my_server):
    port = random.randint(1, 30000)
    server = await my_server.start_server(port)
    assert server is not None
