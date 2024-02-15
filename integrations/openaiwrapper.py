import openai
import time
import logging

from utils.utility import get_env_variable
from .memoize import memoize_to_sqlite

RETRY_SLEEP_DURATION = 1  # seconds

from dotenv import load_dotenv
load_dotenv()

ENGINE=get_env_variable("OPENAI_EMBEDDING", "text-embedding-ada-002", False)
MODEL=get_env_variable("OPENAI_MODEL", "gpt-4-1106-preview", False)

def get_configured_openai_wrapper(timeout: float = 10, max_retries: int = 5):
    """
    Returns the configured OpenAI wrapper.

        :param timeout: The timeout duration in seconds for API requests.
        :param max_retries: Number of retries for API requests.
    """
    openai_base_url = get_env_variable("OPENAI_BASE_URL", None, False)
    # backward compatibility with OPENAI_API_BASE
    if openai_base_url is None:
        openai_base_url = get_env_variable("OPENAI_API_BASE", None, False)
    openai_api_key = get_env_variable("OPENAI_API_KEY", None, False)
    openai_org_id = get_env_variable("OPENAI_ORG_ID", None, False)
    azure_openai_api_key = get_env_variable("AZURE_OPENAI_API_KEY", None, False)
    azure_openai_endpoint = get_env_variable("AZURE_OPENAI_ENDPOINT", None, False)
    azure_openai_api_version = get_env_variable("AZURE_OPENAI_API_VERSION", "2023-12-01-preview", False)
    azure_openai_use_aad = get_env_variable("AZURE_OPENAI_USE_AAD", "false", False).strip().lower()
    azure_openai_ad_token = get_env_variable("AZURE_OPENAI_AD_TOKEN", None, False)
    azure_client_id = get_env_variable("AZURE_CLIENT_ID", None, False)
    

    # convert to boolean
    azure_openai_use_aad = ( azure_openai_use_aad == "true" or azure_openai_use_aad == "1"  or azure_openai_use_aad == "yes" or azure_openai_use_aad == "y" )

    # in case no api tokens are set, check if azure ad authentication is requested
    if openai_api_key is None and azure_openai_api_key is None:
        if azure_client_id is not None:
            azure_openai_use_aad = True
        if azure_openai_ad_token is not None:
            azure_openai_use_aad = True

    # check if the required environment variables are set
    if (
         (openai_api_key is None and azure_openai_api_key is None and azure_openai_use_aad==False) or
         (openai_api_key is not None and azure_openai_api_key is not None) or
         (openai_api_key is not None and azure_openai_use_aad) or
         (azure_openai_api_key is not None and azure_openai_use_aad)
    ):
        raise ValueError("Please set just one of the required environment variables: OPENAI_API_KEY or AZURE_OPENAI_API_KEY or AZURE_OPENAI_USE_AAD")
        
    # connect to openai or azure openai?
    if openai_api_key is not None:
        params = {
            "api_key": openai_api_key
        }
        if openai_base_url is None:
            logging.debug("Accessing OPENAI at %s" % openai_base_url)
            params["base_url"] = openai_base_url
        if openai_org_id is not None:
            params["organization"] = openai_org_id
        return OpenAIAPIWrapper(
            openai_client = openai.OpenAI(**params),
            timeout = timeout,
            max_retries = max_retries
        )
    else:
        if azure_openai_endpoint is None:
            raise ValueError("Please set the required environment variable: AZURE_OPENAI_ENDPOINT")
        params = {
            "azure_endpoint": azure_openai_endpoint,
            "api_version": azure_openai_api_version
        }

        if azure_openai_api_key is not None:
            params["api_key"] = azure_openai_api_key
        elif azure_openai_use_aad:
            if azure_openai_ad_token is not None:
                params["azure_ad_token"] = azure_openai_ad_token
            else:
                from azure.identity import get_bearer_token_provider, DefaultAzureCredential
                params["azure_ad_token_provider"] = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")
        else:
            raise RuntimeError("Please set one of the required environment variables: AZURE_OPENAI_API_KEY or AZURE_OPENAI_USE_AAD")
        if openai_org_id is not None:
            params["organization"] = openai_org_id

        return OpenAIAPIWrapper(
            openai_client = openai.AzureOpenAI(**params),
            timeout = timeout,
            max_retries = max_retries
        )


class OpenAIAPIWrapper:
    """
    A wrapper class for OpenAI's API.
    """
    _openai_client = None
    timeout : float = 10
    max_retries : int = 5

    def __init__(
        self,
        openai_client : openai.OpenAI | openai.AzureOpenAI, 
        timeout : float = 10,
        max_retries : int = 5
    ):
        """
        Initializes the OpenAIAPIWrapper instance.

        :param openai_client: The openai client
        :param timeout: The timeout duration in seconds for API requests.
        :param max_retries: Number of retries for API requests.
        """
        self._openai_client = openai_client
        self.timeout = timeout
        self.max_retries = max_retries

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
                response = self._openai_client.embeddings.create(input=text, model=ENGINE)
                data = {
                    "data": [],
                    "model": response.model,
                    "usage" : {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "total_tokens": response.usage.total_tokens
                    }
                }
                for emb in response.data:
                    data["data"].append({
                        "embedding": emb.embedding,
                        "index": emb.index
                    })
                return data
            except openai.OpenAIError as e:
                logging.error(f"OpenAI API error: {e}")
                retries += 1
                if retries >= self.max_retries:
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
                res=self._openai_client.chat.completions.create(**kwargs)
                if isinstance(res, dict):
                   if isinstance(res['choices'][0], dict):
                      return res['choices'][0]['message']['content'].strip()
                   return res['choices'][0].message['content'].strip()
                return res.choices[0].message.content.strip()
            except openai.OpenAIError as e:
                logging.error(f"OpenAI API error: {e}")
                retries += 1
                if retries >= self.max_retries:
                    raise
                time.sleep(RETRY_SLEEP_DURATION)

                if f"{e}".startswith("Rate limit"):
                   print("Rate limit reached...  sleeping for 20 seconds")
                   start_time+=20
                   time.sleep(20)
        raise TimeoutError("API call timed out")
