import logging
from integrations.openaiwrapper import OpenAIAPIWrapper
from prompt_management.prompts import EVOLVE_PROMPT_QUERY

logger = logging.getLogger()

class PromptEvolution:
    def __init__(self, openai_wrapper: OpenAIAPIWrapper, manager):
        """Initialize PromptEvolution with OpenAI API wrapper and a manager."""
        self.openai_wrapper = openai_wrapper
        self.manager = manager

    def evolve_prompt(self, input_text: str, dynamic_prompt: str, output: str, full_conversation: str, new_solution: bool, depth: int) -> str:
        """
        Evolves the prompt based on feedback from the output and full conversation.

        Args:
            input_text: The input text for the prompt.
            dynamic_prompt: The dynamic part of the prompt.
            output: The output received from the previous interaction.
            full_conversation: The entire conversation history.
            new_solution: Boolean indicating if a new solution is provided.
            depth: The current depth of the agent.

        Returns:
            The evolved prompt.
        """
        full_conversation = self._truncate_conversation(full_conversation)
        runtime_context = self._generate_runtime_context(depth)
        evolve_prompt_query = self._build_evolve_prompt_query(dynamic_prompt, output, full_conversation, new_solution)

        try:
            new_prompt = self._get_new_prompt(evolve_prompt_query, runtime_context)
        except Exception as e:
            logger.error(f"Error evolving prompt: {e}")
            new_prompt = dynamic_prompt

        return new_prompt

    def _truncate_conversation(self, conversation: str) -> str:
        """Truncates the conversation to the last 1000 characters if it's too long."""
        if len(conversation) > 1000:
            return conversation[:200] + "..." + conversation[-1000:]
        return conversation

    def _generate_runtime_context(self, depth: int) -> str:
        """Generates runtime context for the evolve prompt query."""
        available_agents = [agent for agent in self.manager.agents if agent.purpose != "General"]
        agents_info = ', '.join([f"{agent.purpose} (depth={agent.depth})" for agent in available_agents])
        return f"Current Agent Depth: {depth}. Available agents: {agents_info}."

    def _build_evolve_prompt_query(self, dynamic_prompt: str, output: str, full_conversation: str, new_solution: bool) -> str:
        """Builds the query for evolving the prompt."""
        evolve_query = EVOLVE_PROMPT_QUERY.format(dynamic_prompt=dynamic_prompt, full_conversation=full_conversation)

        return evolve_query 

    def _get_new_prompt(self, evolve_prompt_query: str, runtime_context: str) -> str:
        """Fetches a new prompt from the OpenAI API."""
        return self.openai_wrapper.chat_completion(
            messages=[{"role": "system", "content": evolve_prompt_query + runtime_context}]
        )
