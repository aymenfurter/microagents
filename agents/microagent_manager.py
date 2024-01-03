import logging

from typing import List, Optional, Any
from agents.agent_creation import AgentCreation
from agents.agent_similarity import AgentSimilarity
from integrations.manager import LLM_Manager

logger= logging.getLogger()

class MicroAgentManager:
    """
    Manages the creation and retrieval of micro agents.
    """

    def __init__(self, max_agents: int = 20):
        self.max_agents = max_agents
        self.llm_manager = LLM_Manager()
        self.agent_creator = AgentCreation(self.llm_manager, max_agents)

    def get_agents(self) -> List[Any]:
        """Returns the list of agents."""
        return self.agent_creator.agents

    def create_agents(self) -> None:
        """Creates prime agents and logs the process."""
        logger.info("Creating agents...")
        try:
            self.agent_creator.create_prime_agent()
            logger.info("Agents created successfully.")
        except Exception as e:
            logger.exception(f"Error in creating agents: {e}")
            raise

    def get_or_create_agent(self, purpose: str, depth: int, sample_input: str) -> Any:
        """
        Retrieves an existing agent or creates a new one based on the given purpose.
        """
        logger.info(f"Getting or creating agent for purpose: {purpose}")
        try:
            agent = self.agent_creator.get_or_create_agent(purpose, depth, sample_input)
            logger.info(f"Agent for purpose '{purpose}' retrieved or created.")
            return agent
        except Exception as e:
            logging.exception(f"Error in getting or creating agent: {e}")
            raise

    def find_closest_agent(self, purpose: str) -> Any:
        """
        Finds the closest agent matching the given purpose.
        """
        logger.info(f"Finding closest agent for purpose: {purpose}")
        try:
            agent_similarity = AgentSimilarity(self.api_key, self.agent_creator.agents)
            purpose_embedding = agent_similarity.get_embedding(purpose)
            closest_agent = agent_similarity.find_closest_agent(purpose_embedding)
            logger.info(f"Closest agent for purpose '{purpose}' found.")
            return closest_agent
        except Exception as e:
            logging.exception(f"Error in finding closest agent: {e}")
            raise

    def display_agent_status(self):
        """Displays the current status of all agents."""
        for agent in self.get_agents():
            logger.info(f"Agent {agent.purpose}: Status = {agent.current_status}, Evolve Count = {agent.evolve_count}")

    def display_active_agent_tree(self):
        """Displays a tree view of active agent relationships."""
        for agent in self.get_agents():
            if agent.active_agents:
                logger.info(f"Agent {agent.purpose} is calling: {agent.active_agents}")
            else:
                logger.info(f"Agent {agent.purpose} is currently idle.")
