import logging

from typing import List, Optional

from agents.microagent import MicroAgent
from integrations.openaiwrapper import OpenAIAPIWrapper
from agents.agent_similarity import AgentSimilarity
from agents.agent_persistence_manager import AgentPersistenceManager
from numpy import ndarray
from prompt_management.prompts import (
    PRIME_PROMPT, PRIME_NAME, 
    PROMPT_ENGINEERING_SYSTEM_PROMPT, 
    PROMPT_ENGINEERING_TEMPLATE, EXAMPLES
)

logger=logging.getLogger()

DEFAULT_MAX_AGENTS = 20
PRIME_AGENT_WEIGHT = 25

class AgentLifecycle:
    def __init__(self, openai_wrapper: OpenAIAPIWrapper, agent_persistance_manager: AgentPersistenceManager, max_agents: int = DEFAULT_MAX_AGENTS):
        self.agents: List[MicroAgent] = []
        self.openai_wrapper = openai_wrapper
        self.agent_persistence = agent_persistance_manager
        self.max_agents = max_agents

    def cleanup_agents(self):
        """Remove all agents with status stopped = True"""
        for agent in self.agents:
            if agent.stopped:
                self.agents.remove(agent)
    
    def create_prime_agent(self) -> None:
        """
        Creates the prime agent and adds it to the agent list.
        """
        prime_agent = MicroAgent(
            PRIME_PROMPT, PRIME_NAME, 0, self, 
            self.openai_wrapper, PRIME_AGENT_WEIGHT, True, True
        )
        self.agents.append(prime_agent)

    def get_or_create_agent(self, purpose: str, depth: int, sample_input: str, force_new: bool = False) -> MicroAgent:
        """
        Retrieves or creates an agent based on the given purpose.
        Optionally creates a new agent regardless of similarity if force_new is True.
        """
        if not force_new:
            agent_similarity = AgentSimilarity(self.openai_wrapper, self.agents)
            purpose_embedding = agent_similarity.get_embedding(purpose)
            closest_agent, highest_similarity = agent_similarity.find_closest_agent(purpose_embedding)
            similarity_threshold = agent_similarity.calculate_similarity_threshold()

            if highest_similarity >= similarity_threshold:
                closest_agent.usage_count += 1
                return closest_agent

        self.remove_least_used_agent_if_needed()
        new_agent = self.create_new_agent(purpose, depth, sample_input, None)  # Purpose embedding is not required if creating a new agent
        return new_agent

    def remove_least_used_agent_if_needed(self) -> None:
        """
        Removes the least used agent if the maximum number of agents is exceeded.
        """
        if len(self.agents) >= self.max_agents:
            self.agents.sort(key=lambda agent: agent.usage_count)
            self.agents.pop(0)

    def create_new_agent(self, purpose: str, depth: int, sample_input: str, purpose_embedding: ndarray) -> MicroAgent:
        """
        Creates a new agent.
        """
        prompt = self.generate_llm_prompt(purpose, sample_input)
        new_agent = MicroAgent(prompt, purpose, depth, self, self.openai_wrapper, purpose_embedding=purpose_embedding)
        new_agent.usage_count = 1
        self.agents.append(new_agent)
        return new_agent

    def save_agent(self, agent) -> None:
        """Saves the given agent."""
        try:
            self.agent_persistence.save_agent(agent)
        except Exception as e:
            logger.exception(f"Error in saving agent: {e}")
            raise

    def generate_llm_prompt(self, goal: str, sample_input: str) -> str:
        """
        Generates a prompt for the LLM based on the given goal and sample input.
        """
        messages = [
            {"role": "system", "content": PROMPT_ENGINEERING_SYSTEM_PROMPT},
            {"role": "user", "content": PROMPT_ENGINEERING_TEMPLATE.format(goal=goal, sample_input=sample_input, examples=EXAMPLES)}
        ]

        try:
            return self.openai_wrapper.chat_completion(messages=messages)
        except Exception as e:
            logger.exception(f"Error generating LLM prompt: {e}")
            print(f"Error generating LLM prompt: {e}")
            return ""
