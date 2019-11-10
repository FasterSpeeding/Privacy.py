"""Test LoggingClass and it's inheritability."""
from privacy.util.logging import *


def test_mock_logger():
    class mock_logger(LoggingClass):
        pass

    assert isinstance(mock_logger().log, logging.Logger)
