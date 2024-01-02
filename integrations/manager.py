from utils.utility import get_env_variable
from .memoize import memoize_to_sqlite

from dotenv import load_dotenv
load_dotenv()

LLM_SOURCE = get_env_variable("LLM_SOURCE", "openai", False)


class LLM_Manager:
    """
    A manager class for LLMs, etc.
    """

    def __init__(self, timeout=10):
        """
        Initializes the OpenAIAPIWrapper instance.

        :param api_key: The API key for OpenAI.
        :param timeout: The timeout duration in seconds for API requests.
        """
        if LLM_SOURCE == "openai":
           from .openaiwrapper import OpenAIAPIWrapper
           api_key=get_env_variable("OPENAI_KEY", None, True)
           self.api=OpenAIAPIWrapper(api_key, timeout=timeout)
        elif LLM_SOURCE== "huggingface":
           from .huggingfacewrapper import HuggingFaceWrapper
           self.api=HuggingFaceWrapper(timeout)
        else:
           raise Exception("LLM_SOURCE environment variable needs to be set to openai or huggingface")

    @memoize_to_sqlite(func_name="get_embedding", filename=LLM_SOURCE+"_embedding_cache.db")
    def get_embedding(self, text):
        """
        Retrieves the embedding for the given text.

        :param text: The text for which embedding is required.
        :return: The embedding for the given text.
        """
        return self.api.get_embedding(text)

    def chat_completion(self, **kwargs):
        """
        Generates a chat completion using OpenAI's API.

        :param kwargs: Keyword arguments for the chat completion API call.
        :return: The result of the chat completion API call.
        """

        return self.api.chat_completion(**kwargs)
