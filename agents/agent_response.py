import logging
from integrations.openaiwrapper import OpenAIAPIWrapper
from agents.parallel_agent_executor import ParallelAgentExecutor
from prompt_management.prompts import (
    REACT_STEP_POST, REACT_STEP_PROMPT, REACT_SYSTEM_PROMPT, REACT_PLAN_PROMPT, STATIC_PRE_PROMPT, STATIC_PRE_PROMPT_PRIME, REACT_STEP_PROMPT_PRIME, REACT_STEP_POST_PRIME
)

logger = logging.getLogger()

class AgentResponse:
    def __init__(self, openai_wrapper, manager, code_execution, agent, creator, depth):
        self.openai_wrapper = openai_wrapper
        self.manager = manager
        self.code_execution = code_execution
        self.agent = agent
        self.creator = creator
        self.depth = depth

    def number_to_emoji(self, number):
        """Converts a number to an emoji."""
        response = ""
        for digit in str(number):
            response += chr(0x1f1e6 + int(digit))
        return response

    def generate_response(self, input_text, dynamic_prompt, max_depth):
        runtime_context = self._generate_runtime_context(dynamic_prompt)
        system_prompt = self._compose_system_prompt(runtime_context, dynamic_prompt)
        conversation_accumulator = ""
        thought_number = 0
        action_number = 0
        found_new_solution = False

        for _ in range(max_depth):
            react_prompt = self._build_react_prompt(input_text, conversation_accumulator, thought_number, action_number)
            self.agent.update_status(f"🤔 (Iteration {thought_number})")
            response = self._generate_chat_response(system_prompt, react_prompt)
            conversation_accumulator, thought_number, action_number = self._process_response(
                response, conversation_accumulator, thought_number, action_number, input_text
            )

            if "Query Solved" in response:
                found_new_solution = True
                break

        return self._conclude_output(conversation_accumulator, input_text), conversation_accumulator, found_new_solution, thought_number

    def _compose_system_prompt(self, runtime_context, dynamic_prompt):
        pre_prompt = STATIC_PRE_PROMPT_PRIME if self.agent.is_prime else STATIC_PRE_PROMPT
        return pre_prompt + runtime_context + dynamic_prompt + "\nDELIVER THE NEXT PACKAGE."

    def _generate_runtime_context(self, dynamic_prompt):
        available_agents = self.manager.get_available_agents_for_agent(self.agent)
        available_agents_info = ', '.join([f"{agent.purpose} (depth={agent.depth})" for agent in available_agents])
        return f"Your Purpose: {dynamic_prompt}. Available agents (Feel free to invent new ones if required!): {available_agents_info}."


    def _build_react_prompt(self, input_text, conversation_accumulator, thought_number, action_number):
        thought_prompt = REACT_STEP_PROMPT_PRIME if self.agent.is_prime else REACT_STEP_PROMPT
        action_prompt = REACT_STEP_POST_PRIME if self.agent.is_prime else REACT_STEP_POST
        return (
            f"Question: {input_text}\n"
            f"{conversation_accumulator}\n"
            f"Thought {thought_number}: {thought_prompt}\n"
            f"Action {action_number}: {action_prompt}"
        )

    def _generate_chat_response(self, system_prompt, react_prompt):
        return self.openai_wrapper.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": react_prompt}
            ]
        )

    def _process_response(self, response, conversation_accumulator, thought_number, action_number, input_text):
        updated_accumulator = self._append_response_to_accumulator(conversation_accumulator, response)
        thought_number += 1
        action_number += 1

        if self._is_python_code(response):
            exec_response = self._execute_python_code(response)
            updated_accumulator = self._append_execution_response(updated_accumulator, exec_response, thought_number)

        if self._is_agent_invocation(response):
            agent_name, updated_input_text = self._parse_agent_info(response)
            delegated_response, updated_accumulator = self._handle_agent_delegation(agent_name, updated_input_text, updated_accumulator, thought_number, action_number)
            action_number += 1

        return updated_accumulator, thought_number, action_number

    def _append_response_to_accumulator(self, accumulator, response):
        return accumulator + f"\n{response}"

    def _is_python_code(self, response):
        return "```python" in response

    def _execute_python_code(self, response):
        self.agent.update_status('👩‍💻 Coding..')
        self.agent.number_of_code_executions += 1
        return self.code_execution.execute_external_code(response)

    def _append_execution_response(self, accumulator, exec_response, thought_number):
        return accumulator + f"\nObservation: Executed Python code\nOutput: {exec_response}"

    def _is_agent_invocation(self, response):
        return "Use Agent[" in response

    def _handle_agent_delegation(self, agent_name, input_text, accumulator, thought_number, action_number):
        self.agent.update_active_agents(self.agent.purpose, agent_name)
        self.agent.update_status('⏳ ' + agent_name + '..')
        if agent_name == self.agent.purpose:
            accumulator += f"\nOutput {thought_number}: Unable to use Agent {agent_name}\nIt is not possible to call yourself!"
            return "", accumulator
        else:
            parallel_executor = ParallelAgentExecutor(self.manager)
            delegated_response = parallel_executor.create_and_run_agents(agent_name, self.depth + 1, input_text, self.agent)

            accumulator += f"\nOutput {thought_number}: Delegated task to Agent {agent_name}\nOutput of Agent {action_number}: {delegated_response}"
            return delegated_response, accumulator

    def _parse_agent_info(self, response):
        agent_info = response.split('Use Agent[')[1].split(']')[0]
        split_info = agent_info.split(":", 1)
        agent_name = split_info[0].strip()
        input_text = split_info[1].strip() if len(split_info) > 1 else ""
        return agent_name, input_text

    def _conclude_output(self, conversation, input_text):
        
        react_prompt = conversation
        react_prompt += f"\nYour designation is: {self.agent.purpose}\n"
        react_prompt += f"\nThe original question / task was: {input_text}\n"
        react_prompt += f"\nUse beautiful markdown formatting in your output, e.g. include images using ![Drag Racing](https://example.com/Dragster.jpg)\n"
        self.agent.update_status('🧐 Reviewing..')
        return self.openai_wrapper.chat_completion(
            messages=[
                {"role": "system", "content": REACT_SYSTEM_PROMPT},
                {"role": "user", "content": react_prompt}
            ]
        )