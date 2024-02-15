import time
from textual.worker import Worker, get_current_worker, WorkerState
from functools import partial
from ui.format import format_text
from rich.text import Text
from utils.utility import get_env_variable
from integrations.openaiwrapper import get_configured_openai_wrapper

class MicroAgentsLogic:
    def __init__(self, app):
        self.app = app
        self.manager = None
        self.initialize_manager()

    def initialize_manager(self):
        try:
            openai_wrapper = get_configured_openai_wrapper()
            from agents.microagent_manager import MicroAgentManager
            self.manager = MicroAgentManager(openai_wrapper, db_filename=get_env_variable("MICROAGENTS_DB_FILENAME", "agents.db", False))
            self.manager.create_agents()
        except Exception as e:
            self.app.statusbar.update(f"🚫 Error: {e}")

    async def on_input_submitted(self, event):
        self.app.run_worker(self.get_agent_info, thread=True, group="display_agent_info")
        self.app.statusbar.update(event.value)
        self.app.run_worker(partial(self.process_inputs, event.value), thread=True, exclusive=True, group="process_inputs")

    def process_user_input(self, user_input):
        self.app.process_input_done = False
        self.app.run_worker(self.get_agent_info, thread=True, group="display_agent_info")

        self.app.sub_title = user_input
        agent = self.manager.get_or_create_agent("Bootstrap Agent", depth=1, sample_input=user_input)
        return agent.respond(user_input)

    def on_worker_state_changed(self, event: Worker.StateChanged):
        if event.state in (WorkerState.SUCCESS,):
            if event.worker.name == "get_agent_info" and not self.app.process_input_done:
                self.app.run_worker(self.get_agent_info, thread=True, group="display_agent_info")

    def process_inputs(self, user_input):
        self.app.process_input_done = False
        worker = get_current_worker()
        self.app.statusbar.update("processing inputs.. " + user_input)
        response = self.process_user_input(user_input)
        self.app.question_number += 1
        output_text = format_text(self.app.question_number, user_input, response)
        if not worker.is_cancelled:
            time.sleep(2)
            self.app.statusbar.update("cancelled.. " + user_input)
            self.app.call_from_thread(self.app.rlog.write, output_text)

        self.app.statusbar.update("done.. " + user_input)
        self.app.process_input_done = True
        self.output_results()

    def display_agent_info(self, table_data):
        time.sleep(2)
        self.app.table.clear()

        if len(table_data) > 0:
            for row in table_data:
                styled_row = [Text(str(cell), no_wrap=False, overflow="fold") for cell in row]
                self.app.table.add_row(*styled_row)

    def get_agent_info(self):
        self.app.statusbar.update("Running Agents...")
        worker = get_current_worker()

        table_data = []
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
            self.app.call_from_thread(self.display_agent_info, table_data)
        else:
            self.app.statusbar.update("worker was cancelled")

    def output_results(self):
        self.app.rlog.write("\n\nFinal Results:\n")
        for agent in self.manager.get_agents():
            self.app.rlog.write(f"📊 Stats for {agent.purpose} :")
            self.app.rlog.write(f"🔁 Evolve Count: {agent.evolve_count}")
            self.app.rlog.write(f"💻 Code Executions: {agent.number_of_code_executions}")
            self.app.rlog.write(f"👥 Active Agents: {agent.active_agents}")
            self.app.rlog.write(f"📈 Usage Count: {agent.usage_count}")
            self.app.rlog.write(f"🏔 Max Depth:  {agent.max_depth}")
            self.app.rlog.write(f"🌟 Depth: {agent.depth}")
            self.app.rlog.write(f"🛠 Working Agent::{agent.working_agent}")
            self.app.rlog.write(f"📝 Last Input: {agent.last_input}")
            self.app.rlog.write(f"🚦 Status: {agent.current_status}")
            self.app.rlog.write(f"\nPrompt for {agent.purpose}:")
            self.app.rlog.write(f"{agent.dynamic_prompt}\n")