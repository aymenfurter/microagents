import logging

class ListLogHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.log_messages = []

    def emit(self, record):
        message = self.format(record)
        self.log_messages.append(message)

    def get_logs(self):
        return self.log_messages

    def clear_logs(self):
        self.log_messages.clear()