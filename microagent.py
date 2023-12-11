import openai
import subprocess
import shlex

class MicroAgent:
    static_pre_prompt = (
        "You are a helpful assistant capable of processing various tasks, "
        "including executing simple Python code within code blocks. "
    )

    def __init__(self, initial_prompt, purpose, all_agents, api_key, depth=0, max_depth=5):
        self.dynamic_prompt = initial_prompt
        self.purpose = purpose
        self.all_agents = all_agents
        self.api_key = api_key
        self.depth = depth
        self.max_depth = max_depth
        self.usage_count = 0
        openai.api_key = api_key
        self.code_block_start = "```python"
        self.code_block_end = "```"

    def generate_runtime_context(self):
        return f"Agent Purpose: {self.purpose}. Queue Depth: {self.depth}. "

    def generate_response(self, input_text):
        runtime_context = self.generate_runtime_context()
        system_prompt = MicroAgent.static_pre_prompt + runtime_context + self.dynamic_prompt
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": input_text}
        ]
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages
        ).choices[0].message['content']

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
            new_prompt = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "system", "content": evolve_prompt_query}]
            ).choices[0].message['content'].strip() or self.dynamic_prompt
            self.dynamic_prompt = new_prompt

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
        evaluation = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": evaluation_query}]
        ).choices[0].message['content']
        return evaluation

    def evaluate(self, response, input_text, depth):
        if depth < self.max_depth:
            for agent in self.all_agents:
                if agent != self:
                    return agent.evaluate(response, input_text, depth + 1)
        else:
            return self.evaluate_at_max_depth(input_text)

# Example usage:
# agents = [MicroAgent("I specialize in arithmetic calculations.", "Math", agents, your_api_key), ...]
# response = agents[0].respond("Calculate 2 + 2.")
# print(response)
