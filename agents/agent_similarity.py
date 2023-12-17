import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from integrations.openaiwrapper import OpenAIAPIWrapper

class AgentSimilarity:
    def __init__(self, openai_wrapper, agents):
        self.openai_wrapper = openai_wrapper
        self.agents = agents

    def get_embedding(self, text):
        """
        Retrieves the embedding for a given text.
        """
        response = self.openai_wrapper.get_embedding(text)
        return np.array(response['data'][0]['embedding'])

    def calculate_similarity_threshold(self):
        """
        Calculates the average similarity threshold across all agents.
        """
        embeddings = [self.get_embedding(agent.purpose) for agent in self.agents]
        if len(embeddings) < 2:
            return 0.9

        avg_similarity = np.mean([np.dot(e1, e2) / (np.linalg.norm(e1) * np.linalg.norm(e2)) for e1 in embeddings for e2 in embeddings if not np.array_equal(e1, e2)])
        return avg_similarity

    def find_closest_agent(self, purpose_embedding):
        """
        Finds the closest agent based on the given purpose embedding.
        """
        closest_agent = None
        highest_similarity = -np.inf

        for agent in self.agents:
            agent_embedding = self.get_embedding(agent.purpose)
            similarity = cosine_similarity([agent_embedding], [purpose_embedding])[0][0]

            if similarity > highest_similarity:
                highest_similarity = similarity
                closest_agent = agent

        return closest_agent, highest_similarity