import logging
from integrations.openaiwrapper import OpenAIAPIWrapper

# Basic logging setup
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
MODEL_NAME = "gpt-4-1106-preview"

class AgentEvaluator:
    """
    Evaluates AI agent's responses using OpenAI's GPT model.
    """

    def __init__(self, openai_wrapper: OpenAIAPIWrapper):
        self.openai_api = openai_wrapper

    def evaluate(self, input_text: str, prompt: str, output: str) -> str:
        """
        Returns evaluation of agent's output as 'Poor', 'Good', or 'Perfect'.
        """
        try:
            query = ("Evaluate LLM Output: '{input}' with prompt '{prompt}' "
                     "for quality/relevance. Possible Answers: Poor, Good, Perfect. "
                     "LLM output: '{output}'").format(input=input_text, prompt=prompt, output=output)

            result = self.openai_api.chat_completion(
                model=MODEL_NAME,
                messages=[{"role": "system", "content": query}]
            )
            return result.choices[0].essage['content']

        except Exception as error:
            logging.info(f"Agent evaluation error: {error}")
            raise