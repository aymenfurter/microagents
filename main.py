from microagent import MicroAgent
import time
from openaiwrapper import OpenAIAPIWrapper
import os
import openai
import numpy as np
import logging
from sklearn.metrics.pairwise import cosine_similarity

class MicroAgentManager:
    def __init__(self, api_key, max_agents=20):
        self.agents = []
        self.api_key = api_key
        self.max_agents = max_agents
        self.openai_wrapper = OpenAIAPIWrapper(api_key)
        self.create_prime_agent()
        self.self_optimization = True

    def create_prime_agent(self):
        prime_agent = MicroAgent("This is the prime agent. You are only allowed to call other agents. Prime Agent's prompt may not be changed", "General", self, self.api_key, 0, 25, True)
        self.agents.append(prime_agent)

    def get_embedding(self, text):
        response = self.openai_wrapper.get_embedding(text)
        return np.array(response['data'][0]['embedding'])

    def calculate_similarity_threshold(self):
        if len(self.agents) < 2:
            return 0.9  # Default threshold if not enough agents for comparison

        embeddings = [self.get_embedding(agent.purpose) for agent in self.agents]
        avg_similarity = np.mean([np.dot(e1, e2) / (np.linalg.norm(e1) * np.linalg.norm(e2)) for e1 in embeddings for e2 in embeddings if not np.array_equal(e1, e2)])
        return avg_similarity

    def find_closest_agent(self, purpose_embedding):
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

        print("Creating new agent for purpose:", purpose)
        prompt = self.generate_llm_prompt(purpose, sample_input)
        new_agent = MicroAgent(prompt, purpose, self, self.api_key, depth=depth)
        new_agent.usage_count = 1
        self.agents.append(new_agent)
        return new_agent
    def extractResponseFromPrompt(self, prompt, question):
        extraction_prompt = f"Extract the response for question '{question}' from the following prompt: '{prompt}'. If it is not present, give a 10 word explaination why it failed."
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": extraction_prompt}
        ]
        extraction = self.openai_wrapper.chat_completion(
            model="gpt-4",
            messages=messages,
            max_tokens=100,
        )

        return extraction.choices[0].message['content'].strip()

    def goal_reached(self, response, user_input):
        evaluation_prompt = f"Given the user input: '{user_input}', and the agent response: '{response}', has the goal been achieved? Respond with 'goal achieved' or 'goal not achieved'."
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": evaluation_prompt}
        ]
        evaluation = self.openai_wrapper.chat_completion(
            model="gpt-4",
            messages=messages
        )
        return "goal achieved" in evaluation.choices[0].message['content'].lower()

    def generate_llm_prompt(self, goal, sample_input):
        """
        Generate a high-quality prompt for an LLM based on the goal, incorporating prompt engineering best practices and detailed examples, including a Python code snippet in Markdown format. Never use API KEYS or passwords in your code. Code must be runnable, besides the dynamic part coming as input. (e.g. weather code must work but may container a placeholder with the location to be filled.). Keep the code simple. 

        :param goal: The primary goal or purpose of the LLM's response.
        :return: A structured prompt for the LLM.
        """
        examples = [
            "Goal: Your purpose is to be able to write blog posts. Generated Prompt: You are an expert writer on the topic of blog posts.",
            "Goal: Your purpose is to count the words of the input. Generated Prompt: # You are a useful assistant that is able to count words. You can use the following code during execution to count word frequencies. Here is sample code, adopt as needed:```python\nfrom collections import Counter\n\n\nwords = text.split()\nword_counts = Counter(words)\nprint(word_counts)\n```.",
            "Goal: Your purpose is to solve basic arithmetic problems. Generated Prompt: You are a proficient calculator. Here's a Python function to solve a basic arithmetic problem, here is some sample code, adopt as needed.: ```python\nprint(eval(problem))\n\n# Example problem: What is 15 times 4?\nprint(eval('15 * 4'))\n```.",
            "Goal: Your purpose is to generate creative writing prompts. Generated Prompt: You are a creative muse who can come up with engaging and unique writing prompts. Provide an intriguing prompt for a science fiction story set in a distant galaxy.",
            "Goal: Your purpose is to translate sentences from English to Spanish. Generated Prompt: You are an efficient language translator. Translate the following sentence into Spanish: 'The sun rises early in the morning.'",
            "Goal: Your purpose is to query the Wikipedia API for the current president of a specified country and extract the relevant information. Generated Prompt: You are an adept information retriever. Use the code snippet to query the Wikipedia API for the current president of a specified country and extract the relevant information. Ensure the code is specific enough to identify the president's name. ```python\nimport requests\n\ndef get_current_president(country):\n    S = requests.Session()\n    URL = f\"https://en.wikipedia.org/w/api.php\"\n    PARAMS = {\n        \"action\": \"query\",\n        \"format\": \"json\",\n        \"titles\": f\"President_of_{country}\",\n        \"prop\": \"extracts\",\n        \"exintro\": True,\n        \"explaintext\": True,\n    }\n\n    response = S.get(url=URL, params=PARAMS).json()\n    page = next(iter(response[\"query\"][\"pages\"].values()))\n    extract = page[\"extract\"]\n    print(extract)\n\n# Example usage: get_current_president(\"France\")\n```"
        ]

        messages = [
            {"role": "system", "content": "You are a helpful assistant knowledgeable in prompt engineering."},
            {"role": "user", "content": f"Using best practices in prompt engineering, create a detailed prompt for the goal '{goal}'. This generated prompt will be combined with the following context later (but must be genertic and is forbidden to contain any of the following context): '{sample_input}'\n  Examples: {examples}. Aim for maximum 50 words. Important: Any problems must be solved through sample code or learned information provided in the prompt. Any sample code provided must be executable in isolation. Avoid unresolveable placerholder for URLs and API Keys. If you retrieve information from the web, avoid parsing HTML Code or use regex, just process the textdata and print it out (As shown in the examples)!!! As long as the answer is somewhere in the output, and it is below 1k characters, its a perfect solution. Use real existing services and websites. Don't invent services or use example.com."}
        ]
        
        response = self.openai_wrapper.chat_completion(
            model="gpt-4-1106-preview",  # Using the specified model
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

def main():
    api_key = os.environ["OPENAI_KEY"]
    manager = MicroAgentManager(api_key)
    
    user_inputs = [
        "What is 5*10?",
        "What are the most popular GitHub repositories?",
        "What is the population of Thailand?",
        "What is the population of Sweden?",
        "What is the population of the smallest country on earth?",
        "What is the biggest news headline right now?"
    ]
    
    for user_input in user_inputs:
        start_time = time.time()
        response = manager.respond(user_input)
        final_response = manager.extractResponseFromPrompt(response, user_input)
        print("Question:", user_input)
        print("Response:", final_response)
        end_time = time.time() - start_time
        print("Time taken:", end_time)
        print("Number of Agents:", len(manager.agents))

if __name__ == "__main__":
    main()
