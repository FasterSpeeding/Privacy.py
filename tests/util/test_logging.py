"""Tests for privacy.util.logging"""
from privacy.util import logging


def test_mock_logger():
    class MockLogger(logging.LoggingClass):
        pass

    assert isinstance(MockLogger().log, logging.logging.Logger)
