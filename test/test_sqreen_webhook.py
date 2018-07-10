import pytest
import json
from unittest import mock

from app.dispatcher import Dispatcher
from app import app

WEBHOOK_PATH = '/sqreenhook'

TEST_PAYLOAD = b'[{"sqreen_payload_type":"security_event","application_id":"5b2229397f4c18001bd6c62c","event_category":"http_error","date_occurred":"2018-06-17T19:12:53.862000+00:00","environment":"development","event_kind":"bot_scanning","humanized_description":"Potential Automated Vulnerability discovery from 127.0.0.1","risk":50,"id":"5b26b2b6d1d76b0007c10858","application_name":"sqreened_application","ips":[{"is_tor":false,"address":"127.0.0.1","date_resolved":"2018-06-17T19:12:54.005000+00:00"}],"url":"https://my.sqreen.io/application/38cc5939802c4b63a2b81ec1dba90c9fd67b40c0d55d4d3e85c5efc8adc1377d/events/5b26b2b6d1d76b0007c10858"}]'
TEST_PAYLOAD_SIG = b'a2d35e5845f6a34511994e68ff18a0f8e043e59eb73e804e73c66c664d972b9a'

@pytest.fixture
def mock_dispatcher():
    return mock.Mock()

@pytest.fixture
def client(mock_dispatcher):
    def bind_mock_dispatcher(binder):
        binder.bind(
            Dispatcher,
            to=mock_dispatcher
        )

    test_app = app.create_app([bind_mock_dispatcher])
    test_app.testing = True
    return test_app.test_client()

def test_methodGET_returns405(client):
    """Respond with 405 to GET requests (only POST should be allowed)."""
    rv = client.get(WEBHOOK_PATH)
    assert rv.status_code == 405

def test_invalidSignature_returns400(client):
    """Respond with 400 to POST requests with invalid signature."""
    rv = client.post(WEBHOOK_PATH, data=TEST_PAYLOAD, headers={"X-Sqreen-Integrity": "invalid_signature"})
    assert rv.status_code == 400

def test_validSignature_returnsEmptySuccess(client):
    """Respond with an empty (200) response to POST requests with a valid signature."""
    rv = client.post(WEBHOOK_PATH, data=TEST_PAYLOAD, headers={"X-Sqreen-Integrity": TEST_PAYLOAD_SIG})
    assert rv.status_code == 200
    assert rv.data == b''

def test_validSignature_invokesDispatcher(client, mock_dispatcher):
    """Tests that a valid notification is given to the dispatcher for processing."""
    client.post(WEBHOOK_PATH, data=TEST_PAYLOAD, headers={"X-Sqreen-Integrity": TEST_PAYLOAD_SIG})
    expected_object = json.loads(TEST_PAYLOAD)
    mock_dispatcher.process_payload.assert_called_with(expected_object)

