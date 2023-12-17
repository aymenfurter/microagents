import logging
from typing import List, Optional, Any
from agents.agent_creation import AgentCreation
from agents.agent_similarity import AgentSimilarity
from integrations.openaiwrapper import OpenAIAPIWrapper

class MicroAgentManager:
    """
    Manages the creation and retrieval of micro agents.
    """

    def __init__(self, api_key: str, max_agents: int = 20, logger: Optional[logging.Logger] = None):
        self.api_key = api_key
        self.max_agents = max_agents
        self.openai_wrapper = OpenAIAPIWrapper(api_key)
        self.agent_creator = AgentCreation(self.openai_wrapper, max_agents)
        self.logger = logger or self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Sets up a logger for the class."""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.ERROR)
        logger.addHandler(logging.StreamHandler())
        return logger

    def get_agents(self) -> List[Any]:
        """Returns the list of agents."""
        return self.agent_creator.agents

    def create_agents(self) -> None:
        """Creates prime agents and logs the process."""
        self.logger.info("Creating agents...")
        try:
            self.agent_creator.create_prime_agent()
            self.logger.info("Agents created successfully.")
        except Exception as e:
            self.logger.error(f"Error in creating agents: {e}")
            raise

    def get_or_create_agent(self, purpose: str, depth: int, sample_input: str) -> Any:
        """
        Retrieves an existing agent or creates a new one based on the given purpose.
        """
        self.logger.info(f"Getting or creating agent for purpose: {purpose}")
        try:
            agent = self.agent_creator.get_or_create_agent(purpose, depth, sample_input)
            self.logger.info(f"Agent for purpose '{purpose}' retrieved or created.")
            return agent
        except Exception as e:
            self.logger.error(f"Error in getting or creating agent: {e}")
            raise

    def find_closest_agent(self, purpose: str) -> Any:
        """
        Finds the closest agent matching the given purpose.
        """
        self.logger.info(f"Finding closest agent for purpose: {purpose}")
        try:
            agent_similarity = AgentSimilarity(self.api_key, self.agent_creator.agents)
            purpose_embedding = agent_similarity.get_embedding(purpose)
            closest_agent = agent_similarity.find_closest_agent(purpose_embedding)
            self.logger.info(f"Closest agent for purpose '{purpose}' found.")
            return closest_agent
        except Exception as e:
            self.logger.error(f"Error in finding closest agent: {e}")
            raise

    def display_agent_status(self):
        """Displays the current status of all agents."""
        for agent in self.get_agents():
            self.logger.info(f"Agent {agent.purpose}: Status = {agent.current_status}, Evolve Count = {agent.evolve_count}")

    def display_active_agent_tree(self):
        """Displays a tree view of active agent relationships."""
        for agent in self.get_agents():
            if agent.active_agents:
                self.logger.info(f"Agent {agent.purpose} is calling: {agent.active_agents}")
            else:
                self.logger.info(f"Agent {agent.purpose} is currently idle.")
