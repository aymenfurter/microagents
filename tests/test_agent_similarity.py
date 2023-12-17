import unittest
from unittest.mock import Mock
import numpy as np
from agents.agent_creation import AgentCreation
from agents.agent_similarity import AgentSimilarity 
from agents.microagent import MicroAgent
from integrations.openaiwrapper import OpenAIAPIWrapper

class TestAgentSimilarity(unittest.TestCase):
    
    def setUp(self):
        # Mocking the OpenAIAPIWrapper
        self.mock_openai_wrapper = Mock()
        self.openai_wrapper = OpenAIAPIWrapper("api_key")
        self.agent_creator = AgentCreation(self.openai_wrapper, 5)
        self.agents = [MicroAgent("initial_prompt", "purpose1", "api_key", self.agent_creator, self.openai_wrapper, None),
                          MicroAgent("initial_prompt", "purpose2", "api_key", self.agent_creator, self.openai_wrapper, None),
                          MicroAgent("initial_prompt", "purpose3", "api_key", self.agent_creator, self.openai_wrapper, None)] 


        self.agent_similarity = AgentSimilarity(self.mock_openai_wrapper, self.agents)

    def test_find_closest_agent(self):
        self.mock_openai_wrapper.get_embedding.side_effect = [
            {'data': [{'embedding': [0.1, 0.2, 0.3]}]},
            {'data': [{'embedding': [0.4, 0.5, 0.6]}]},
            {'data': [{'embedding': [0.7, 0.8, 0.9]}]}
        ]

        test_purpose_embedding = np.array([0.4, 0.5, 0.6])
        closest_agent, similarity = self.agent_similarity.find_closest_agent(test_purpose_embedding)

        self.assertIsNotNone(closest_agent)
        self.assertAlmostEqual(similarity, 1.0)  # Assuming cosine similarity is 1.0 for identical vectors

if __name__ == '__main__':
    unittest.main()
