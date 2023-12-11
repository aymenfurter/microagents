import openai
import subprocess
import shlex

class MicroAgent:
    def __init__(self, initial_prompt, purpose, all_agents, api_key, depth=0, max_depth=5):
        self.prompt = initial_prompt
        self.purpose = purpose
        self.all_agents = all_agents
        self.api_key = api_key
        self.depth = depth
        self.max_depth = max_depth
        openai.api_key = api_key
        self.code_block_start = "```"
        self.code_block_end = "```"

    def generate_response(self, input_text):
        combined_input = self.prompt + ' ' + input_text
        response = openai.Completion.create(engine="gpt-4", prompt=combined_input, max_tokens=150).choices[0].text.strip()
        if self.code_block_start in response and self.code_block_end in response:
            code_output = self.execute_code(response)
            if len(code_output) > 1000:
                code_output = code_output[:200] + code_output[-800:]
            response += "\n\nCode Execution Output:\n" + code_output
        return response

    def execute_code(self, text_with_code):
        try:
            code_start_index = text_with_code.find(self.code_block_start) + len(self.code_block_start)
            code_end_index = text_with_code.find(self.code_block_end, code_start_index)
            code_to_execute = text_with_code[code_start_index:code_end_index].strip()
            result = subprocess.run(shlex.split(code_to_execute), capture_output=True, text=True, shell=True, timeout=30)
            return result.stdout or result.stderr
        except Exception as e:
            return f"Error in executing code: {e}"

    def evolve_prompt(self, input_text):
        response = self.generate_response(input_text)
        feedback = self.request_evaluations(response, input_text)
        if feedback.count("Poor") > len(feedback) / 2:
            evolve_prompt_query = f"How should the prompt evolve based on this input and feedback? Input: {input_text}, Feedback: {feedback}"
            new_prompt = openai.Completion.create(engine="gpt-4", prompt=evolve_prompt_query, max_tokens=50)
            self.prompt = new_prompt.choices[0].text.strip() or self.prompt

    def respond(self, input_text):
        if self.depth < self.max_depth:
            response = self.generate_response(input_text)
            self.evolve_prompt(input_text)
            return response
        else:
            return self.evaluate_at_max_depth(input_text)

    def request_evaluations(self, response, input_text):
        feedback = []
        for agent in self.all_agents:
            if agent != self:
                feedback.append(agent.evaluate(response, input_text, self.depth + 1))
        return feedback

    def evaluate_at_max_depth(self, input_text):
        evaluation_query = f"Evaluate this input for quality and relevance: '{input_text}'"
        evaluation = openai.Completion.create(engine="gpt-4", prompt=evaluation_query, max_tokens=50)
        return evaluation.choices[0].text.strip()

    def evaluate(self, response, input_text, depth):
        if depth < self.max_depth:
            for agent in self.all_agents:
                if agent != self:
                    return agent.evaluate(response, input_text, depth + 1)
        else:
            return self.evaluate_at_max_depth(input_text)
