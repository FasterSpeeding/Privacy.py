"""Tests for privacy.util.logging"""
from privacy.util.logging import LoggingClass, logging


def test_mock_logger():
    class MockLogger(LoggingClass):
        pass

    assert isinstance(MockLogger().log, logging.Logger)
