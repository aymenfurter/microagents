import openai
import time
import logging

from .memoize import memoize_to_sqlite

RETRY_SLEEP_DURATION = 1  # seconds
MAX_RETRIES = 5

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
                return openai.Embedding.create(input=text, engine="text-embedding-ada-002")
            except openai.error.OpenAIError as e:
                logging.error(f"OpenAI API error: {e}")
                retries += 1
                if retries >= MAX_RETRIES:
                    raise
                time.sleep(RETRY_SLEEP_DURATION)
                #for those using the free version of openai
                #if f"{e}".startswith("Rate limit"):
                #   print("Rate limit reached...  sleeping for 20 seconds")
                #   start_time+=20
                #   time.sleep(20)
        raise TimeoutError("API call timed out")

    @memoize_to_sqlite(func_name="chat_completion", filename="openai_chat_cache.db")
    def chat_completion(self, **kwargs):
        """
        Generates a chat completion using OpenAI's API.

        :param kwargs: Keyword arguments for the chat completion API call.
        :return: The result of the chat completion API call.
        """

        if 'model' not in kwargs:
           kwargs['model']='gpt-4-1106-preview'
           #kwargs['model']='gpt-3.5-turbo'     #for those using free version of openai

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
                #for those using the free version of openai
                #if f"{e}".startswith("Rate limit"):
                #   print("Rate limit reached...  sleeping for 20 seconds")
                #   start_time+=20
                #   time.sleep(20)
        raise TimeoutError("API call timed out")
