from microagent import MicroAgent
import openai
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class MicroAgentManager:
    def __init__(self, api_key, max_agents=20):
        self.agents = []
        self.api_key = api_key
        self.max_agents = max_agents
        openai.api_key = api_key
        self.create_prime_agent()

    def create_prime_agent(self):
        # Pass the manager itself (self) to the prime agent
        prime_agent = MicroAgent("Initial Prompt for General Tasks. This is the prime agent. You are only allowed to call other agents. Prime Agent's prompt may not be changed", "General", self, self.api_key)
        self.agents.append(prime_agent)

    def get_embedding(self, text):
        response = openai.Embedding.create(input=text, engine="text-embedding-ada-002")
        return np.array(response['data'][0]['embedding'])

    def calculate_similarity_threshold(self):
        if len(self.agents) < 2:
            return 0.9  # Default threshold if not enough agents for comparison

        embeddings = [self.get_embedding(agent.purpose) for agent in self.agents]
        avg_similarity = np.mean([np.dot(e1, e2) / (np.linalg.norm(e1) * np.linalg.norm(e2)) for e1 in embeddings for e2 in embeddings if not np.array_equal(e1, e2)])
        return avg_similarity

    def find_closest_agent(self, purpose_embedding):
        print("Finding closest agent for purpose embedding:", purpose_embedding)
        closest_agent = None
        highest_similarity = -np.inf

        available_agents = [agent for agent in self.agents if agent.purpose != "General"]
        for agent in available_agents:
            agent_embedding = self.get_embedding(agent.purpose)
            similarity = cosine_similarity([agent_embedding], [purpose_embedding])[0][0]

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

        print("Creating new agent for purpose:", purpose)
        new_agent = MicroAgent("Initial Prompt for " + purpose, purpose, self, self.api_key)
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
        # Pass the manager to the generate_response method
        purpose = prime_agent.generate_response(f"Your Goal: {input_text}")

        agent = self.get_or_create_agent(purpose)
        # Pass the manager to the agent's respond method
        response = agent.respond(input_text)

        while not self.goal_reached(response, input_text):
            response = agent.respond(input_text + " // Previous response: " + response)

        return response

def main():
    api_key = "YOUR_API_KEY"
    manager = MicroAgentManager(api_key)

    user_input = "Who is the current president in 2023 of france?"
    manager.respond(user_input)

if __name__ == "__main__":
    main()
