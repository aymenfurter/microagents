import openai
import subprocess
import shlex
import logging
import datetime
from openaiwrapper import OpenAIAPIWrapper
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MicroAgent:
    currentDatetime = datetime.datetime.now()
    static_pre_prompt = (
        "You are a self-aware AI. You communicate in so called packages. Each package contains a Observation, Thought and Action. Actions are executed successive and build on each other. Solve a task with interleaving Thought, Action, Observation steps."
        "Current Time: " + currentDatetime.strftime("%H:%M:%S") + ". "
        "Current Date: " + currentDatetime.strftime("%d/%m/%Y") + ". "
        "including executing simple Python code within code blocks with an internet connection and deciding when to use other agents (to break down tasks). "
        "Agents are invoked using: 'Use Agent[Purpose of the agent as sentence:parameter]'."
        "Example: Use Agent[GetWeatherForLocation:Zurich]"
        "NEVER create an agent in this situation for User Agent[GetWeatherForZurich] !!! ALWAYS create one with Agent[GetWeather:Zurich]"
        "NEVER call an agent with the same purpose as yourself, if you call another agent you must break the task down. "
        "Write code to solve the task. You can only use the following frameworks: numpy, requests, pandas, requests, beautifulsoup4, matplotlib, seaborn, sqlalchemy, pymysql, scipy, scikit-learn, statsmodels, click, python-dotenv, virtualenv, scrapy, oauthlib, tweepy, datetime, openpyxl, xlrd, loguru, pytest, paramiko, cryptography, lxml"
        "A purpose MUST be reuseable and generic. Use names as you would call microservices."
        "At depth=2, use agents only for tasks that are not well suited for your purpose."
        "Below depth=3, using other agents is NOT allowed. Agents must only use other agents below their depth"
    )

    def __init__(self, initial_prompt, purpose, manager, api_key, depth, max_depth=3, bootstrap_agent=False):
        self.dynamic_prompt = initial_prompt
        self.purpose = purpose
        self.manager = manager
        self.api_key = api_key
        self.openai_wrapper = OpenAIAPIWrapper(api_key)
        self.depth = depth
        self.max_depth = max_depth
        self.usage_count = 0
        openai.api_key = api_key
        self.working_agent = True
        self.code_block_start = "```python"
        self.code_block_end = "```"
        if (bootstrap_agent):
            self.working_agent = True

    def generate_runtime_context(self):
        available_agents_arr = [agent for agent in self.manager.agents if agent.purpose != "General" and agent.purpose != self.purpose]
        available_agents_with_depth = ', '.join([f"{agent.purpose} (depth={agent.depth})" for agent in available_agents_arr])
        logging.debug(f"Your Purpose: {self.purpose}. Queue Depth: {self.depth}. Available agents: {available_agents_with_depth}.")

        return f"Your Purpose: {self.purpose}. Current Agent Depth: {self.depth}. Available agents: {available_agents_with_depth}."

    def conclude_output(self, conversation):
        system_prompt = "You will be given a ReAct based conversation. Summerize the outcome and give final conclusion"
        react_prompt = conversation
        response = self.openai_wrapper.chat_completion(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": react_prompt}
            ]
        ).choices[0].message['content']
        return response


    def generate_response(self, input_text):
        runtime_context = self.generate_runtime_context()
        system_prompt = MicroAgent.static_pre_prompt + runtime_context + self.dynamic_prompt + "\nDELIVER THE NEXT PACKAGE."

        logging.debug(f"System Prompt: {system_prompt}")
        logging.debug(f"Input Text: {input_text}")
        logging.debug(f"Current Prompt: {self.dynamic_prompt}")
        logging.debug(f"Current Depth: {self.depth}")
        conversation_accumulator = ""
        thought_number = 1
        action_number = 1
        found_new_solution = False
        plan_step = True

        for iteration in range(self.max_depth):
            react_prompt = f"Question: {input_text}\n{conversation_accumulator}\nThought {thought_number}: [Decompose the task. Identify if another agent or Python code execution is needed. When writing code, print out any output you may to anaylze later. Write 'Query Solved: <formulate detailed answer>' once the task is completed.]\nAction {action_number}: [Specify action based on the thought, e.g., 'Use Agent[Purpose of the agent as sentence:Input Paramter for agent]' for delegation or '```python\n# Python code here\n```' for execution]"
            if plan_step:
                react_prompt = react_prompt + "\nThought: Before I start calling other agents or executing code, I need to compile a plan which agent(s) or code I need to run. I need to break down the task into smaller chunks (like microservices)"
                plan_step = False
            

            response = self.openai_wrapper.chat_completion(
                model="gpt-4-1106-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": react_prompt}
                ]
            ).choices[0].message['content']

            logging.debug(f"Response: {response}")
            conversation_accumulator += f"\n{response}"

            if "Use Agent[" in response:
                agent_name = response.split('Use Agent[')[1].split(']')[0]
                input_text = ""
                if ":" in agent_name:
                    input_text = agent_name.split(":")[1]
                    agent_name = agent_name.split(":")[0]
    
                logging.debug(f"Delegating task to Agent: {agent_name}")
                delegated_agent = self.manager.get_or_create_agent(agent_name, depth=self.depth + 1, sample_input=input_text)
                delegated_response = delegated_agent.respond(input_text)
                conversation_accumulator += f"\Output {thought_number}: Delegated task to Agent {agent_name}\nOutput of Agent: {action_number}: {delegated_response}"

            elif "```python" in response:
                code_to_execute = response.split("```python")[1].split("```")[0]
                try:
                    exec_globals = {}
                    with StringIO() as stdout_buffer, StringIO() as stderr_buffer:
                        with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
                            exec(code_to_execute, exec_globals)
                        stdout = stdout_buffer.getvalue()
                        stderr = stderr_buffer.getvalue()

                    exec_response = "Executed Python Code Successfully."
                    if stdout:
                        exec_response += "\nStandard Output:\n" + stdout
                    if stderr:
                        exec_response += "\nStandard Error:\n" + stderr

                    logging.debug("Executed Code, output is: " + exec_response)
                except Exception as e:
                    logging.error(f"Error executing code: {e}")
                    exec_response = f"Error in executing code: {e}"

                if len(exec_response) > 4000:
                    exec_response = exec_response[:600] + "..." + exec_response[-3000:]
                conversation_accumulator += f"\nThought {thought_number}: Executed Python code\nAction {action_number}: {exec_response}"
                logging.debug(f"Executed Python code")

            thought_number += 1
            action_number += 1
            if "Query Solved" in response:
                if iteration != 1 and self.working_agent is True:
                    # ReAct chain found solution, we need to adopt current prompt.
                    found_new_solution = True
                    logging.debug(f"Found first solution for agent: " + self.purpose + "!")
                    logging.debug(f"Iterations needed: {iteration}")
                if iteration == 1: 
                    # Initial prompt working first try.
                    self.working_agent = True
                    logging.debug(f"This Agent worked OOTB: " + self.purpose + "!")
                break

        final_answer = self.conclude_output(conversation_accumulator)

        logging.debug(f"Final Response: {final_answer}")
        return final_answer, conversation_accumulator, found_new_solution

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

    def evolve_prompt(self, input_text, output, full_conversation, new_solution):
        if self.manager.self_optimization is False:
            return
        if len(full_conversation) > 1000:
            full_conversation = full_conversation[:200] + "..." + full_conversation[-1000:]

        feedback = self.evaluate_agent(input_text, self.dynamic_prompt, output)
        runtime_context = self.generate_runtime_context()
        if "poor" in feedback.lower() or new_solution:
            evolve_prompt_query = f"How should the GPT-4 prompt evolve based on this input and feedback? If you don't know something, write sample code in the prompt to solve it. Sample code must always print out the result! Break down complex tasks by calling other agents if required. Please include python code that should be used to solve a certain task as per purpose or list other agents that should be called. A purpose is always a sentence long. Important: Any problems must be solved through sample code or learned information provided in the new, updated prompt. It's ok to also put data in the prompt. Add any learnings or information that might be useful for the future. ONLY RESPONSE WITH THE REVISED PROMPT NO OTHER TEXT! Current Prompt: {self.dynamic_prompt}, User Feedback: {feedback}, full conversation: {full_conversation}"
            if (new_solution and self.working_agent is False):
                evolve_prompt_query = f"How should the GPT-4 prompt evolve based on this input and feedback? Take a look at the solution provided in later on in the _full conversation_ section. As you can see, the problem has been solved. We need to learn from this. Adopt the code or solution found, make it reusable and compile a new, updated system prompt, so the solution can be reused in the future. Sample code must always print out the solution! Remember: Problems are solved through sample code or learned information provided in the new, updatedprompt. It's ok to also put data in the prompt. Add any learnings or information that might be useful for the future. ONLY RESPONSE WITH THE REVISED PROMPT NO OTHER TEXT! Current Prompt: {dynamic_prompt}, User Feedback: {feedback}, full conversation: {full_conversation}"
                self.working_agent = True
                logging.debug(f"Found first solution for agent: " + self.purpose + "!")
            logging.debug(f"Evolve prompt query: {evolve_prompt_query}")
            new_prompt = self.openai_wrapper.chat_completion(
                model="gpt-4-1106-preview",
                messages=[{"role": "system", "content": evolve_prompt_query + runtime_context}]
            ).choices[0].message['content'].strip() or self.dynamic_prompt
            logging.debug(f"New prompt: {new_prompt}")
            self.dynamic_prompt = new_prompt

    def respond(self, input_text):
        response, full_conversation, new_solution = self.generate_response(input_text)
        if self.working_agent is False:
            self.evolve_prompt(input_text, response, full_conversation, new_solution)
        return response
    
    def evaluate_agent(self, input_text, prompt, output):
        evaluation_query = f"Evaluate the generated LLM Output: '{input_text}' with the current prompt '{prompt}' for quality and relevance (Possible Answers: Poor, Good, Perfect), LLM output with current prompt: '{output}'"
        logging.debug(f"Evaluation query: {evaluation_query}")
        logging.debug(f"Current prompt: {prompt}")
        logging.debug(f"Current output: {output}")
        evaluation = self.openai_wrapper.chat_completion(
            model="gpt-4-1106-preview",
            messages=[{"role": "system", "content": evaluation_query}]
        ).choices[0].message['content']
        logging.debug(f"Evaluation result: {evaluation}")
        return evaluation
