import unittest
from unittest.mock import Mock, patch
from agents.agent_lifecycle import AgentLifecycle
from agents.agent_persistence_manager import AgentPersistenceManager
from agents.microagent import MicroAgent

from integrations.openaiwrapper import OpenAIAPIWrapper

class TestAgentLifecycle(unittest.TestCase):

    def setUp(self):
        self.openai_wrapper_mock = Mock(spec=OpenAIAPIWrapper)
        self.agent_persistence_mock = Mock(spec=AgentPersistenceManager)
        self.agent_lifecycle = AgentLifecycle(self.openai_wrapper_mock, self.agent_persistence_mock)
        self.dummy_agent = MicroAgent("dummy_prompt", "dummy_name", 0, self.agent_lifecycle, self.openai_wrapper_mock)

    def test_cleanup_agents_removes_stopped_agents(self):
        self.agent_lifecycle.agents = [self.dummy_agent]
        self.dummy_agent.stopped = True

        self.agent_lifecycle.cleanup_agents()

        self.assertEqual(len(self.agent_lifecycle.agents), 0)

    def test_create_prime_agent_adds_agent(self):
        with patch('agents.microagent.MicroAgent') as MockAgent:
            MockAgent.return_value = self.dummy_agent

            self.agent_lifecycle.create_prime_agent()

            self.assertEqual(len(self.agent_lifecycle.agents), 1)
            self.assertEqual(self.agent_lifecycle.agents[0].purpose, "Bootstrap Agent")

    def test_save_agent_calls_persistence_save(self):
        self.agent_lifecycle.save_agent(self.dummy_agent)

        self.agent_persistence_mock.save_agent.assert_called_with(self.dummy_agent)

    def test_generate_llm_prompt_returns_prompt(self):
        expected_prompt = "generated_prompt"
        self.openai_wrapper_mock.chat_completion.return_value = expected_prompt
        actual_prompt = self.agent_lifecycle._generate_llm_prompt("goal", "sample_input")

        self.assertEqual(actual_prompt, expected_prompt)

if __name__ == '__main__':
    unittest.main()
