import openai
import subprocess
import shlex
import logging
import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MicroAgent:
    currentDatetime = datetime.datetime.now()
    static_pre_prompt = (
        "Current Time: " + currentDatetime.strftime("%H:%M:%S") + ". "
        "You are an autonomous agent capable of processing various tasks, "
        "including executing simple Python code within code blocks with an internet connection (i.e. to get real-time information) and deciding when to use other agents (to break down tasks). "
        "Agents are invoked using: 'Use Agent[Purpose of the agent as sentence]'."
        "NEVER call an agent with the same purpose as yourself, if you call another agent you must break the task down. "
        "Write code to solve the task."
        "A purpose MUST be reuseable and generic. Use names as you would call microservices."
    )

    def __init__(self, initial_prompt, purpose, manager, api_key, depth=0, max_depth=5):
        self.dynamic_prompt = initial_prompt
        self.purpose = purpose
        self.manager = manager
        self.api_key = api_key
        self.depth = depth
        self.max_depth = max_depth
        self.usage_count = 0
        openai.api_key = api_key
        self.code_block_start = "```python"
        self.code_block_end = "```"

    def generate_runtime_context(self):
        available_agents_arr = [agent for agent in self.manager.agents if agent.purpose != "General" and agent.purpose != self.purpose]
        available_agents = ', '.join([agent.purpose for agent in available_agents_arr])
        logging.info(f"Your Purpose: {self.purpose}. Queue Depth: {self.depth}. Available agents: {available_agents}.")

        return f"Your Purpose: {self.purpose}. Queue Depth: {self.depth}. Available agents: {available_agents}."

    def generate_response(self, input_text):
        runtime_context = self.generate_runtime_context()
        system_prompt = MicroAgent.static_pre_prompt + runtime_context + self.dynamic_prompt
        logging.info(f"System Prompt: {system_prompt}")
        logging.info(f"Input Text: {input_text}")
        logging.info(f"Current Prompt: {self.dynamic_prompt}")
        logging.info(f"Current Depth: {self.depth}")
        conversation_accumulator = ""
        thought_number = 1
        action_number = 1

        for iteration in range(self.max_depth):
            react_prompt = f"Question: {input_text}\n{conversation_accumulator}\nThought {thought_number}: [Decompose the task. Identify if another agent or Python code execution is needed. Write 'Query Solved' once the task is completed.]\nAction {action_number}: [Specify action based on the thought, e.g., 'Use Agent[Purpose of the agent as sentence]' for delegation or '```python\n# Python code here\n```' for execution]"

            response = openai.ChatCompletion.create(
                model="gpt-4-1106-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": react_prompt}
                ]
            ).choices[0].message['content']

            logging.info(f"Response: {response}")
            conversation_accumulator += f"\nOutput: {thought_number}: {response}"

            if "Use Agent[" in response:
                agent_name = response.split('Use Agent[')[1].split(']')[0]
                logging.info(f"Delegating task to Agent: {agent_name}")
                delegated_agent = self.manager.get_or_create_agent(agent_name)
                delegated_response = delegated_agent.respond(agent_name)
                conversation_accumulator += f"\nThought {thought_number}: Delegated task to Agent {agent_name}\nAction {action_number}: {delegated_response}"
                logging.info(f"Conversation: {conversation_accumulator}")
                logging.info(f"Delegated task to Agent {agent_name}")

            elif "```python" in response:
                code_to_execute = response.split("```python")[1].split("```")[0]
                try:
                    exec_globals = {}
                    exec(code_to_execute, exec_globals)
                    exec_response = "Executed Python Code Successfully. Output: " + str(exec_globals)
                except Exception as e:
                    exec_response = f"Error in executing code: {e}"

                if len(exec_response) > 1000:
                    exec_response = exec_response[:200] + "..." + exec_response[-1000:]
                conversation_accumulator += f"\nThought {thought_number}: Executed Python code\nAction {action_number}: {exec_response}"
                logging.info(f"Executed Python code")

            thought_number += 1
            action_number += 1

            if "Query Solved" in response:
                break

        final_answer = "Final Response: " + conversation_accumulator
        logging.info(f"Final Response: {final_answer}")
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

    def evolve_prompt(self, input_text, output):
        feedback = self.evaluate_agent(input_text, self.dynamic_prompt, output)
        runtime_context = self.generate_runtime_context()
        if "poor" in feedback.lower():
            evolve_prompt_query = f"How should the GPT-4 prompt evolve based on this input and feedback? If you don't know something, write sample code in the prompt to solve it. Break down complex tasks by calling other agents if required. Please include python code that should be used to solve a certain task as per purpose or list other agents that should be called. A purpose is always a sentence long. ONLY RESPONSE WITH THE NEW PROMPT NO OTHER TEXT! Current Prompt: {input_text}, User Feedback: {feedback}"
            logging.info(f"Evolve prompt query: {evolve_prompt_query}")
            new_prompt = openai.ChatCompletion.create(
                model="gpt-4-1106-preview",
                messages=[{"role": "system", "content": evolve_prompt_query + runtime_context}]
            ).choices[0].message['content'].strip() or self.dynamic_prompt
            logging.info(f"New prompt: {new_prompt}")
            self.dynamic_prompt = new_prompt

    def respond(self, input_text):
        response = self.generate_response(input_text)
        self.evolve_prompt(input_text, response)
        return response
    
    def evaluate_agent(self, input_text, prompt, output):
        evaluation_query = f"Evaluate the generated LLM Output: '{input_text}' with the current prompt '{prompt}' for quality and relevance (Possible Answers: Poor, Good), LLM output with current prompt: '{output}'"
        logging.info(f"Evaluation query: {evaluation_query}")
        logging.info(f"Current prompt: {prompt}")
        logging.info(f"Current output: {output}")
        evaluation = openai.ChatCompletion.create(
            model="gpt-4-1106-preview",
            messages=[{"role": "system", "content": evaluation_query}]
        ).choices[0].message['content']
        logging.info(f"Evaluation result: {evaluation}")
        return evaluation
