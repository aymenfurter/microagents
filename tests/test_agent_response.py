import unittest

from agents.agent_response import AgentResponse

class TestAgentResponse(unittest.TestCase):
    def setUp(self):
        # Setup your OpenAIAPIWrapper, Manager, and other dependencies here
        # For the test, we can use mock objects or simplified versions
        self.agent_response = AgentResponse(None, None, None, None, None, None)

    def test_parse_agent_info(self):
        # Standard case
        response = 'Use Agent[ReadTitle:https://google.com]'
        agent_name, input_text = self.agent_response._parse_agent_info(response)
        self.assertEqual(agent_name, 'ReadTitle')
        self.assertEqual(input_text, 'https://google.com')

        # No URL case
        response = 'Use Agent[SimpleAgent]'
        agent_name, input_text = self.agent_response._parse_agent_info(response)
        self.assertEqual(agent_name, 'SimpleAgent')
        self.assertEqual(input_text, '')

        # Agent name and no input text
        response = 'Use Agent[DataAgent:]'
        agent_name, input_text = self.agent_response._parse_agent_info(response)
        self.assertEqual(agent_name, 'DataAgent')
        self.assertEqual(input_text, '')

        # Malformed string
        response = 'This is not a correct format'
        with self.assertRaises(IndexError):
            self.agent_response._parse_agent_info(response)

if __name__ == '__main__':
    unittest.main()
