"""Used for consistent logging across classes."""
import logging


class LoggingClass:
    """A logging class"""
    _log: logging.Logger

    @property
    def log(self) -> logging.Logger:
        """
        Used for automatically getting a class' logger.

        Returns:
            `logging.Logger`: The Logger class.
        """
        if not hasattr(self, "_log"):
            self._log = logging.getLogger(self.__class__.__name__)

        return self._log
