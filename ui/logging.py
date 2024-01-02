import logging
from ui.text_handler import TextHandler

class LoggingHandler:
    def __init__(self, log_panel):
        self.log_panel = log_panel
        self.setup_logger()

    def setup_logger(self):
        th = TextHandler(self.log_panel)
        th.setLevel(logging.DEBUG)
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        logger.addHandler(th)