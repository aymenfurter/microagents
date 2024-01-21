import sqlite3
import json
from integrations.agent_persistence import AbstractAgentPersistence

class SQLiteAgentPersistence(AbstractAgentPersistence):
    def __init__(self, filename="agents.db"):
        self.filename = filename
        self._initialize_database()

    def _initialize_database(self):
        """
        Initialize the SQLite database with the required schema.
        """
        with sqlite3.connect(self.filename) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS agents (
                    id TEXT PRIMARY KEY,
                    purpose TEXT,
                    data TEXT
                )
            """)
    def remove_agent(self, purpose):
        """
        Remove an agent from the SQLite database.
        """
        with sqlite3.connect(self.filename) as conn:
            conn.execute("DELETE FROM agents WHERE id = ?", (purpose,))

    def save_agent(self, agent_dict):
        """
        Save the serialized agent to an SQLite database.
        """
        with sqlite3.connect(self.filename) as conn:
            conn.execute(
                # add id field
                "REPLACE INTO agents (id, purpose, data) VALUES (?, ?, ?)",
                (agent_dict['id'], agent_dict['purpose'], json.dumps(agent_dict))
            )

    def fetch_agent(self, purpose):
        """
        Fetch a serialized agent based on its purpose from the SQLite database.
        """
        with sqlite3.connect(self.filename) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT data FROM agents WHERE purpose = ?", (purpose,))
            row = cursor.fetchone()
            return json.loads(row[0]) if row else None

    def load_all_purposes(self):
        """
        Load all agent purposes from the SQLite database.
        """
        with sqlite3.connect(self.filename) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT purpose FROM agents")
            return [row[0] for row in cursor.fetchall()]