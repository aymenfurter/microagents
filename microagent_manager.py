import logging
from agent_creation import AgentCreation
from agent_similarity import AgentSimilarity
from openaiwrapper import OpenAIAPIWrapper

class MicroAgentManager:
    def __init__(self, api_key, max_agents=20):
        self.api_key = api_key
        self.max_agents = max_agents
        self.openai_wrapper = OpenAIAPIWrapper(api_key)
        self.agent_creator = AgentCreation(self.openai_wrapper, max_agents)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(logging.StreamHandler())

    def get_agents(self):
        return self.agent_creator.agents

    def create_agents(self):
        self.logger.info("Creating agents...")
        self.agent_creator.create_prime_agent(self.openai_wrapper)
        self.logger.info("Agents created successfully.")

    def get_or_create_agent(self, purpose, depth, sample_input):
        self.logger.info(f"Getting or creating agent for purpose: {purpose}")
        agent = self.agent_creator.get_or_create_agent(purpose, depth, sample_input)
        self.logger.info(f"Agent for purpose '{purpose}' retrieved or created.")
        return agent

    def find_closest_agent(self, purpose):
        self.logger.info(f"Finding closest agent for purpose: {purpose}")
        agent_similarity = AgentSimilarity(self.api_key, self.agent_creator.agents)
        purpose_embedding = agent_similarity.get_embedding(purpose)
        closest_agent = agent_similarity.find_closest_agent(purpose_embedding)
        self.logger.info(f"Closest agent for purpose '{purpose}' found.")
        return closest_agent
