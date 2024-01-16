from agents.agent_serializer import AgentSerializer
from integrations.memoize import memoize_to_sqlite
from integrations.sqlite_agent_persistence import SQLiteAgentPersistence


class AgentPersistenceManager:
    def __init__(self, db_filename="agents.db"):
        self.persistence = SQLiteAgentPersistence(db_filename)

    def save_agent(self, agent):
        """
        Serialize and save the agent state if it is a working agent and not a prime agent.
        """
        if agent.working_agent and not agent.is_prime:
            agent_dict = AgentSerializer.to_dict(agent)
            self.persistence.save_agent(agent_dict)
        
    def load_agent(self, purpose, agent_lifecycle, openai_wrapper):
        """
        Load an agent with the given purpose from the database.
        """
        serialized_agent = self.persistence.fetch_agent(purpose)
        if serialized_agent:
            return AgentSerializer.from_dict(serialized_agent, agent_lifecycle, openai_wrapper)
        return None

    def load_all_agents(self, agent_lifecycle, openai_wrapper):
        """
        Load all agents from the database.
        """
        purposes = self.persistence.load_all_purposes()
        agents = []
        for purpose in purposes:
            agent = self.load_agent(purpose, agent_lifecycle, openai_wrapper)
            if agent:
                agents.append(agent)
        return agents
