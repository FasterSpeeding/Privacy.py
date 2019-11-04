import logging


class LoggingClass:
    @property
    def log(self):
        if not hasattr(self, "_log"):
            self._log = logging.getLogger(self.__class__.__name__)

        return self._log
