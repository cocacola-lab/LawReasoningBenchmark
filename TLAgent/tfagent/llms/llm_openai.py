# the version of openai library should be higher than 1.0.
from openai import OpenAI
from openai import BadRequestError
from openai import RateLimitError, AuthenticationError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_random_exponential

from tfagent.config.config import get_config
from tfagent.lib.logger import logger
from tfagent.llms.base_llm import BaseLlm

MAX_RETRY_ATTEMPTS = 5
MIN_WAIT = 30 # Seconds
MAX_WAIT = 300 # Seconds

def custom_retry_error_callback(retry_state):
    logger.info("OpenAi Exception:", retry_state.outcome.exception())
    return {"error": "ERROR_OPENAI", "message": "Open ai exception: "+str(retry_state.outcome.exception())}

class OpenAi(BaseLlm):
    def __init__(self, api_key, model="gpt-4", temperature=0.6, max_tokens=get_config("MAX_MODEL_TOKEN_LIMIT"), top_p=1,
                 frequency_penalty=0,
                 presence_penalty=0, number_of_results=1):
        """
        Args:
            api_key (str): The OpenAI API key.
            model (str): The model.
            temperature (float): The temperature.
            max_tokens (int): The maximum number of tokens.
            top_p (float): The top p.
            frequency_penalty (float): The frequency penalty.
            presence_penalty (float): The presence penalty.
            number_of_results (int): The number of results.
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.number_of_results = number_of_results
        self.api_key = api_key
        self.client = OpenAI(
            api_key=api_key,
            base_url=get_config("OPENAI_API_BASE", "https://api.openai.com/v1"),
            timeout=10,
        )

    def get_source(self):
        return "openai"

    def get_api_key(self):
        """
        Returns:
            str: The API key.
        """
        return self.api_key

    def get_model(self):
        """
        Returns:
            str: The model.
        """
        return self.model

    @retry(
        retry=(
            retry_if_exception_type(RateLimitError)
        ),
        stop=stop_after_attempt(MAX_RETRY_ATTEMPTS), # Maximum number of retry attempts
        wait=wait_random_exponential(min=MIN_WAIT, max=MAX_WAIT),
        before_sleep=lambda retry_state: logger.info(f"{retry_state.outcome.exception()} (attempt {retry_state.attempt_number})"),
        retry_error_callback=custom_retry_error_callback
    )

    def chat_completion(self, messages, max_tokens=get_config("MAX_MODEL_TOKEN_LIMIT")):
        """
        Call the OpenAI chat completion API.

        Args:
            messages (list): The messages.
            max_tokens (int): The maximum number of tokens.

        Returns:
            dict: The response.
        """
        try:
            response = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                n=self.number_of_results,
                temperature=self.temperature,
                max_tokens=max_tokens,
                top_p=self.top_p,
                frequency_penalty=self.frequency_penalty,
                presence_penalty=self.presence_penalty
            )
            content = response.choices[0].message.content
            return {"response": response, "content": content}
        except RateLimitError as api_error:
            logger.info("OpenAi RateLimitError:", api_error)
            raise RateLimitError(str(api_error))
        except AuthenticationError as auth_error:
            logger.info("OpenAi AuthenticationError:", auth_error)
            return {"error": "ERROR_AUTHENTICATION", "message": "Authentication error please check the api keys: "+str(auth_error)}
        except BadRequestError as bad_request_error:
            logger.info("OpenAi InvalidRequestError:", bad_request_error)
            return {"error": "ERROR_INVALID_REQUEST", "message": "Openai invalid request error: "+str(bad_request_error)}
        except Exception as exception:
            logger.info("OpenAi Exception:", exception)
            return {"error": "ERROR_OPENAI", "message": "OpenAi exception: "+str(exception)}

    def verify_access_key(self):
        """
        Verify the access key is valid.

        Returns:
            bool: True if the access key is valid, False otherwise.
        """
        try:
            models = OpenAI.models.list()
            return True
        except Exception as exception:
            logger.info("OpenAi Exception:", exception)
            return False

    def get_models(self):
        """
        Get the models.

        Returns:
            list: The models.
        """
        try:
            models = OpenAI.models.list()
            models = [model["id"] for model in models.data]
            models_supported = ['gpt-4', 'gpt-4o', 'gpt-4o-mini', 'gpt-3.5-turbo', 'gpt-3.5-turbo-16k', 'gpt-4-32k']
            models = [model for model in models if model in models_supported]
            return models
        except Exception as exception:
            logger.info("OpenAi Exception:", exception)
            return []
