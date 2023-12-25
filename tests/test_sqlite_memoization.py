import unittest
from unittest.mock import MagicMock
from integrations.memoize import SQLiteMemoization, memoize_to_sqlite
import uuid
import os

class TestSQLiteMemoization(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db_file = 'test.db'
        cls.memoizer = SQLiteMemoization(cls.db_file)
        cls.memoizer.__enter__() 

    @classmethod
    def tearDownClass(cls):
        cls.memoizer.__exit__(None, None, None)
        os.remove(cls.db_file)

    def test_initialization_creates_cache_table(self):
        cursor = self.memoizer.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cache'")
        self.assertIsNotNone(cursor.fetchone(), "Cache table should be created during initialization")

    def test_hash_computation_returns_string(self):
        test_hash = self.memoizer._compute_hash('test_func', 1, 2, 3, key='value')
        self.assertIsInstance(test_hash, str, "Hash computation should return a string")

    def test_caching_mechanism_stores_and_retrieves_data_correctly(self):
        test_hash = self.memoizer._compute_hash('test_func', 1, 2, 3)
        self.memoizer._cache_result(test_hash, "test_result")
        cached_result = self.memoizer._fetch_from_cache(test_hash)
        self.assertEqual(cached_result, "test_result", "Caching mechanism should store and retrieve data correctly")

    def test_memoization_decorator_caches_function_output(self):
        return_pong = MagicMock(return_value="pong")
        unique_arg = uuid.uuid4().hex

        @memoize_to_sqlite('test_func', self.db_file)
        def ping(arg):
            return return_pong(arg)

        self.assertEqual(ping(unique_arg), "pong")
        return_pong.assert_called_once()

        return_pong.reset_mock()
        self.assertEqual(ping(unique_arg), "pong")
        return_pong.assert_not_called()

    def test_resource_management_closes_connection(self):
        with SQLiteMemoization(self.db_file) as memoizer:
            self.assertIsNotNone(memoizer.connection, "Connection should be established")
        self.assertIsNone(memoizer.connection, "Connection should be closed after context manager exit")

if __name__ == '__main__':
    unittest.main()
