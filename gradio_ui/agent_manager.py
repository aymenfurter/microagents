import logging
from typing import Any, List

from agents.microagent_manager import MicroAgentManager
from agents.microagent import MicroAgent

logger = logging.getLogger(__name__)

class GradioAgentManager:
    """
    A wrapper class for interacting with MicroAgentManager in a Gradio interface.
    """

    def __init__(self, api_key: str):
        self.manager = MicroAgentManager(api_key)
        self.manager.create_agents()

    def get_agents_info(self) -> List[dict]:
        """
        Retrieve information about all agents for display in Gradio.
        """
        agents = self.manager.get_agents()
        return [self.format_agent_info(agent) for agent in agents]

    def format_agent_info(self, agent: MicroAgent) -> dict:
        """
        Format the information of a MicroAgent for display.
        """
        agent_name = ", ".join(f"{k}->{v}" for k, v in agent.active_agents.items())
        if not agent_name:
            agent_name = agent.purpose
        return {
            "Agent": agent_name,
            "Status": agent.current_status,
            "Depth": agent.depth,
            "Evolve Count": agent.evolve_count,
            "Executions": agent.number_of_code_executions,
            "Last Input": agent.last_input,
            "Is Working": "✅" if agent.working_agent else "❌",
        }

    def format_agent_info_details(self, agent: MicroAgent) -> dict:
        """
        Format the information of a MicroAgent for display.
        """
        return {
            "Purpose": agent.purpose,
            "System Prompt": agent.dynamic_prompt,
            "Last Input": agent.last_input,
            "Last Output": agent.last_output,
            "Last Conversation": agent.last_conversation,
        }

    def get_agent_details(self, purpose: str) -> dict:
        """
        Get detailed information about an agent by its purpose.
        """
        agent = next((a for a in self.manager.get_agents() if a.purpose == purpose), None)
        return self.format_agent_info_details(agent) if agent else {}

    def process_user_input(self, user_input: str) -> str:
        """
        Process user input through a specified agent and return its response.
        """
        try:
            agent = self.manager.get_or_create_agent("Bootstrap Agent", depth=1, sample_input=user_input)
            return agent.respond(user_input)
        except Exception as e:
            logger.exception(f"Error processing user input: {e}")
            return "Error in processing input."

    def update_agent_status(self, purpose: str, new_status: str):
        """
        Update the status of a specific agent.
        """
        agent = next((a for a in self.manager.get_agents() if a.purpose == purpose), None)
        if agent:
            agent.update_status(new_status)
            self.manager.agent_lifecycle.save_agent(agent)