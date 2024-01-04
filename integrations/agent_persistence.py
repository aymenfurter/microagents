class AbstractAgentPersistence:
    def save_agent(self, agent_dict):
        """
        Save the serialized agent to the persistence layer.
        """
        raise NotImplementedError

    def fetch_agent(self, purpose):
        """
        Fetch a serialized agent based on its purpose.
        """
        raise NotImplementedError

    def load_all_purposes(self):
        """
        Load all agent purposes from the persistence layer.
        """
        raise NotImplementedError