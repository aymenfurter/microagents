from microagent import MicroAgent
from openaiwrapper import OpenAIAPIWrapper
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from prompts import PRIME_PROMPT
from prompts import PRIME_NAME
from prompts import EXAMPLES
from prompts import PROMPT_ENGINEERING_SYSTEM_PROMPT
from prompts import PROMPT_ENGINEERING_TEMPLATE
from prompts import GOAL_REACHED_PROMPT_TEMPLATE
from prompts import EXTRACTION_PROMPT_TEMPLATE
from prompts import STANDARD_SYSTEM_PROMPT

class MicroAgentManager:
    def __init__(self, api_key, max_agents=20):
        self.agents = []
        self.api_key = api_key
        self.max_agents = max_agents
        self.openai_wrapper = OpenAIAPIWrapper(api_key)
        self.create_prime_agent()
        self.self_optimization = True

    def create_prime_agent(self):
        prime_agent = MicroAgent(PRIME_PROMPT, PRIME_NAME, self, self.api_key, 0, 25, True)
        self.agents.append(prime_agent)

    def get_embedding(self, text):
        response = self.openai_wrapper.get_embedding(text)
        return np.array(response['data'][0]['embedding'])

    def calculate_similarity_threshold(self):
        if len(self.agents) < 2:
            return 0.9 

        embeddings = [self.get_embedding(agent.purpose) for agent in self.agents]
        avg_similarity = np.mean([np.dot(e1, e2) / (np.linalg.norm(e1) * np.linalg.norm(e2)) for e1 in embeddings for e2 in embeddings if not np.array_equal(e1, e2)])
        return avg_similarity

    def find_closest_agent(self, purpose_embedding):
        closest_agent = None
        highest_similarity = -np.inf

        available_agents = [agent for agent in self.agents if agent.purpose != PRIME_NAME]
        for agent in available_agents:
            agent_embedding = self.get_embedding(agent.purpose)
            similarity = cosine_similarity([agent_embedding], [purpose_embedding])[0][0]

            if similarity > highest_similarity:
                highest_similarity = similarity
                closest_agent = agent

        return closest_agent, highest_similarity

    def get_or_create_agent(self, purpose, depth, sample_input):
        purpose_embedding = self.get_embedding(purpose)
        closest_agent, highest_similarity = self.find_closest_agent(purpose_embedding)
        similarity_threshold = self.calculate_similarity_threshold()

        if highest_similarity >= similarity_threshold:
            closest_agent.usage_count += 1
            return closest_agent

        if len(self.agents) >= self.max_agents:
            self.agents.sort(key=lambda x: x.usage_count)
            self.agents.pop(0)

        prompt = self.generate_llm_prompt(purpose, sample_input)
        new_agent = MicroAgent(prompt, purpose, self, self.api_key, depth=depth)
        new_agent.usage_count = 1
        self.agents.append(new_agent)
        return new_agent

    def extractResponseFromPrompt(self, prompt, question):
        extraction_prompt = EXTRACTION_PROMPT_TEMPLATE.format(question=question, prompt=prompt)

        messages = [
            {"role": "system", "content": STANDARD_SYSTEM_PROMPT},
            {"role": "user", "content": extraction_prompt}
        ]
        extraction = self.openai_wrapper.chat_completion(
            model="gpt-4",
            messages=messages,
            max_tokens=100,
        )

        return extraction.choices[0].message['content'].strip()

    def goal_reached(self, response, user_input):
        goal_reached_prompt = GOAL_REACHED_PROMPT_TEMPLATE.format(user_input=user_input, response=response)
        messages = [
            {"role": "system", "content": STANDARD_SYSTEM_PROMPT},
            {"role": "user", "content": goal_reached_prompt}
        ]
        evaluation = self.openai_wrapper.chat_completion(
            model="gpt-4",
            messages=messages
        )
        return "goal achieved" in evaluation.choices[0].message['content'].lower()

    def generate_llm_prompt(self, goal, sample_input):
        messages = [
            {"role": "system", "content": PROMPT_ENGINEERING_SYSTEM_PROMPT},
            {"role": "user", "content": PROMPT_ENGINEERING_TEMPLATE.format(goal=goal, sample_input=sample_input, EXAMPLES=EXAMPLES)}

        ]
        
        response = self.openai_wrapper.chat_completion(
            model="gpt-4-1106-preview",
            messages=messages
        )

        generated_prompt = response.choices[0].message['content'].strip()

        return generated_prompt 

    def respond(self, input_text):
        prime_agent = self.agents[0]
        response = prime_agent.generate_response(f"Your Goal: {input_text}")
        
        while not self.goal_reached(response, input_text):
            response = prime_agent.respond(input_text + " // Previous response: " + response)

        return response