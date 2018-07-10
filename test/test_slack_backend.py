import pytest
import os
import requests
from unittest.mock import patch, call, Mock

from app.dispatcher import Dispatcher
from app.dispatcher.backends.slack import SlackBackend

@pytest.fixture
def backend_instance():
    return SlackBackend()

@patch.dict(os.environ, {})
def test_missing_slack_webhook_env__prints_warning_to_logger(backend_instance):
    mock_logger = Mock()
    backend_instance.process_payload([], mock_logger)
    assert mock_logger.warn.mock_calls == [call('Please enable the Slack backend by setting the BACKEND_SLACK_URL environment variable.')]

@patch('requests.post', return_value=Mock())
@patch.dict(os.environ, {'BACKEND_SLACK_URL':'https://dummyslack.dev/123/'})
def test_two_notifications__posts_humanized_description_to_slack__two_times(mocked_post, backend_instance):

    mock_logger = Mock()
    mocked_post.return_value.status_code = 200

    backend_instance.process_payload(
        [
            {"humanized_description": "test1"},
            {"humanized_description": "test2"}
        ],
        mock_logger)

    assert mocked_post.mock_calls == [
        call(
            "https://dummyslack.dev/123/",
            data='{"text": "test1"}',
            headers={"Content-Type": "application/json"}),
        call(
            "https://dummyslack.dev/123/",
            data='{"text": "test2"}',
            headers={"Content-Type": "application/json"})
        ]

@patch('requests.post', side_effect=requests.exceptions.RequestException("Simulated error"))
@patch.dict(os.environ, {'BACKEND_SLACK_URL':'https://dummyslack.dev/123/'})
def test_notification__request_exception_while_posting__log_error_to_logger(mocked_post, backend_instance):
    mock_logger = Mock()
    backend_instance.process_payload([{"humanized_description": "test1"}], mock_logger)
    assert mock_logger.error.mock_calls == [call("Failed to post the message to Slack: Simulated error")]

@patch('requests.post')
@patch.dict(os.environ, {'BACKEND_SLACK_URL':'https://dummyslack.dev/123/'})
def test_notification__http_response_non_200__log_error_to_logger(mocked_post, backend_instance):
    mock_logger = Mock()
    mocked_post.return_value.status_code = 500
    backend_instance.process_payload([{"humanized_description": "test1"}], mock_logger)
    assert mock_logger.error.mock_calls == [call("Posted the message to Slack successfully, but received response code: 500")]
