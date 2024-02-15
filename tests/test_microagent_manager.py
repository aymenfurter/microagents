import unittest
from unittest.mock import Mock, patch
from agents.microagent_manager import MicroAgentManager
from integrations.openaiwrapper import OpenAIAPIWrapper
import openai

class TestMicroAgentManager(unittest.TestCase):

    def setUp(self):
        self.openai_wrapper = OpenAIAPIWrapper(openai.OpenAI(api_key="dummy_key"))
        self.max_agents = 20
        self.db_filename = "agents.db"
        self.micro_agent_manager = MicroAgentManager(self.openai_wrapper, self.max_agents, self.db_filename)

    @patch('agents.microagent_manager.OpenAIAPIWrapper')
    @patch('agents.microagent_manager.AgentPersistenceManager')
    @patch('agents.microagent_manager.AgentLifecycle')
    def test_init(self, MockAgentLifecycle, MockAgentPersistenceManager, MockOpenAIAPIWrapper):
        micro_agent_manager = MicroAgentManager(self.openai_wrapper, self.max_agents, self.db_filename)
        self.assertIsInstance(micro_agent_manager, MicroAgentManager)

    @patch('agents.microagent_manager.logging')
    def test_cleanup_agents(self, mock_logging):
        self.micro_agent_manager.agent_lifecycle = Mock()
        self.micro_agent_manager.cleanup_agents()
        self.micro_agent_manager.agent_lifecycle.cleanup_agents.assert_called_once()

    @patch('agents.microagent_manager.logging')
    def test_get_agents(self, mock_logging):
        self.micro_agent_manager.agent_lifecycle = Mock()
        self.micro_agent_manager.get_agents()
        self.micro_agent_manager.agent_lifecycle.cleanup_agents.assert_called_once()

if __name__ == '__main__':
    unittest.main()
