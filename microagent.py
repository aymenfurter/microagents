import openai
import subprocess
import shlex
import logging
import datetime
from openaiwrapper import OpenAIAPIWrapper

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MicroAgent:
    currentDatetime = datetime.datetime.now()
    static_pre_prompt = (
        "Current Time: " + currentDatetime.strftime("%H:%M:%S") + ". "
        "Current Date: " + currentDatetime.strftime("%d/%m/%Y") + ". "
        "You are an autonomous agent capable of processing various tasks, "
        "including executing simple Python code within code blocks with an internet connection and deciding when to use other agents (to break down tasks). "
        "Agents are invoked using: 'Use Agent[Purpose of the agent as sentence:parameter]'."
        "Example: Use Agent[GetWeatherForLocation:Zurich]"
        "NEVER call an agent with the same purpose as yourself, if you call another agent you must break the task down. "
        "Write code to solve the task. You can only use the following frameworks: numpy, requests, pandas, requests, beautifulsoup4, matplotlib, seaborn, sqlalchemy, pymysql, scipy, scikit-learn, statsmodels, click, python-dotenv, virtualenv, scrapy, oauthlib, tweepy, datetime, openpyxl, xlrd, loguru, pytest, paramiko, cryptography, lxml"
        "A purpose MUST be reuseable and generic. Use names as you would call microservices."
        "At depth=2, use agents only for tasks that are not well suited for your purpose."
        "Below depth=3, using other agents is NOT allowed. Agents must only use other agents below their depth"
    )

    def __init__(self, initial_prompt, purpose, manager, api_key, depth, max_depth=5):
        self.dynamic_prompt = initial_prompt
        self.purpose = purpose
        self.manager = manager
        self.api_key = api_key
        self.openai_wrapper = OpenAIAPIWrapper(api_key)
        self.depth = depth
        self.max_depth = max_depth
        self.usage_count = 0
        openai.api_key = api_key
        self.code_block_start = "```python"
        self.code_block_end = "```"

    def generate_runtime_context(self):
        available_agents_arr = [agent for agent in self.manager.agents if agent.purpose != "General" and agent.purpose != self.purpose]
        available_agents_with_depth = ', '.join([f"{agent.purpose} (depth={agent.depth})" for agent in available_agents_arr])
        logging.info(f"Your Purpose: {self.purpose}. Queue Depth: {self.depth}. Available agents: {available_agents_with_depth}.")

        return f"Your Purpose: {self.purpose}. Current Agent Depth: {self.depth}. Available agents: {available_agents_with_depth}."

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
            react_prompt = f"Question: {input_text}\n{conversation_accumulator}\nThought {thought_number}: [Decompose the task. Identify if another agent or Python code execution is needed. Write 'Query Solved: <formulate detailed answer>' once the task is completed.]\nAction {action_number}: [Specify action based on the thought, e.g., 'Use Agent[Purpose of the agent as sentence:Input Paramter for agent]' for delegation or '```python\n# Python code here\n```' for execution]"

            response = self.openai_wrapper.chat_completion(
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
                input_text = ""
                if ":" in agent_name:
                    input_text = agent_name.split(":")[1]
                    agent_name = agent_name.split(":")[0]
    
                logging.info(f"Delegating task to Agent: {agent_name}")
                delegated_agent = self.manager.get_or_create_agent(agent_name, depth=self.depth + 1, sample_input=input_text)
                delegated_response = delegated_agent.respond(input_text)
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
        return final_answer, conversation_accumulator

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

    def evolve_prompt(self, input_text, output, full_conversation):
        if len(full_conversation) > 1000:
            full_conversation = full_conversation[:200] + "..." + full_conversation[-1000:]

        feedback = self.evaluate_agent(input_text, self.dynamic_prompt, output)
        runtime_context = self.generate_runtime_context()
        if "poor" in feedback.lower():
            evolve_prompt_query = f"How should the GPT-4 prompt evolve based on this input and feedback? If you don't know something, write sample code in the prompt to solve it. Break down complex tasks by calling other agents if required. Please include python code that should be used to solve a certain task as per purpose or list other agents that should be called. A purpose is always a sentence long. Important: Any problems must be solved through sample code or learned information provided in the prompt. Add any learnings or information that might be useful for the future. ONLY RESPONSE WITH THE REVISED PROMPT NO OTHER TEXT! Current Prompt: {input_text}, User Feedback: {feedback}, full conversation: {full_conversation}"
            logging.info(f"Evolve prompt query: {evolve_prompt_query}")
            new_prompt = self.openai_wrapper.chat_completion(
                model="gpt-4-1106-preview",
                messages=[{"role": "system", "content": evolve_prompt_query + runtime_context}]
            ).choices[0].message['content'].strip() or self.dynamic_prompt
            logging.info(f"New prompt: {new_prompt}")
            self.dynamic_prompt = new_prompt

    def respond(self, input_text):
        response, full_conversation = self.generate_response(input_text)
        self.evolve_prompt(input_text, response, full_conversation)
        return response
    
    def evaluate_agent(self, input_text, prompt, output):
        evaluation_query = f"Evaluate the generated LLM Output: '{input_text}' with the current prompt '{prompt}' for quality and relevance (Possible Answers: Poor, Good), LLM output with current prompt: '{output}'"
        logging.info(f"Evaluation query: {evaluation_query}")
        logging.info(f"Current prompt: {prompt}")
        logging.info(f"Current output: {output}")
        evaluation = self.openai_wrapper.chat_completion(
            model="gpt-4-1106-preview",
            messages=[{"role": "system", "content": evaluation_query}]
        ).choices[0].message['content']
        logging.info(f"Evaluation result: {evaluation}")
        return evaluation
