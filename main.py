from microagent import MicroAgent
import openai

class MicroAgentManager:
    def __init__(self, api_key, max_agents=20):
        self.agents = []
        self.api_key = api_key
        self.max_agents = max_agents

    def get_or_create_agent(self, purpose):
        # Find an existing agent with the given purpose
        for agent in self.agents:
            if agent.purpose == purpose:
                agent.usage_count += 1
                return agent
        
        # If max number of agents is reached, remove the least used agent
        if len(self.agents) >= self.max_agents:
            self.agents.sort(key=lambda x: x.usage_count)
            self.agents.pop(0)

        # Create a new agent
        new_agent = MicroAgent("Initial Prompt for " + purpose, purpose, self.agents, self.api_key)
        new_agent.usage_count = 1
        self.agents.append(new_agent)
        return new_agent

    def respond(self, input_text):
        # Determine the purpose for the input text using a generic agent
        generic_agent = self.get_or_create_agent("General")
        purpose = generic_agent.generate_response(f"Determine the purpose for: {input_text}")

        # Get or create an agent for this purpose
        agent = self.get_or_create_agent(purpose)
        return agent.respond(input_text)

def main():
    api_key = 'your-openai-api-key'  # Replace with your actual OpenAI API key
    manager = MicroAgentManager(api_key)

    # Example interaction
    user_input = "Calculate the sum of 4 and 5."
    response = manager.respond(user_input)
    print("Response:", response)

if __name__ == "__main__":
    main()
