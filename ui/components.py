from textual.widgets import DataTable, Footer, Header, Input, Static
from rich.text import Text

class MicroAgentsHeader(Header):
    """Custom Header for the MicroAgents App."""
    def __init__(self):
        super().__init__()

class MicroAgentsFooter(Footer):
    """Custom Footer for the MicroAgents App."""

class MicroAgentsStatusbar(Static):
    """Custom Status Bar for displaying various status messages."""
    def __init__(self, initial_text="Waiting for a question.."):
        super().__init__(initial_text, classes="statusbar")

class MicroAgentsInput(Input):
    """Custom Input field for user queries."""
    def __init__(self, placeholder="Enter question here"):
        super().__init__(placeholder=placeholder, classes="prompt")

class MicroAgentsTable(DataTable):
    """Custom Table for displaying agent information."""
    def __init__(self):
        super().__init__(header_height=2, zebra_stripes=True, classes="table")
        self.add_columns()

    def add_columns(self):
        """Adds columns to the table."""
        headers = ("Agent", "Evolve\nCount", "Code\nExecutions", "Active\nAgents",
                   "Usage\nCount", "Depth", "Working?", "Last\nInput", "Status")
        for header in headers:
            self.add_column(header)