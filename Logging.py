from typing import List, Pattern
import logging
import re

class Logger:
    def __init__(self,
                 name: str,
                 strFormat: str,
                 handler: logging.Handler = logging.StreamHandler()):
        self.log: logging.Logger = logging.getLogger(name)
        self.log.setLevel(logging.INFO)

        self.handler: logging.Handler = handler
        self.handler.setLevel(logging.INFO)
        self.handler.setFormatter(logging.Formatter(strFormat))

        self.log.addHandler(self.handler)

    def close(self):
        handlers: List[logging.Handler] = self.log.handlers[:]

        for handler in handlers:
            handler.close()
            self.log.removeHandler(handler)

class StreamFiltered(logging.StreamHandler):
    def __init__(self, pattern: Pattern):
        self.pattern: Pattern = pattern
        logging.StreamHandler.__init__(self)

    def emit(self, record: logging.LogRecord):
        if re.search(self.pattern, record.getMessage()) is None:
            logging.StreamHandler.emit(self, record)
