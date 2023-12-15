import logging
from openaiwrapper import OpenAIAPIWrapper

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PromptEvolution:
    def __init__(self, openai_wrapper, manager):
        self.openai_wrapper = openai_wrapper
        self.manager = manager

    def evolve_prompt(self, input_text, dynamic_prompt, output, full_conversation, new_solution, depth):
        """
        Evolves the prompt based on the feedback from the output and full conversation.
        """
        if len(full_conversation) > 1000:
            full_conversation = full_conversation[:200] + "..." + full_conversation[-1000:]

        runtime_context = self.generate_runtime_context(dynamic_prompt, depth)
        evolve_prompt_query = self.build_evolve_prompt_query(dynamic_prompt, output, full_conversation, new_solution)
        new_prompt = self.openai_wrapper.chat_completion(
            model="gpt-4-1106-preview",
            messages=[{"role": "system", "content": evolve_prompt_query + runtime_context}]
        ).choices[0].message['content'].strip()

        return new_prompt or dynamic_prompt

    def generate_runtime_context(self, dynamic_prompt, depth):
        """
        Generates runtime context for the evolve prompt query.
        """
        available_agents_arr = [agent for agent in self.manager.agents if agent.purpose != "General"]
        available_agents_with_depth = ', '.join([f"{agent.purpose} (depth={agent.depth})" for agent in available_agents_arr])
        runtime_context = f"Current Agent Depth: {depth}. Available agents: {available_agents_with_depth}."
        return runtime_context

    def build_evolve_prompt_query(self, dynamic_prompt, output, full_conversation, new_solution):
        """
        Builds the query for evolving the prompt.
        """
        feedback_query_part = "How should the GPT-4 prompt evolve based on this input and feedback?"
        if new_solution:
            feedback_query_part += " Take a look at the solution provided in the full conversation section. Adopt the code or solution found, make it reusable and compile a new, updated system prompt."

        evolve_prompt_query = f"{feedback_query_part} Current Prompt: {dynamic_prompt}, Full Conversation: {full_conversation}"
        return evolve_prompt_query
