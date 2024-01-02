import logging
from integrations.openaiwrapper import OpenAIAPIWrapper
from integrations.manager import LLM_Manager
from prompt_management.prompts import (
    REACT_STEP_POST, REACT_STEP_PROMPT, REACT_SYSTEM_PROMPT, REACT_PLAN_PROMPT, STATIC_PRE_PROMPT, STATIC_PRE_PROMPT_PRIME, REACT_STEP_PROMPT_PRIME, REACT_STEP_POST_PRIME
)

logger = logging.getLogger()

class AgentResponse:
    def __init__(self, llm_manager, manager, code_execution, agent, creator, depth):
        self.llm_manager = llm_manager
        self.manager = manager
        self.code_execution = code_execution
        self.agent = agent
        self.creator = creator
        self.depth = depth

    def generate_response(self, input_text, dynamic_prompt, max_depth):
        runtime_context = self._generate_runtime_context(dynamic_prompt)
        system_prompt = self._compose_system_prompt(runtime_context, dynamic_prompt)
        conversation_accumulator = ""
        thought_number = 0
        action_number = 0
        found_new_solution = False

        for _ in range(max_depth):
            react_prompt = self._build_react_prompt(input_text, conversation_accumulator, thought_number, action_number)
            self.agent.update_status(f"Thinking .. (Iteration #{thought_number})")
            response = self._generate_chat_response(system_prompt, react_prompt)
            conversation_accumulator, thought_number, action_number = self._process_response(
                response, conversation_accumulator, thought_number, action_number, input_text
            )

            if "Query Solved" in response:
                found_new_solution = True
                break

        return self._conclude_output(conversation_accumulator), conversation_accumulator, found_new_solution, thought_number

    def _compose_system_prompt(self, runtime_context, dynamic_prompt):
        pre_prompt = STATIC_PRE_PROMPT_PRIME if self.agent.is_prime else STATIC_PRE_PROMPT
        return pre_prompt + runtime_context + dynamic_prompt + "\nDELIVER THE NEXT PACKAGE."

    def _generate_runtime_context(self, dynamic_prompt):
        available_agents = [agent for agent in self.manager.agents if agent.purpose != "Bootstrap Agent"]
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
        return self.llm_manager.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": react_prompt}
            ]
        )

    def _process_response(self, response, conversation_accumulator, thought_number, action_number, input_text):
        conversation_accumulator += f"\n{response}"
        thought_number += 1
        action_number += 1

        if "```python" in response:
            self.agent.update_status('Executing Python code')
            self.agent.number_of_code_executions += 1
            exec_response = self.code_execution.execute_external_code(response)
            conversation_accumulator += f"\nObservation: Executed Python code\nOutput: {exec_response}"

        if "Use Agent[" in response:
            agent_name, input_text = self._parse_agent_info(response)
            self.agent.update_active_agents(self.agent.purpose, agent_name)
            self.agent.update_status('Waiting for Agent')
            delegated_agent = self.creator.get_or_create_agent(agent_name, depth=self.depth + 1, sample_input=input_text)
            delegated_response = delegated_agent.respond(input_text)
            conversation_accumulator += f"\nOutput {thought_number}: Delegated task to Agent {agent_name}\nOutput of Agent: {action_number}: {delegated_response}"

        return conversation_accumulator, thought_number, action_number

    def _parse_agent_info(self, response):
        agent_info = response.split('Use Agent[')[1].split(']')[0]
        agent_name, input_text = (agent_info.split(":") + [""])[:2]
        return agent_name.strip(), input_text.strip()

    def _conclude_output(self, conversation):
        react_prompt = conversation

        self.agent.update_status('Reviewing output')
        return self.llm_manager.chat_completion(
            messages=[
                {"role": "system", "content": REACT_SYSTEM_PROMPT},
                {"role": "user", "content": react_prompt}
            ]
        )
