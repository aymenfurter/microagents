import logging
from integrations.openaiwrapper import OpenAIAPIWrapper

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

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
            logging.error(f"Error evolving prompt: {e}")
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
        feedback_query = "How should the GPT-4 prompt evolve based on this input and feedback?"
        if new_solution:
            feedback_query += " Consider the solution provided in the full conversation section and make it reusable."
        return f"{feedback_query} Current Prompt: {dynamic_prompt}, Full Conversation: {full_conversation}"

    def _get_new_prompt(self, evolve_prompt_query: str, runtime_context: str) -> str:
        """Fetches a new prompt from the OpenAI API."""
        response = self.openai_wrapper.chat_completion(
            model="gpt-4-1106-preview",
            messages=[{"role": "system", "content": evolve_prompt_query + runtime_context}]
        )
        return response.choices[0].message['content'].strip()