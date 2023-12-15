import logging
from openaiwrapper import OpenAIAPIWrapper

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AgentEvaluation:
    def __init__(self, openai_wrapper):
        self.openai_wrapper = openai_wrapper

    def evaluate_agent(self, input_text, prompt, output):
        """
        Evaluates the performance of an agent based on given input, prompt, and output.
        """
        evaluation_query = f"Evaluate the generated LLM Output: '{input_text}' with the current prompt '{prompt}' for quality and relevance (Possible Answers: Poor, Good, Perfect), LLM output with current prompt: '{output}'"
        evaluation = self.openai_wrapper.chat_completion(
            model="gpt-4-1106-preview",
            messages=[{"role": "system", "content": evaluation_query}]
        ).choices[0].message['content']
        return evaluation