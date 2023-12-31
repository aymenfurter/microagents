import openai
import time
import logging

from utils.utility import get_env_variable
from .memoize import memoize_to_sqlite

RETRY_SLEEP_DURATION = 1  # seconds
MAX_RETRIES = 5

from dotenv import load_dotenv
load_dotenv()

ENGINE=get_env_variable("OPENAI_EMBEDDING", "text-embedding-ada-002", False)
MODEL=get_env_variable("OPENAI_MODEL", "gpt-4-1106-preview", False)

API_BASE = get_env_variable("OPENAI_API_BASE", None, False)


class OpenAIAPIWrapper:
    """
    A wrapper class for OpenAI's API.
    """

    def __init__(self, api_key, timeout=10):
        """
        Initializes the OpenAIAPIWrapper instance.

        :param api_key: The API key for OpenAI.
        :param timeout: The timeout duration in seconds for API requests.
        """
        self.api_key = api_key
        openai.api_key = api_key
        if API_BASE is not None:
           logging.error("Accessing OPENAI at %s" % API_BASE)
           openai.api_base = API_BASE
        self.timeout = timeout

    @memoize_to_sqlite(func_name="get_embedding", filename="openai_embedding_cache.db")
    def get_embedding(self, text):
        """
        Retrieves the embedding for the given text.

        :param text: The text for which embedding is required.
        :return: The embedding for the given text.
        """
        start_time = time.time()
        retries = 0

        while time.time() - start_time < self.timeout:
            try:
                return openai.Embedding.create(input=text, engine=ENGINE)
            except openai.error.OpenAIError as e:
                logging.error(f"OpenAI API error: {e}")
                retries += 1
                if retries >= MAX_RETRIES:
                    raise
                time.sleep(RETRY_SLEEP_DURATION)

                if f"{e}".startswith("Rate limit"):
                   print("Rate limit reached...  sleeping for 20 seconds")
                   start_time+=20
                   time.sleep(20)
        raise TimeoutError("API call timed out")

    def chat_completion(self, **kwargs):
        """
        Generates a chat completion using OpenAI's API.

        :param kwargs: Keyword arguments for the chat completion API call.
        :return: The result of the chat completion API call.
        """

        if 'model' not in kwargs:
           kwargs['model']=MODEL

        start_time = time.time()
        retries = 0

        while time.time() - start_time < self.timeout:
            try:
                res=openai.ChatCompletion.create(**kwargs)
                if isinstance(res, dict):
                   if isinstance(res['choices'][0], dict):
                      return res['choices'][0]['message']['content'].strip()
                   return res['choices'][0].message['content'].strip()
                return res.choices[0].message['content'].strip()
            except openai.error.OpenAIError as e:
                logging.error(f"OpenAI API error: {e}")
                retries += 1
                if retries >= MAX_RETRIES:
                    raise
                time.sleep(RETRY_SLEEP_DURATION)

                if f"{e}".startswith("Rate limit"):
                   print("Rate limit reached...  sleeping for 20 seconds")
                   start_time+=20
                   time.sleep(20)
        raise TimeoutError("API call timed out")
