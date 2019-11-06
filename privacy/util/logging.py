import logging


class LoggingClass:
    """A logging class"""
    @property
    def log(self) -> logging.Logger:
        """
        Used for automatically getting a class' logger.

        Returns:
            :class:`logging.Logger`
        """
        if not hasattr(self, "_log"):
            self._log = logging.getLogger(self.__class__.__name__)

        return self._log
