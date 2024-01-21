import logging
from integrations.memoize import memoize_to_sqlite
from integrations.openaiwrapper import OpenAIAPIWrapper
from prompt_management.prompts import AGENT_NAME_EVALUATION_PROMPT
logger = logging.getLogger()

#feature flag
DISABLE_AGENT_NAME_EVALUATION = True

class AgentNameEvaluator:
    """
    Evaluates AI name responses using OpenAI's GPT model.
    """

    def __init__(self, openai_wrapper: OpenAIAPIWrapper):
        self.openai_api = openai_wrapper

    @memoize_to_sqlite(func_name="evaluate", filename="agent_name_evals.db")
    def evaluate(self, input_text: str, agent_name: str) -> str:
        """
        Returns evaluation agents response (score from 1-5) 
        """
        if DISABLE_AGENT_NAME_EVALUATION:
            return "5"

        try:
            formatted_prompt = AGENT_NAME_EVALUATION_PROMPT.format(input=input_text, agent_name=agent_name)
            response = self.openai_api.chat_completion(messages=[{"role": "system", "content": formatted_prompt}])

            print (f"Agent name {agent_name} evaluated as {response}")
            print(f"Input was {input_text}")
            if "5" in response or "4" in response:
                return True
            else:
                return False
        except Exception as error:
            logger.exception(f"Agent evaluation error: {error}")
            raise
