import logging
from integrations.openaiwrapper import OpenAIAPIWrapper
from prompt_management.prompts import AGENT_EVALUATION_PROMPT
# Basic logging setup
logger = logging.getLogger()

class AgentEvaluator:
    """
    Evaluates AI agent's responses using OpenAI's GPT model.
    """

    def __init__(self, openai_wrapper: OpenAIAPIWrapper):
        self.openai_api = openai_wrapper

    def evaluate(self, input_text: str, prompt: str, output: str) -> str:
        """
        Returns evaluation agents response (score from 1-5) 
        """

        try:
            formatted_prompt = AGENT_EVALUATION_PROMPT.format(input=input_text, prompt=prompt, output=output)
            response = self.openai_api.chat_completion(messages=[{"role": "system", "content": formatted_prompt}])

            if "5" in response or "4" in response:
                return True
            else:
                return False
        except Exception as error:
            logger.exception(f"Agent evaluation error: {error}")
            raise
