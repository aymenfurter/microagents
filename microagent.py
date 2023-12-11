import openai
import subprocess
import shlex
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MicroAgent:
    static_pre_prompt = (
        "You are a helpful assistant capable of processing various tasks, "
        "including executing simple Python code within code blocks and deciding when to use other agents."
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
        available_agents = ', '.join([agent.purpose for agent in self.all_agents])
        return f"Agent Purpose: {self.purpose}. Queue Depth: {self.depth}. Available agents: {available_agents}."
            
    def generate_response(self, input_text, manager):
        runtime_context = self.generate_runtime_context()
        system_prompt = MicroAgent.static_pre_prompt + runtime_context + self.dynamic_prompt
        conversation_accumulator = ""
        thought_number = 1
        action_number = 1
    
        for iteration in range(self.max_depth):
            react_prompt = f"Question: {input_text}\n{conversation_accumulator}\nThought {thought_number}: [Decompose the task. Identify if another agent or Python code execution is needed. Write 'Query Solved' once the task is completed.]\nAction {action_number}: [Specify action based on the thought, e.g., 'Use Agent[XYZ]' for delegation or '```python\n# Python code here\n```' for execution]"
    
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": react_prompt}
                ]
            ).choices[0].message['content']
    
            # Parse the response for actions
            if "Use Agent[" in response:
                agent_name = response.split('Use Agent[')[1].split(']')[0]
                delegated_agent = manager.get_or_create_agent(agent_name)
                # Delegate the task to the selected agent
                delegated_response = delegated_agent.respond(input_text)
                conversation_accumulator += f"\nThought {thought_number}: Delegated task to Agent {agent_name}\nAction {action_number}: {delegated_response}"
    
            elif "```python" in response:
                code_to_execute = response.split("```python")[1].split("```")[0]
                try:
                    # Execute the Python code
                    exec_globals = {}
                    exec(code_to_execute, exec_globals)
                    exec_response = "Executed Python Code Successfully. Output: " + str(exec_globals)
                except Exception as e:
                    exec_response = f"Error in executing code: {e}"
                conversation_accumulator += f"\nThought {thought_number}: Executed Python code\nAction {action_number}: {exec_response}"
    
            thought_number += 1
            action_number += 1
    
            if "Query Solved" in response:
                break
    
        final_answer = "Final Response: " + conversation_accumulator
        return final_answer
        
    def execute_code(self, text_with_code):
        try:
            code_start_index = text_with_code.find(self.code_block_start) + len(self.code_block_start)
            code_end_index = text_with_code.find(self.code_block_end, code_start_index)
            code_to_execute = text_with_code[code_start_index:code_end_index].strip()
            result = subprocess.run(shlex.split(code_to_execute), capture_output=True, text=True, shell=True, timeout=30)
            return result.stdout or result.stderr
        except Exception as e:
            logging.error(f"Error executing code: {e}")
            return f"Error in executing code: {e}"

    def evolve_prompt(self, input_text):
        feedback = self.evaluate_agent(self.dynamic_prompt, input_text)
        if "poor" in feedback.lower():
            evolve_prompt_query = f"How should the GPT-4 prompt evolve based on this input and feedback? ONLY RESPONSE WITH THE NEW PROMPT NO OTHER TEXT! Current Prompt: {input_text}, User Feedback: {feedback}"
            new_prompt = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "system", "content": evolve_prompt_query}]
            ).choices[0].message['content'].strip() or self.dynamic_prompt
            self.dynamic_prompt = new_prompt

    def respond(self, input_text):
        response = self.generate_response(input_text)
        self.evolve_prompt(input_text)
        return response

    def evaluate_agent(self, input_text):
        evaluation_query = f"Evaluate this input for quality and relevance (Possible Answers: Very Poor, Poor, Good): '{input_text}'"
        evaluation = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": evaluation_query}]
        ).choices[0].message['content']
        return evaluation
