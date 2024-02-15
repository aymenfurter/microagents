import logging
from typing import Any, List

from agents.microagent_manager import MicroAgentManager
from agents.microagent import MicroAgent
from agents.parallel_agent_executor import ParallelAgentExecutor
from integrations.openaiwrapper import OpenAIAPIWrapper
from utils.utility import get_env_variable
import time
logger = logging.getLogger(__name__)

class GradioAgentManager:
    """
    A wrapper class for interacting with MicroAgentManager in a Gradio interface.
    """

    def __init__(self, openai_wrapper: OpenAIAPIWrapper):
        self.manager = MicroAgentManager(openai_wrapper, db_filename=get_env_variable("MICROAGENTS_DB_FILENAME", "agents.db", False))
        self.manager.create_agents()

    def stop_all_agents(self) -> None:
        """Stops all agents."""
        self.manager.stop_all_agents()

    def get_agents_info_flat(self) -> List[dict]:
        """
        Retrieve information about all agents for display in Gradio.
        """
        agents = self.manager.get_agents()
    
        return [self.format_agent_info(agent, agents, format=False) for agent in agents]

    def get_agents_info(self) -> List[dict]:
        """
        Retrieve information about all agents for display in Gradio.
        """
        agents = self.manager.get_agents()
        agents_sorted = self.sort_agents(agents)
    
        if not agents_sorted:
            return []
    
        return [self.format_agent_info(agent, agents_sorted) for agent in agents_sorted]

    def sort_agents(self, agents: List[MicroAgent]) -> List[MicroAgent]:
        """
        Sort agents based on their parent-child relationship.
        """
        if not agents:
            return []

        agent_dict = {agent.id: agent for agent in agents}
        sorted_agents = []

        def add_agent(agent_id, depth=0):
            agent = agent_dict.get(agent_id)
            if agent:
                agent.depth = depth 
                sorted_agents.append(agent)
                children = [a for a in agents if getattr(a, 'parent_id', None) == agent_id]
                for child in children:
                    add_agent(child.id, depth + 1)

        bootstrap_agent_id = next((agent.id for agent in agents if getattr(agent, 'purpose', '') == "Bootstrap Agent"), None)
        if bootstrap_agent_id is not None:
            add_agent(bootstrap_agent_id)

        return sorted_agents

    def format_agent_info(self, agent: MicroAgent, all_agents: List[MicroAgent], format=True) -> dict:
        """
        Format the information of a MicroAgent for display with tree structure.
        """

        if format:
            tree_structure = ''
            if agent.depth > 0:
                tree_structure += '│   ' * (agent.depth - 1)
                is_last_child = all_agents.index(agent) == len(all_agents) - 1 or all_agents[all_agents.index(agent) + 1].depth <= agent.depth
                tree_structure += '└── ' if is_last_child else '├── '
            
            agent_name = tree_structure + agent.purpose
        else:
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
            parallel_executor = ParallelAgentExecutor(self.manager)
            delegated_response = parallel_executor.create_and_run_agents("Bootstrap Agent", 1, user_input)
            return delegated_response
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