''' Tests for the prototype Piper messagine service '''
from unittest.mock import Mock, MagicMock
import random
import pytest

from ws_server.server import Server


@pytest.fixture
def my_server():
    return Server()


@pytest.fixture
def mock_client():
    class MockClientFactory():
        def get(self):
            mock_client = Mock()
            mock_client.message_count = 0
            mock_client.last_message = None

            def record_message(message):
                mock_client.message_count += 1
                mock_client.last_message = message
            mock_client.send = MagicMock(side_effect=record_message)

            return mock_client

    return MockClientFactory()


@pytest.fixture
def pipercode_client(mock_client):
    return mock_client.get()


@pytest.fixture
def storymode_client(mock_client):
    return mock_client.get()


@pytest.mark.skip(reason="Not implemented")
def test_server_has_start_method(my_server):
    my_server.start()


def test_server_connections_event(my_server):
    EXPECTED_MSG = '{"type": "connections", "count": 0}'
    assert my_server.connections_event() == EXPECTED_MSG


def test_server_connections_after_registration(my_server, pipercode_client):
    EXPECTED_MSG = '{"type": "connections", "count": 1}'
    my_server.register(pipercode_client)
    assert my_server.connections_event() == EXPECTED_MSG


def test_server_project_event(my_server):
    EXPECTED_MSG = '{"type": "project", "project_id": null}'
    assert my_server.project_event() == EXPECTED_MSG


def test_mock_client_send(pipercode_client):
    SAMPLE_USER_MESSAGE = '{"type": "user"}'
    SAMPLE_PROJECT_MESSAGE = '{"type": "project"}'

    assert pipercode_client.message_count == 0
    assert pipercode_client.last_message is None

    pipercode_client.send(SAMPLE_USER_MESSAGE)
    assert pipercode_client.message_count == 1
    assert pipercode_client.last_message == SAMPLE_USER_MESSAGE

    pipercode_client.send(SAMPLE_PROJECT_MESSAGE)
    assert pipercode_client.message_count == 2
    assert pipercode_client.last_message == SAMPLE_PROJECT_MESSAGE


def test_mock_client_independence(pipercode_client, storymode_client):
    ''' Should be able to have multiple clients receive different messages '''
    SAMPLE_USER_MESSAGE = '{"type": "user"}'
    SAMPLE_PROJECT_MESSAGE = '{"type": "project"}'

    assert pipercode_client.message_count is 0
    assert pipercode_client.last_message is None
    assert storymode_client.message_count is 0
    assert storymode_client.last_message is None

    pipercode_client.send(SAMPLE_USER_MESSAGE)

    assert pipercode_client.message_count is 1
    assert pipercode_client.last_message is SAMPLE_USER_MESSAGE
    assert storymode_client.message_count is 0
    assert storymode_client.last_message is None

    storymode_client.send(SAMPLE_USER_MESSAGE)

    assert pipercode_client.message_count is 1
    assert pipercode_client.last_message is SAMPLE_USER_MESSAGE
    assert storymode_client.message_count is 1
    assert storymode_client.last_message is SAMPLE_USER_MESSAGE

    storymode_client.send(SAMPLE_PROJECT_MESSAGE)

    assert pipercode_client.message_count is 1
    assert pipercode_client.last_message is SAMPLE_USER_MESSAGE
    assert storymode_client.message_count is 2
    assert storymode_client.last_message is SAMPLE_PROJECT_MESSAGE


def test_server_client_registration(my_server, pipercode_client):
    ''' Server should be able to register a new client '''
    my_server.register(pipercode_client)
    assert pipercode_client in my_server.connections


def test_client_registration_confirmation(my_server, pipercode_client):
    ''' Client should get a message confirming new user'''
    my_server.register(pipercode_client)
    assert pipercode_client.message_count > 0


def test_multi_client_regitration(my_server, pipercode_client, storymode_client):
    my_server.register(pipercode_client)
    assert pipercode_client.message_count is 1
    my_server.register(storymode_client)
    assert storymode_client.message_count is 1


def test_clients_receive_connections_update(my_server, pipercode_client, storymode_client):
    my_server.register(pipercode_client)
    my_server.register(storymode_client)
    assert pipercode_client.message_count is 2
    assert storymode_client.message_count is 1


def test_client_unregister(my_server, pipercode_client, storymode_client):
    my_server.register(pipercode_client)
    assert len(my_server.connections) == 1
    my_server.register(storymode_client)
    assert len(my_server.connections) == 2
    my_server.unregister(storymode_client)
    assert len(my_server.connections) == 1
    my_server.unregister(pipercode_client)
    assert len(my_server.connections) == 0


def test_client_unregister_message(my_server, pipercode_client, storymode_client):
    my_server.register(pipercode_client)
    my_server.register(storymode_client)
    EXPECTED_MSG = '{"type": "connections", "count": 2}'
    assert pipercode_client.last_message == EXPECTED_MSG
    my_server.unregister(storymode_client)
    EXPECTED_MSG = '{"type": "connections", "count": 1}'
    assert pipercode_client.last_message == EXPECTED_MSG
    my_server.unregister(pipercode_client)
    assert len(my_server.connections) == 0
    # N messages expected:
    # 1: PiperCode registered
    # 2: StoryMode registered
    # 3: StoryMode unregistered
    assert pipercode_client.message_count == 3


def test_can_set_project_id(my_server):
    project_id_1, project_id_2 = random.randint(0, 20), random.randint(0, 20)
    my_server.request_project(project_id_1)
    EXPECTED_MSG = '{"type": "project", "project_id": ' + str(project_id_1)+'}'
    assert my_server.project_event() == EXPECTED_MSG
    my_server.request_project(project_id_2)
    EXPECTED_MSG = '{"type": "project", "project_id": ' + str(project_id_2)+'}'
    assert my_server.project_event() == EXPECTED_MSG


def test_project_request(my_server, pipercode_client, storymode_client):
    PROJECT_ID = random.randint(0, 20)
    EXPECTED_MSG = '{"type": "project", "project_id": ' + str(PROJECT_ID)+'}'
    my_server.register(pipercode_client)
    my_server.register(storymode_client)
    my_server.request_project(PROJECT_ID)
    assert pipercode_client.message_count == 3
    assert pipercode_client.last_message == EXPECTED_MSG
