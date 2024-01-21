import numpy as np
import unittest
from agents.microagent import MicroAgent
from agents.agent_serializer import AgentSerializer
from unittest.mock import Mock
from integrations.openaiwrapper import OpenAIAPIWrapper

class TestAgentSerializer(unittest.TestCase):

    def test_full_serialization(self):
        self.mock_agent_lifecycle = Mock()
        self.mock_openai_wrapper = OpenAIAPIWrapper("api_key")
        agent = MicroAgent("dynamic prompt", "purpose", 2, self.mock_agent_lifecycle, self.mock_openai_wrapper, 5)
        agent.purpose_embedding = np.array([1, 2, 3])
        agent.usage_count = 10
        agent.working_agent = True
        agent.is_prime = False
        agent.evolve_count = 3
        agent.number_of_code_executions = 20
        agent.last_input = "test input"

        serialized_agent = AgentSerializer.to_dict(agent)
        self.assertEqual(serialized_agent["dynamic_prompt"], "dynamic prompt")
        self.assertEqual(serialized_agent["purpose"], "purpose")
        self.assertEqual(serialized_agent["purpose_embedding"], [1, 2, 3])
        self.assertEqual(serialized_agent["usage_count"], 10)
        self.assertTrue(serialized_agent["working_agent"])
        self.assertFalse(serialized_agent["is_prime"])
        self.assertEqual(serialized_agent["evolve_count"], 3)
        self.assertEqual(serialized_agent["number_of_code_executions"], 20)
        self.assertEqual(serialized_agent["last_input"], "test input")

    def test_deserialization(self):
        self.mock_agent_lifecycle = Mock()
        self.mock_openai_wrapper = OpenAIAPIWrapper("api_key")
        agent_data = {
            "dynamic_prompt": "dynamic prompt",
            "purpose": "purpose",
            "purpose_embedding": [1, 2, 3],
            "depth": 2,
            "max_depth": 5,
            "usage_count": 10,
            "working_agent": True,
            "is_prime": False,
            "evolve_count": 3,
            "id": 1,
            "parent_id": 2,
            "number_of_code_executions": 20,
            "last_input": "test input"
        }

        agent = AgentSerializer.from_dict(agent_data, self.mock_agent_lifecycle, self.mock_openai_wrapper)
        self.assertEqual(agent.dynamic_prompt, "dynamic prompt")
        self.assertEqual(agent.purpose, "purpose")
        np.testing.assert_array_equal(agent.purpose_embedding, np.array([1, 2, 3]))
        self.assertEqual(agent.depth, 2)
        self.assertEqual(agent.max_depth, 5)
        self.assertEqual(agent.usage_count, 10)
        self.assertTrue(agent.working_agent)
        self.assertFalse(agent.is_prime)
        self.assertEqual(agent.evolve_count, 3)
        self.assertEqual(agent.number_of_code_executions, 20)
        self.assertEqual(agent.last_input, "test input")

if __name__ == '__main__':
    unittest.main()
