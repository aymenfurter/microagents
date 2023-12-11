import openai

class MicroAgent:
    def __init__(self, initial_prompt, purpose, all_agents, api_key):
        self.prompt = initial_prompt
        self.purpose = purpose
        self.all_agents = all_agents
        openai.api_key = api_key

    def process_input(self, input_text):
        combined_input = self.prompt + ' ' + input_text
        return combined_input

    def generate_response(self, combined_input):
        response = openai.Completion.create(engine="gpt-4", prompt=combined_input, max_tokens=150)
        return response.choices[0].text.strip()

    def evolve_prompt(self, feedback):
        self.prompt += ' ' + feedback

    def respond(self, input_text):
        combined_input = self.process_input(input_text)
        response = self.generate_response(combined_input)
        feedback = self.request_evaluations(response, input_text)
        self.evolve_prompt(feedback)
        return response

    def request_evaluations(self, response, input_text):
        # Determine the purpose for evaluation using GPT-4
        purpose_query = f"What is the appropriate purpose for evaluating this response? Input: {input_text} Response: {response}"
        purpose_response = openai.Completion.create(engine="gpt-4", prompt=purpose_query, max_tokens=50)
        evaluation_purpose = purpose_response.choices[0].text.strip()

        # Find the agent with the determined purpose
        evaluation_agent = self.find_agent_by_purpose(evaluation_purpose)
        if evaluation_agent:
            feedback = evaluation_agent.evaluate(response, input_text)
        else:
            feedback = "Good"  # Default feedback if no matching agent found
        return feedback

    def find_agent_by_purpose(self, purpose):
        for agent in self.all_agents:
            if agent.purpose == purpose:
                return agent
        return None

    def evaluate(self, response, input_text):
        # Formulate evaluation criteria using GPT-4
        evaluation_criteria_prompt = f"What are good criteria to evaluate this response? Input: {input_text} Response: {response}"
        criteria = openai.Completion.create(engine="gpt-4", prompt=evaluation_criteria_prompt, max_tokens=50)

        # Evaluate the response based on the generated criteria
        evaluation = openai.Completion.create(engine="gpt-4", prompt=f"Based on these criteria: {criteria.choices[0].text}, evaluate the response: {response}", max_tokens=10)
        return evaluation.choices[0].text.strip()
