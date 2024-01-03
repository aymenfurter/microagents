from integrations.manager import LLM_Manager

from prompt_management.prompts import STANDARD_SYSTEM_PROMPT, EXTRACTION_PROMPT_TEMPLATE

class ResponseExtraction:
    """
    A class responsible for extracting responses using OpenAI's GPT model.

    Attributes:
        openai_wrapper (OpenAIAPIWrapper): An instance of the OpenAIAPIWrapper class.
    """

    def __init__(self, llm_manager: LLM_Manager):
        """
        Initializes the ResponseExtraction class with an OpenAIAPIWrapper instance.

        Args:
            openai_wrapper (OpenAIAPIWrapper): An instance of the OpenAIAPIWrapper class.
        """
        if not isinstance(llm_manager, LLM_Manager):
            raise TypeError("llm_manager must be an instance of LLM_Manager")

        self.llm_manager = llm_manager

    def extract_response_from_prompt(self, prompt: str, question: str) -> str:
        """
        Extracts a response based on the given prompt and question using the OpenAI GPT model.

        Args:
            prompt (str): The initial prompt for the model.
            question (str): The user's question to be appended to the prompt.

        Returns:
            str: The extracted response.

        Raises:
            ValueError: If any of the arguments are not of expected type or empty.
        """
        if not prompt or not isinstance(prompt, str):
            raise ValueError("prompt must be a non-empty string")
        if not question or not isinstance(question, str):
            raise ValueError("question must be a non-empty string")

        formatted_prompt = EXTRACTION_PROMPT_TEMPLATE.format(question=question, prompt=prompt)
        messages = [
            {"role": "system", "content": STANDARD_SYSTEM_PROMPT},
            {"role": "user", "content": formatted_prompt}
        ]

        return self.llm_manager.chat_completion(messages=messages, max_tokens=100)
