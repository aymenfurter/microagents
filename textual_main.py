import time
import logging

from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import ScrollableContainer
from textual.widgets import DataTable, Footer, Header, Input, Label, Static, RichLog, TabbedContent, TabPane
from textual.worker import Worker, get_current_worker, WorkerState

from agents.microagent_manager import MicroAgentManager
from utils.utility import get_env_variable
from utils.ui import format_text

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


# Constants
"""
QUESTION_SET = [
    "What is 5+9?",
    "What is the population of Thailand?",
    "What is the population of Sweden?",
    "What is the population of Sweden and Thailand combined?"
]
"""

class TextHandler(logging.Handler):
    """Class for  logging to a TextLog widget"""

    def __init__(self, textlog):
        self.text = textlog
        logging.Handler.__init__(self)

    def emit(self, record):
        msg = self.format(record)
        style = "red"
        # style your output depending on e.g record.levelno here
        self.text.write(Text(msg, style))

class MicroAgentsApp(App):
    """ Main MicroAgents App Window """

    CSS = """
      Screen {
        layout: vertical;
      }

      .table {
        height: 5fr;
      }

      .tabs {
        height: 10fr;
      }

      .statusbar {
        dock: bottom;
        border: white;
      }

      .prompt {
        width: 100%;
        border: yellow;
      }
    """

    BINDINGS = [Binding(key="q", action="quit", description="Quit the app"),
                ("d", "toggle_dark", "Toggle dark mode"),
    ]

    def __init__(self):
        self.table=DataTable(header_height=2, zebra_stripes=True, classes="table")
        self.rlog = RichLog(wrap=True, classes="rlog")
        self.logpanel = RichLog(wrap=True)
        self.statusbar=Static("Waiting for a question..", classes="statusbar")
        self.process_input_done=True

        self.agents_running=False

        App.__init__(self)

    def compose(self) -> ComposeResult:
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

    def on_ready(self):
        th = TextHandler(self.logpanel)
        th.setLevel(logging.DEBUG)
        logger.addHandler(th)

    def on_mount(self) -> None:
        self.title="Microagents"
        self.sub_title=""

        _header=("Agent", "Evolve\nCount", "Code\nExecutions", "Active\nAgents",
                 "Usage\nCount", "Depth", "Working?", "Last\nInput", "Status")
        for _label in _header:
            self.table.add_column(_label)

        self.statusbar.update("Waiting for a question..")
        self.manager = MicroAgentManager()
        self.manager.create_agents()

    def action_toggle_dark(self) -> None:
        """ An action to toggle dark mode. """
        self.dark= not self.dark

    async def on_input_submitted(self, event: Input.Submitted) -> None:

        global QUESTION_SET
        QUESTION_SET=[event.value,]

        if not self.agents_running:
           self.run_worker(self.get_agent_info, thread=True, group="display_agent_info")
        self.statusbar.update(event.value)
        self.run_worker(self.process_inputs, thread=True, exclusive=True, group="process_inputs")

        self.statusbar.update("Waiting for a question1..")

    def process_user_input(self, user_input):
        """
        Processes a single user input and generates a response.
        """
        self.process_input_done=False
        if not self.agents_running:
           self.run_worker(self.get_agent_info, thread=True, group="display_agent_info")

        self.sub_title = user_input
        agent = self.manager.get_or_create_agent("Bootstrap Agent", depth=1, sample_input=user_input)
        return agent.respond(user_input)

    def on_worker_state_changed(self, event:Worker.StateChanged) -> None:
        """ Called when the worker state changes.."""
        if event.state in (WorkerState.SUCCESS,):
           if event.worker.name == "get_agent_info" and not self.process_input_done:
              self.run_worker(self.get_agent_info, thread=True, group="display_agent_info")

    def process_inputs(self):
        self.process_input_done=False
        worker = get_current_worker()
        self.statusbar.update("processing inputs..")
        for question_number, user_input in enumerate(QUESTION_SET, start=1):
            response = self.process_user_input(user_input)
            output_text = format_text(question_number, user_input, response)
            if not worker.is_cancelled:
               time.sleep(2)
               self.call_from_thread(self.rlog.write, output_text)

        self.process_input_done=True
        self.output_results()
        self.table.clear()
        self.sub_title=""
        self.statusbar.update("Finished..")


    def display_agent_info(self, table_data):
        time.sleep(2)
        self.table.clear()

        if len(table_data) > 0:
           for row in table_data:
               styled_row = [Text(str(cell), no_wrap=False, overflow="fold") for cell in row]
               self.table.add_row(*styled_row)

    def get_agent_info(self) -> None:
        self.agents_running=True
        self.statusbar.update("Running Agents...")
        worker = get_current_worker()

        table_data=[]
        agents = self.manager.get_agents()
        for agent in agents:
            active_agents = ", ".join(f"{k} -> {v}" for k, v in agent.active_agents.items())
            table_data.append([agent.purpose,
                                 agent.evolve_count,
                                 agent.number_of_code_executions,
                                 active_agents,
                                 agent.usage_count,
                                 agent.depth,
                                 "✅" if agent.working_agent else "❌",
                                 agent.last_input,
                                 "" if agent.current_status is None else agent.current_status
            ])


        if not worker.is_cancelled:
           time.sleep(2)
           self.call_from_thread(self.display_agent_info, table_data)
        else:
           self.statusbar.update("worker was cancelled")

    def output_results(self):
        self.rlog.write("\n\nFinal Results:\n")
        for agent in self.manager.get_agents():
                self.rlog.write(f"📊 Stats for {agent.purpose} :")
                self.rlog.write(f"🔁 Evolve Count: {agent.evolve_count}")
                self.rlog.write(f"💻 Code Executions: {agent.number_of_code_executions}")
                self.rlog.write(f"👥 Active Agents: {agent.active_agents}")
                self.rlog.write(f"📈 Usage Count: {agent.usage_count}")
                self.rlog.write(f"🏔 Max Depth:  {agent.max_depth}")
                self.rlog.write(f"🌟 Depth: {agent.depth}")
                self.rlog.write(f"🛠 Working Agent::{agent.working_agent}")
                self.rlog.write(f"📝 Last Input: {agent.last_input}")
                self.rlog.write(f"🚦 Status: {agent.current_status}")
                self.rlog.write(f"\nPrompt for {agent.purpose}:")
                self.rlog.write(f"{agent.dynamic_prompt}\n")

if __name__ == '__main__':
   from dotenv import load_dotenv
   load_dotenv()
   app = MicroAgentsApp()
   app.run()
