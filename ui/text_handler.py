import logging
from rich.text import Text

class TextHandler(logging.Handler):
    """Class for  logging to a TextLog widget"""

    def __init__(self, textlog):
        self.text = textlog
        logging.Handler.__init__(self)

    def emit(self, record):
        msg = self.format(record)
        style = "red"
        self.text.write(Text(msg, style))