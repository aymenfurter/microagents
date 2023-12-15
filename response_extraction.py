from openaiwrapper import OpenAIAPIWrapper
from prompts import STANDARD_SYSTEM_PROMPT, EXTRACTION_PROMPT_TEMPLATE

class ResponseExtraction:
    def __init__(self, openai_wrapper):
        self.openai_wrapper = openai_wrapper

    def extract_response_from_prompt(self, prompt, question):
        """
        Extracts a response based on the given prompt and question.
        """
        extraction_prompt = EXTRACTION_PROMPT_TEMPLATE.format(question=question, prompt=prompt)
        messages = [
            {"role": "system", "content": STANDARD_SYSTEM_PROMPT},
            {"role": "user", "content": extraction_prompt}
        ]
        extraction = self.openai_wrapper.chat_completion(
            model="gpt-4",
            messages=messages,
            max_tokens=100,
        )

        return extraction.choices[0].message['content'].strip()
