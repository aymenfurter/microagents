import openai
import time

class OpenAIAPIWrapper:
    def __init__(self, api_key, timeout=10):
        openai.api_key = api_key
        self.timeout = timeout
        self.cache = {}

    def get_embedding(self, text):
        if text in self.cache:
            return self.cache[text]

        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                embedding = openai.Embedding.create(input=text, engine="text-embedding-ada-002")
                self.cache[text] = embedding
                return embedding
            except Exception as e:
                time.sleep(1)  # Wait for 1 second before retrying
        raise TimeoutError("API call timed out")

    def chat_completion(self, **kwargs):
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                return openai.ChatCompletion.create(**kwargs)
            except Exception as e:
                time.sleep(1)  # Wait for 1 second before retrying
        raise TimeoutError("API call timed out")