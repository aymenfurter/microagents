from textual.app import App
from ui.logic import MicroAgentsLogic
from ui.logging import LoggingHandler
from ui.components import MicroAgentsHeader, MicroAgentsFooter, MicroAgentsStatusbar, MicroAgentsInput, MicroAgentsTable
from ui.constants import CSS, BINDINGS
from textual.widgets import RichLog, TabbedContent
from textual.widgets import Footer, Header, Input, RichLog, TabbedContent, TabPane

class MicroAgentsApp(App):
    CSS = CSS 
    BINDINGS = BINDINGS
    
    def __init__(self):
        super().__init__()
        self.setup_ui_components()
        self.logic = MicroAgentsLogic(self)
        self.logging_handler = LoggingHandler(self.logpanel)
        self.question_number = 0

    def setup_ui_components(self):
        self.header = MicroAgentsHeader()
        self.footer = MicroAgentsFooter()
        self.statusbar = MicroAgentsStatusbar()
        self.input_field = MicroAgentsInput()
        self.table = MicroAgentsTable()
        self.logpanel = RichLog(wrap=True, classes="logpanel")
        self.rlog = RichLog(wrap=True, classes="rlog")

    def compose(self):
        self.header=Header()
        yield self.header
        yield self.table
        with TabbedContent(initial="Output", classes="tabs"):
             with TabPane("Output", id="Output"):
                  yield self.rlog
             with TabPane("Logging"):
                  yield self.logpanel
        yield Input(placeholder="Enter question here", classes="prompt")
        yield self.statusbar
        self.footer=Footer()
        yield self.footer

    async def on_input_submitted(self, event):
        await self.logic.on_input_submitted(event)

    def on_ready(self):
        pass

    def on_worker_state_changed(self, event):
        self.logic.on_worker_state_changed(event)

if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()
    app = MicroAgentsApp()
    app.run()