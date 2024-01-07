import unittest
import logging
from gradio_ui.log_handler import ListLogHandler 

class TestListLogHandler(unittest.TestCase):
    def setUp(self):
        self.logger = logging.getLogger("test_logger")
        self.log_handler = ListLogHandler()
        self.log_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(self.log_handler)
        self.logger.setLevel(logging.DEBUG)

    def test_log_capture(self):
        test_message = "Test log message"
        self.logger.debug(test_message)
        logs = self.log_handler.get_logs()
        self.assertIn(test_message, logs)

    def test_log_clear(self):
        self.logger.debug("Test log message")
        self.log_handler.clear_logs()
        logs = self.log_handler.get_logs()
        self.assertEqual(len(logs), 0)

if __name__ == '__main__':
    unittest.main()
