import logging
import re

class Logger:
    def __init__(self,
                 name: str,
                 strFormat: str,
                 handler: logging.Handler = logging.StreamHandler()):
        # sys.stderr = self.StreamFiltered(filter, sys.stderr)
        # sys.stdout = self.StreamFiltered(filter, sys.stdout)

        self.log = logging.getLogger(name)
        self.log.setLevel(logging.INFO)

        self.handler = handler
        self.handler.setLevel(logging.INFO)
        self.handler.setFormatter(logging.Formatter(strFormat))

        self.log.addHandler(self.handler)

    def close(self):
        handlers = self.log.handlers[:]

        for handler in handlers:
            handler.close()
            self.log.removeHandler(handler)

class StreamFiltered(logging.StreamHandler):
    def __init__(self, pattern):
        self.pattern = pattern
        logging.StreamHandler.__init__(self)

    def emit(self, record):
        if re.search(self.pattern, record.getMessage()) is None:
            logging.StreamHandler.emit(self, record)
