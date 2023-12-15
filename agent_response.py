import logging
from openaiwrapper import OpenAIAPIWrapper
from prompts import REACT_STEP_POST, REACT_STEP_PROMPT, REACT_SYSTEM_PROMPT, REACT_PLAN_PROMPT, STATIC_PRE_PROMPT
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AgentResponse:
    def __init__(self, openai_wrapper, manager, code_execution, creator, depth):
        self.openai_wrapper = openai_wrapper
        self.manager = manager
        self.code_execution = code_execution
        self.creator = creator
        self.depth = depth

    def generate_response(self, input_text, dynamic_prompt, max_depth):
        runtime_context = self.generate_runtime_context(dynamic_prompt)
        system_prompt = STATIC_PRE_PROMPT + runtime_context + dynamic_prompt + "\nDELIVER THE NEXT PACKAGE."
        conversation_accumulator = ""
        thought_number = 0
        action_number = 0
        found_new_solution = False
        plan_step = True


        for iteration in range(max_depth):
            react_prompt = self.build_react_prompt(input_text, conversation_accumulator, thought_number, action_number)

            if plan_step:
                react_prompt = react_prompt + REACT_PLAN_PROMPT
                plan_step = False

            response = self.openai_wrapper.chat_completion(
                model="gpt-4-1106-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": react_prompt}
                ]
            ).choices[0].message['content']

            conversation_accumulator += f"\n{response}"
            thought_number += 1
            action_number += 1

            if "```python" in response:
                exec_response = self.code_execution.execute_external_code(response)
                print(exec_response)
                conversation_accumulator += f"\nObservation: Executed Python code\nOutput: {exec_response}"
            
            if "Use Agent[" in response:
                agent_name = response.split('Use Agent[')[1].split(']')[0]
                input_text = ""
                if ":" in agent_name:
                    input_text = agent_name.split(":")[1]
                    agent_name = agent_name.split(":")[0]
    
                delegated_agent = self.creator.get_or_create_agent(agent_name, depth=self.depth + 1, sample_input=input_text)
                delegated_response = delegated_agent.respond(input_text)
                conversation_accumulator += f"\nOutput {thought_number}: Delegated task to Agent {agent_name}\nOutput of Agent: {action_number}: {delegated_response}"

            if "Query Solved" in response:
                found_new_solution = True
                break

        return self.conclude_output(conversation_accumulator), conversation_accumulator, found_new_solution, thought_number

    def generate_runtime_context(self, dynamic_prompt):
        available_agents_arr = [agent for agent in self.manager.agents if agent.purpose != "General"]
        available_agents_with_depth = ', '.join([f"{agent.purpose} (depth={agent.depth})" for agent in available_agents_arr])
        return f"Your Purpose: {dynamic_prompt}. Available agents: {available_agents_with_depth}."

    def build_react_prompt(self, input_text, conversation_accumulator, thought_number, action_number):
        return (
            f"Question: {input_text}\n"
            f"{conversation_accumulator}\n"
            f"Thought {thought_number}: {REACT_STEP_PROMPT}\n"
            f"Action {action_number}: {REACT_STEP_POST}"
        )

    def conclude_output(self, conversation):
        react_prompt = conversation
        response = self.openai_wrapper.chat_completion(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": REACT_SYSTEM_PROMPT},
                {"role": "user", "content": react_prompt}
            ]
        ).choices[0].message['content']
        return response