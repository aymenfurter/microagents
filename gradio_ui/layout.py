import gradio as gr
import logging
from .components import AgentTable, AgentDetails, ChatInterface
from .agent_manager import GradioAgentManager
from .utils import load_env_variable
from .log_handler import ListLogHandler
from integrations.openaiwrapper import get_configured_openai_wrapper

def create_layout():
    """Create and return the layout for the Gradio app."""
    agent_manager = GradioAgentManager(get_configured_openai_wrapper())

    # Initialize components
    agent_table = AgentTable(agent_manager)
    agent_details = AgentDetails(agent_manager)
    chat_interface = ChatInterface(agent_manager)
    log_handler = ListLogHandler()

    # Initialize logging
    log_handler.setLevel(logging.INFO)
    logging.getLogger().addHandler(log_handler)
    logging.getLogger().setLevel(logging.INFO)
    logging.getLogger().propagate = False
    
    def refresh_agent_list():
        """Function to refresh the agent list in the dropdown."""
        new_agent_choices = [agent['Agent'] for agent in agent_manager.get_agents_info_flat()]
        return gr.Dropdown(label="Select Agent", choices=new_agent_choices, value=default_agent)
    
    def cancel_execution():
        agent_manager.stop_all_agents()

    def fetch_logs():
        return "\n".join(log_handler.get_logs())

    default_agent = "Bootstrap Agent"



    with gr.Blocks() as layout:
        gr.Markdown("## Microagents")
        agent_table_component = agent_table.display()
        gr.Row(agent_table_component)
        chat_interface_component = chat_interface.display()
        gr.Row(chat_interface_component)


        with gr.Row():
            with gr.Column():
                gr.Markdown("### Logs")
                logs_display = gr.Textbox(label="Logs", value="", interactive=False, max_lines=5)
                gr.Row(logs_display)

            with gr.Column():
                gr.Markdown("### Current Execution")
                cancel_button = gr.Button("Cancel")
                cancel_button.click(fn=cancel_execution, inputs=[])
                gr.Row(cancel_button)
                gr.Markdown("### Details")
                agent_choices = [agent['Agent'] for agent in agent_manager.get_agents_info_flat()]
                agent_selector = gr.Dropdown(label="Select Agent", choices=agent_choices, value=default_agent)
                gr.Row(agent_selector)
                refresh_button = gr.Button("Refresh Agent List")
                refresh_button.click(fn=refresh_agent_list, inputs=[], outputs=agent_selector)

                gr.Row(refresh_button)
                agent_details_component = agent_details.display(selected_agent="")
                agent_selector.change(lambda selected_agent: agent_details.display(selected_agent), inputs=agent_selector, outputs=agent_details_component)
                gr.Row(agent_details_component)

        layout.load(fetch_logs, [], logs_display, every=1)
        layout.load(lambda: agent_table.refresh(), [], agent_table_component, every=1)

    return layout
