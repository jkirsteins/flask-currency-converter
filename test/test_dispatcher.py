import pytest
from unittest.mock import Mock, call

from app.dispatcher import Dispatcher
from app.dispatcher.backends.abstract_base_backend import AbstractBaseBackend
from app.dispatcher.backends.slack import SlackBackend
from app.dispatcher.backends.logger import LoggerBackend

@pytest.fixture
def dispatcher_instance():
    return Dispatcher(logger=Mock())

def test_slack_backend_is_registered_by_default():
    assert SlackBackend in Dispatcher.ENABLED_BACKENDS

def test_logger_backend_is_registered_by_default():
    assert LoggerBackend in Dispatcher.ENABLED_BACKENDS

def test_invalid_backend__logs_warning(dispatcher_instance):
    Dispatcher.ENABLED_BACKENDS = ["This is not a valid backend".__class__]
    dispatcher_instance.process_payload([])
    assert dispatcher_instance.logger.warn.mock_calls == [call("Ignoring invalid backend (not a child class of AbstractBaseBackend): <class 'str'>")]

def test_process_payload__with_2_backends__invokes_both_with_no_warnings(dispatcher_instance):

    test_backend_a = Mock(spec=AbstractBaseBackend)
    test_backend_b = Mock(spec=AbstractBaseBackend)
    test_backend_a_class = Mock(return_value=test_backend_a)
    test_backend_b_class = Mock(return_value=test_backend_b)

    Dispatcher.ENABLED_BACKENDS = [test_backend_a_class, test_backend_b_class]

    payload_object = []
    dispatcher_instance.process_payload(payload_object)

    assert dispatcher_instance.logger.warn.mock_calls == []
    assert dispatcher_instance.logger.error.mock_calls == []
    test_backend_a_class.return_value.process_payload.assert_called_with(payload_object, dispatcher_instance.logger)
    test_backend_b_class.return_value.process_payload.assert_called_with(payload_object, dispatcher_instance.logger)
