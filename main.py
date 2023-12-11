from microagent import MicroAgent
import openai
import numpy as np

class MicroAgentManager:
    def __init__(self, api_key, max_agents=20):
        self.agents = []
        self.api_key = api_key
        self.max_agents = max_agents
        openai.api_key = api_key
        self.create_prime_agent()

    def create_prime_agent(self):
        prime_agent = MicroAgent("Initial Prompt for General Tasks", "General", self.agents, self.api_key)
        self.agents.append(prime_agent)

    def get_embedding(self, text):
        response = openai.Embedding.create(input=text, engine="text-embedding-ada-002")
        return np.array(response['data'][0]['embedding'])

    def calculate_similarity_threshold(self):
        if len(self.agents) < 2:
            return 0.7  # Default threshold if not enough agents for comparison

        embeddings = [self.get_embedding(agent.purpose) for agent in self.agents]
        avg_similarity = np.mean([np.dot(e1, e2) / (np.linalg.norm(e1) * np.linalg.norm(e2)) for e1 in embeddings for e2 in embeddings if not np.array_equal(e1, e2)])
        return avg_similarity

    def find_closest_agent(self, purpose_embedding):
        closest_agent = None
        highest_similarity = -np.inf

        for agent in self.agents:
            agent_embedding = self.get_embedding(agent.purpose)
            similarity = np.dot(agent_embedding, purpose_embedding) / (np.linalg.norm(agent_embedding) * np.linalg.norm(purpose_embedding))

            if similarity > highest_similarity:
                highest_similarity = similarity
                closest_agent = agent

        return closest_agent, highest_similarity

    def get_or_create_agent(self, purpose):
        purpose_embedding = self.get_embedding(purpose)
        closest_agent, highest_similarity = self.find_closest_agent(purpose_embedding)
        similarity_threshold = self.calculate_similarity_threshold()

        if highest_similarity >= similarity_threshold:
            closest_agent.usage_count += 1
            return closest_agent

        if len(self.agents) >= self.max_agents:
            self.agents.sort(key=lambda x: x.usage_count)
            self.agents.pop(0)

        new_agent = MicroAgent("Initial Prompt for " + purpose, purpose, self.agents, self.api_key)
        new_agent.usage_count = 1
        self.agents.append(new_agent)
        return new_agent

    def goal_reached(self, response, user_input):
        evaluation_prompt = f"Given the user input: '{user_input}', and the agent response: '{response}', has the goal been achieved? Respond with 'goal achieved' or 'goal not achieved'."
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": evaluation_prompt}
        ]
        evaluation = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages
        )
        return "goal achieved" in evaluation.choices[0].message['content'].lower()

    def respond(self, input_text):
        prime_agent = self.agents[0]
        purpose = prime_agent.generate_response(f"Determine the purpose for: {input_text}")

        agent = self.get_or_create_agent(purpose)
        response = agent.respond(input_text)

        if self.goal_reached(response, input_text):
            print("Goal has been reached with response:", response)
        else:
            print("Continuing interaction. Response:", response)

        return response

def main():
    api_key = 'your-openai-api-key'
    manager = MicroAgentManager(api_key)

    user_input = "What is the capital of France?"
    manager.respond(user_input)

if __name__ == "__main__":
    main()
