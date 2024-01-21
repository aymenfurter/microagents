import pandas as pd
import gradio as gr
from .utils import format_agent_data

class AgentTable:
    """
    Component for displaying information about agents in a table format.
    """
    def __init__(self, agent_manager):
        self.agent_manager = agent_manager

    def display(self):
        agents_info = self.agent_manager.get_agents_info()
        headers = ["Agent", "Status", "Is Working", "Depth", "Evolve Count", "Executions", "Last Input"]
        data = [ [agent[header] for header in headers] for agent in agents_info ]
        dataframe = pd.DataFrame(data, columns=headers)
        return gr.Dataframe(dataframe, interactive=False)
    
    def refresh(self):
        """Method to refresh the agent data."""
        return self.display()

class LogsDisplay:
    def __init__(self, log_handler):
        self.log_handler = log_handler

    def get_logs(self):
        logs = self.log_handler.get_logs()
        return "\n".join(logs)

    def display(self):
        return gr.TextArea(label="Logs", value="", interactive=False)

class AgentDetails:
    """
    Component for displaying details of a selected agent.
    """
    def __init__(self, agent_manager):
        self.agent_manager = agent_manager

    def refresh(self):
        """Method to refresh the agent data."""
        return self.display()
    
    def display(self, selected_agent):
        agent_details = self.agent_manager.get_agent_details(selected_agent)
        formatted_details = format_agent_data(agent_details)
        return gr.Markdown(formatted_details)

class ChatInterface:
    """
    Component for handling chat functionality with agents.
    """
    def __init__(self, agent_manager):
        self.agent_manager = agent_manager

    def chat_function(self, message, history):
        return self.agent_manager.process_user_input(message)

    def cancel_function(self):
        pass

    def display(self):
        chat_interface = gr.ChatInterface(examples=["What is 10 * 38124?", "List today's top three sports news stories.", "What is the population of Japan?", "What is today's top news?", "How is the weather at my location?"],fn=self.chat_function, title="Chat", retry_btn=None, undo_btn=None, clear_btn=None, additional_inputs=None)
        return chat_interface
