import logging
import numpy as np
from typing import List, Tuple, Optional
from sklearn.metrics.pairwise import cosine_similarity

from integrations.manager import LLM_Manager

logger = logging.getLogger()

class Agent:
    def __init__(self, purpose: str):
        self.purpose = purpose

class AgentSimilarity:
    def __init__(self, llm_manager: LLM_Manager, agents: List[Agent]):
        """
        Initializes the AgentSimilarity object.

        :param openai_wrapper: Instance of OpenAIAPIWrapper to interact with OpenAI API.
        :param agents: List of Agent objects.
        """
        self.llm_manager = llm_manager
        self.agents = agents

    def get_embedding(self, text: str):
        """
        Retrieves the embedding for a given text.

        :param text: Text to get embedding for.
        :return: Embedding as a numpy array.
        """
        try:
            return self.llm_manager.get_embedding(text)
        except Exception as e:
            logger.exception(f"Error retrieving embedding: {e}")
            raise ValueError(f"Error retrieving embedding: {e}")


    def calculate_similarity_threshold(self) -> float:
        """
        Calculates the 98th percentile of the similarity threshold across all agents.

        :return: 98th percentile of similarity threshold.
        """
        try:
            embeddings = [self.get_embedding(agent.purpose) for agent in self.agents]
            if len(embeddings) < 250:
                return 0.9

            similarities = [cosine_similarity([e1], [e2])[0][0] for i, e1 in enumerate(embeddings) for e2 in embeddings[i+1:]]
            return np.percentile(similarities, 98) if similarities else 0.9
        except Exception as e:
            logger.exception(f"Error calculating similarity threshold: {e}")
            raise ValueError(f"Error calculating similarity threshold: {e}")


    def find_closest_agent(self, purpose_embedding: np.ndarray) -> Tuple[Optional[Agent], float]:
        """
        Finds the closest agent based on the given purpose embedding.

        :param purpose_embedding: The embedding of the purpose to find the closest agent for.
        :return: Tuple of the closest agent and the highest similarity score.
        """
        closest_agent: Optional[Agent] = None
        highest_similarity: float = -np.inf

        try:
            for agent in self.agents:
                agent_embedding = self.get_embedding(agent.purpose)
                similarity = cosine_similarity([agent_embedding], [purpose_embedding])[0][0]

                if similarity > highest_similarity:
                    highest_similarity = similarity
                    closest_agent = agent

            return closest_agent, highest_similarity
        except Exception as e:
            logger.exception(f"Error finding closest agent: {e}")
            raise ValueError(f"Error finding closest agent: {e}")
