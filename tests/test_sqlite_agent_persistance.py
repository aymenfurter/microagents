import unittest
import sqlite3
import tempfile
import os
import json
from integrations.sqlite_agent_persistence import SQLiteAgentPersistence

class TestSQLiteAgentPersistence(unittest.TestCase):

    def setUp(self):
        self.db_file = tempfile.mktemp()
        self.persistence = SQLiteAgentPersistence(filename=self.db_file)

    def tearDown(self):
        os.remove(self.db_file)

    def _count_agents_in_db(self):
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM agents")
            return cursor.fetchone()[0]

    def test_initialize_database(self):
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='agents'")
            self.assertIsNotNone(cursor.fetchone())

    def test_save_agent(self):
        agent_dict = {'purpose': 'test', 'data': 'some_data', 'id': 'test_id'}
        self.persistence.save_agent(agent_dict)

        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT data FROM agents WHERE purpose = ?", (agent_dict['purpose'],))
            data = cursor.fetchone()
            self.assertIsNotNone(data)
            self.assertEqual(json.loads(data[0]), agent_dict)

    def test_fetch_agent(self):
        agent_dict = {'purpose': 'fetch_test', 'data': 'fetch_data', 'id': 'fetch_id'}
        self.persistence.save_agent(agent_dict)

        fetched_agent = self.persistence.fetch_agent('fetch_test')
        self.assertEqual(fetched_agent, agent_dict)

    def test_load_all_purposes(self):
        agent_dict1 = {'purpose': 'purpose1', 'data': 'data1', 'id': 'test_id'}
        agent_dict2 = {'purpose': 'purpose2', 'data': 'data2', 'id': 'test_id2'}
        self.persistence.save_agent(agent_dict1)
        self.persistence.save_agent(agent_dict2)

        purposes = self.persistence.load_all_purposes()
        self.assertIn('purpose1', purposes)
        self.assertIn('purpose2', purposes)

    def test_non_existent_agent(self):
        self.assertIsNone(self.persistence.fetch_agent('non_existent'))

if __name__ == '__main__':
    unittest.main()
