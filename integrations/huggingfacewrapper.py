from sentence_transformers import SentenceTransformer

import torch
from transformers import pipeline

import time
import logging

RETRY_SLEEP_DURATION = 1  # seconds
MAX_RETRIES=5

from utils.utility import get_env_variable

EMBEDDING_MODEL=get_env_variable("EMBEDDING_MODEL", "all-MiniLM-L6-v2", False)
CHAT_MODEL=get_env_variable("CHAT_MODEL", "TinyLlama/TinyLlama-1.1B-Chat-v1.0", False)

class HuggingFaceWrapper:
    """
    A wrapper class for OpenAI's API.
    """

    def __init__(self, timeout=10):
        """
        Initializes the OpenAIAPIWrapper instance.

        :param api_key: The API key for OpenAI.
        :param timeout: The timeout duration in seconds for API requests.
        """
        self.timeout = timeout
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        self.chat_model_pipe = pipeline("text-generation", model=CHAT_MODEL, torch_dtype=torch.bfloat16, device_map="auto")

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
                return self.embedding_model.encode(text).tolist()
            except Exception as e:
                logging.error(f"Huggin API error: {e}")
                retries += 1
                if retries >= MAX_RETRIES:
                    raise
                time.sleep(RETRY_SLEEP_DURATION)

        raise TimeoutError("API call timed out")

    def chat_completion(self, **kwargs):
        """
        Generates a chat completion using Hugging Face.

        :param kwargs: Keyword arguments for the chat completion API call.
        :return: The result of the chat completion API call.
        """

        start_time = time.time()
        retries = 0

        while time.time() - start_time < self.timeout:
            try:
                prompt = self.chat_model_pipe.tokenizer.apply_chat_template(kwargs['messages'], tokenize=False, add_generation_prompt=True)
                outputs = self.chat_model_pipe(prompt, max_new_tokens=256, do_sample=True, temperature=0.7, top_k=50, top_p=0.95)
                return outputs[0]["generated_text"]
            except ValueError as e:
                logging.error(f"error: {e}")
                retries += 1
                if retries >= MAX_RETRIES:
                    raise
                time.sleep(RETRY_SLEEP_DURATION)
        raise TimeoutError("API call timed out")
