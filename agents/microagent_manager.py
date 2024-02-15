import logging

from typing import List, Optional, Any
from agents.agent_lifecycle import AgentLifecycle 
from agents.agent_similarity import AgentSimilarity
from agents.agent_persistence_manager import AgentPersistenceManager 
from integrations.openaiwrapper import OpenAIAPIWrapper

logger= logging.getLogger()

class MicroAgentManager:
    """
    Manages the creation and retrieval of micro agents.
    """

    def __init__(self, openai_wrapper: OpenAIAPIWrapper, max_agents: int = 20, db_filename : str = "agents.db"):
        self.max_agents = max_agents
        self.openai_wrapper = openai_wrapper
        self.agent_persistence = AgentPersistenceManager(db_filename)
        self.agent_lifecycle = AgentLifecycle(self.openai_wrapper, self.agent_persistence, max_agents)
        self.load_agents()

    def stop_all_agents(self) -> None:
        """Stops all agents."""
        self.agent_lifecycle.stop_all_agents()

    def cleanup_agents(self):
        """Remove all agents with status stopped = True"""
        self.agent_lifecycle.cleanup_agents()
    
    def load_agents(self):
        """Loads agents from the database."""
        loaded_agents = self.agent_persistence.load_all_agents(self.agent_lifecycle, self.openai_wrapper)
        self.agent_lifecycle.agents.extend(loaded_agents)
        logger.info(f"Loaded {len(loaded_agents)} agents from the database.")


    def get_agents(self) -> List[Any]:
        """Returns the list of agents."""
        self.cleanup_agents()
        return self.agent_lifecycle.agents

    def create_agents(self) -> None:
        """Creates prime agents and logs the process."""
        logger.info("Creating agents...")
        try:
            self.agent_lifecycle.create_prime_agent()
            logger.info("Agents created successfully.")
        except Exception as e:
            logger.exception(f"Error in creating agents: {e}")
            raise
    
    def get_or_create_agent(self, purpose: str, depth: int, sample_input: str, parent_agent=None) -> Any:
        """
        Retrieves an existing agent or creates a new one based on the given purpose.
        """
        logger.info(f"Getting or creating agent for purpose: {purpose}")
        try:
            agent = self.agent_lifecycle.get_or_create_agent(purpose, depth, sample_input, parent_agent=parent_agent)
            logger.info(f"Agent for purpose '{purpose}' retrieved or created.")
            return agent
        except Exception as e:
            logging.exception(f"Error in getting or creating agent: {e}")
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