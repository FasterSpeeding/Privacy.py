"""Tests for privacy.util.logging"""
from privacy.util.logging import LoggingClass, logging


def test_mock_logger():
    class mock_logger(LoggingClass):
        pass

    assert isinstance(mock_logger().log, logging.Logger)
