import logging
from integrations.manager import LLM_Manager

# Basic logging setup
logger = logging.getLogger()

class AgentEvaluator:
    """
    Evaluates AI agent's responses using OpenAI's GPT model.
    """

    def __init__(self, llm_manager: LLM_Manager):
        self.llm_manager = llm_manager

    def evaluate(self, input_text: str, prompt: str, output: str) -> str:
        """
        Returns evaluation of agent's output as 'Poor', 'Good', or 'Perfect'.
        """
        try:
            query = ("Evaluate LLM Output: '{input}' with prompt '{prompt}' "
                     "for quality/relevance. Possible Answers: Poor, Good, Perfect. "
                     "LLM output: '{output}'").format(input=input_text, prompt=prompt, output=output)

            return self.llm_manager.chat_completion(messages=[{"role": "system", "content": query}])
        except Exception as error:
            logger.exception(f"Agent evaluation error: {error}")
            raise
