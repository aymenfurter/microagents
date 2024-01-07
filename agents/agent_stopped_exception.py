class AgentStoppedException(Exception):
    """Exception raised when an agent's execution is stopped."""

    def __init__(self, message="Agent execution has been stopped"):
        self.message = message
        super().__init__(self.message)