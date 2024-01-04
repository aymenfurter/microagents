import unittest
from unittest.mock import Mock, patch
from agents.agent_serializer import AgentSerializer
from agents.agent_persistence_manager import AgentPersistenceManager
from integrations.sqlite_agent_persistence import SQLiteAgentPersistence
from integrations.openaiwrapper import OpenAIAPIWrapper

class TestAgentPersistenceManager(unittest.TestCase):

    def setUp(self):
        self.mock_agent_lifecycle = Mock()
        self.mock_openai_wrapper = OpenAIAPIWrapper("api_key")
        self.mock_persistence = Mock(spec=SQLiteAgentPersistence)
        self.manager = AgentPersistenceManager(
            db_filename=":memory:"
        )
        self.manager.persistence = self.mock_persistence

    def test_save_agent_working_not_prime(self):
        mock_agent = Mock()
        mock_agent.working_agent = True
        mock_agent.is_prime = False
        mock_agent_dict = {'purpose': 'test', 'data': 'some_data'}

        with patch('agents.agent_serializer.AgentSerializer.to_dict', return_value=mock_agent_dict):
            self.manager.save_agent(mock_agent)

        self.mock_persistence.save_agent.assert_called_once_with(mock_agent_dict)

    def test_save_agent_not_working_or_prime(self):
        mock_agent = Mock()
        mock_agent.working_agent = False
        mock_agent.is_prime = True

        self.manager.save_agent(mock_agent)

        self.mock_persistence.save_agent.assert_not_called()

    def test_load_agent_existing(self):
        purpose = 'test'
        mock_agent_dict = {'purpose': purpose, 'data': 'some_data'}
        self.mock_persistence.fetch_agent.return_value = mock_agent_dict


        with patch('agents.agent_serializer.AgentSerializer.from_dict') as mock_from_dict:
            self.manager.load_agent(purpose, self.mock_agent_lifecycle, self.mock_openai_wrapper)

        mock_from_dict.assert_called_once_with(mock_agent_dict, self.mock_agent_lifecycle, self.mock_openai_wrapper)

    def test_load_agent_non_existing(self):
        self.mock_persistence.fetch_agent.return_value = None
        result = self.manager.load_agent('non_existent', self.mock_agent_lifecycle, self.mock_openai_wrapper)

        self.assertIsNone(result)

    def test_load_all_agents(self):
        self.mock_persistence.load_all_purposes.return_value = ['purpose1', 'purpose2']
        self.mock_persistence.fetch_agent.side_effect = [{'purpose': 'purpose1', 'data': 'data1'}, {'purpose': 'purpose2', 'data': 'data2'}]

        with patch('agents.agent_serializer.AgentSerializer.from_dict') as mock_from_dict:
            agents = self.manager.load_all_agents(self.mock_agent_lifecycle, self.mock_openai_wrapper)

        self.assertEqual(len(agents), 2)
        self.assertEqual(mock_from_dict.call_count, 2)

if __name__ == '__main__':
    unittest.main()
