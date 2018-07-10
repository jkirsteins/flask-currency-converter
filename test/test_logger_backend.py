import pytest
import os
from unittest.mock import call, Mock

from app.dispatcher import Dispatcher
from app.dispatcher.backends.logger import LoggerBackend

@pytest.fixture
def backend_instance():
    return LoggerBackend()

def test_two_notifications__prints_humanized_description_to_logger__two_times(backend_instance):
    logger = Mock()

    backend_instance.process_payload(
        [
            {"humanized_description": "test1"},
            {"humanized_description": "test2"}
        ],
        logger)

    assert logger.info.mock_calls == [
        call("test1"),
        call("test2")
        ]
