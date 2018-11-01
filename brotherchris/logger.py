import logging
import re
from typing import List, Pattern

class LoggerProxy:
    """
    A proxy class for :class:`Logger<logging.Logger>`. The logging levels are
    set to :attr:`INFO<logging.INFO>`.
    """
    def __init__(
            self,
            name: str,
            strFormat: str,
            handler: logging.Handler = logging.StreamHandler()):
        """
        Parameters
        ----------
        name: str
            The name to give this logger.
        strFormat: str
            The formatting string to use.
        handler: logging.StreamHandler, optional
            The handler to use.
        """
        self.log: logging.Logger = logging.getLogger(name)
        self.log.setLevel(logging.INFO)

        handler: logging.Handler = handler
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter(strFormat))

        self.log.addHandler(handler)

    def close(self):
        """
        Closes and removes all :class:`Handlers<logging.Handler>` from
        :attr:`log`.

        Returns
        -------
        None
        """
        handlers: List[logging.Handler] = self.log.handlers[:]

        for handler in handlers:
            handler.close()
            self.log.removeHandler(handler)

class StreamFiltered(logging.StreamHandler):
    """
    A custom :class:`StreamHandler<logging.StreamHandler>` which can filter out
    :class:`LogRecords<logging.LogRecord>` using a regular expression
    :class:`Pattern`.
    """

    def __init__(self, pattern: Pattern):
        """
        Parameters
        ----------
        pattern: Pattern
            The regular expression :class:`Pattern` to use for filtering out
            :class:`LogRecords<logging.LogRecord>`.
        """
        self.pattern: Pattern = pattern
        logging.StreamHandler.__init__(self)

    def emit(self, record: logging.LogRecord):
        """
        Emits a :class:`record<logging.LogRecord>`.

        Filters out records using the :class:`Pattern` :attr:`pattern`. If no
        match is found, the super's :func:`emit()<logging.StreamHandler.emit>`
        is called.

        Parameters
        ----------
        record: logging.LogRecord
            The record to emit.

        Returns
        -------
        None
        """
        if re.search(self.pattern, record.getMessage()) is None:
            logging.StreamHandler.emit(self, record)
