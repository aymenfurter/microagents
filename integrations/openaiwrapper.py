import openai
import time
import logging

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
        self.cache = {}

    def get_embedding(self, text):
        """
        Retrieves the embedding for the given text.

        :param text: The text for which embedding is required.
        :return: The embedding for the given text.
        """
        if text in self.cache:
            return self.cache[text]

        start_time = time.time()
        retries = 0

        while time.time() - start_time < self.timeout:
            try:
                embedding = openai.Embedding.create(input=text, engine="text-embedding-ada-002")
                self.cache[text] = embedding
                return embedding
            except openai.error.OpenAIError as e:
                logging.error(f"OpenAI API error: {e}")
                retries += 1
                if retries >= MAX_RETRIES:
                    raise
                time.sleep(RETRY_SLEEP_DURATION)
        
        raise TimeoutError("API call timed out")

    def chat_completion(self, **kwargs):
        """
        Generates a chat completion using OpenAI's API.

        :param kwargs: Keyword arguments for the chat completion API call.
        :return: The result of the chat completion API call.
        """
        start_time = time.time()
        retries = 0

        while time.time() - start_time < self.timeout:
            try:
                return openai.ChatCompletion.create(**kwargs)
            except openai.error.OpenAIError as e:
                logging.error(f"OpenAI API error: {e}")
                retries += 1
                if retries >= MAX_RETRIES:
                    raise
                time.sleep(RETRY_SLEEP_DURATION)
        
        raise TimeoutError("API call timed out")