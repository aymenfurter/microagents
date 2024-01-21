import logging
from typing import List
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

logger = logging.getLogger()

DEFAULT_MAX_AGENTS = 2000
PRIME_AGENT_WEIGHT = 25

class AgentLifecycle:
    def __init__(self, openai_wrapper: OpenAIAPIWrapper, agent_persistence_manager: AgentPersistenceManager, max_agents: int = DEFAULT_MAX_AGENTS):
        self.agents: List[MicroAgent] = []
        self.openai_wrapper = openai_wrapper
        self.agent_persistence = agent_persistence_manager
        self.max_agents = max_agents

    def stop_all_agents(self) -> None:
        """Stops all agents."""
        for agent in self.agents:
            agent.stop()

    def reset_all_agents(self) -> None:
        """Resets all agents."""
        for agent in self.agents:
            agent.reset()

    def cleanup_agents(self):
        """Remove all agents with status stopped = True in an efficient manner."""
        self.agents = [agent for agent in self.agents if not agent.stopped]

    def create_prime_agent(self) -> None:
        """Creates the prime agent and adds it to the agent list."""
        prime_agent = MicroAgent(
            PRIME_PROMPT, PRIME_NAME, 0, self, 
            self.openai_wrapper, PRIME_AGENT_WEIGHT, True, True
        )
        self.agents.append(prime_agent)

    def add_agent(self, agent: MicroAgent) -> None:
        """Adds an agent to the list of agents."""
        self.agents.append(agent)



    def get_available_agents_for_agent(self, agent) -> List[MicroAgent]:
        """Returns the list of available agents for the given purpose."""
        agent_id = agent.id 
        available_agents = [agent for agent in self.agents if agent.purpose != "Bootstrap Agent" and agent.working_agent]
        for agent in available_agents:
            if agent.parent_id != agent_id:
                available_agents.remove(agent)

        return available_agents

    def get_or_create_agent(self, purpose: str, depth: int, sample_input: str, force_new: bool = False, parent_agent=None) -> MicroAgent:
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

        return self._create_and_add_agent(purpose, depth, sample_input, parent_agent=parent_agent)

    def _create_and_add_agent(self, purpose: str, depth: int, sample_input: str, parent_agent=None) -> MicroAgent:
        """Helper method to create and add a new agent."""
        if len(self.agents) >= self.max_agents:
            self._remove_least_used_agent()

        new_agent = MicroAgent(self._generate_llm_prompt(purpose, sample_input), purpose, depth, self, self.openai_wrapper, parent=parent_agent)
        new_agent.usage_count = 1
        self.agents.append(new_agent)
        return new_agent

    def _remove_least_used_agent(self):
        """Removes the least used agent."""
        least_used_agent = min(self.agents, key=lambda agent: agent.usage_count)
        self.agents.remove(least_used_agent)

    def save_agent(self, agent: MicroAgent) -> None:
        """Saves the given agent with error handling."""
        try:
            self.agent_persistence.save_agent(agent)
        except Exception as e:
            logger.exception(f"Error in saving agent: {e}")
            raise
    
    
    def remove_agent(self, agent: MicroAgent) -> None:
        """Removes the given agent with error handling."""
        try:
            self.agent_persistence.remove_agent(agent)
        except Exception as e:
            logger.exception(f"Error in saving agent: {e}")
            raise

    def _generate_llm_prompt(self, goal: str, sample_input: str) -> str:
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
            return ""
