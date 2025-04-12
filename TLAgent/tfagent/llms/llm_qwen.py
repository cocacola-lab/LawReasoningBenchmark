from base_llm import BaseLlm
from openai import OpenAI

class qwenApi(BaseLlm):
    def __init__(self, API_KEY, model = "qwen2-72b-instruct", base_url="https://dashscope.aliyuncs.com/compatible-mode/v1", temperature=0.6, max_tokens=4036, top_k=1):
        """
        Args:
            api_key (str): The API key.
            model (str): The model.
            temperature (float): The temperature.
            max_tokens (int): The maximum number of tokens.
            top_p (float): The top p.
        """
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_k = top_k
        self.api_key = API_KEY
        self.base_url = base_url
        self.model = model

    def get_source(self):
        return "Qwen"

    def get_api_key(self):
        """
        Returns:
            str: The API key.
        """
        return {self.api_key}

    def get_model(self):
        """
        Returns:
            str: The model.
        """
        return self.model

    def chat_completion(self, messages, max_tokens=4036):
        """
        Call the qwen chat completion API.

        Args:
            messages (list): The messages.
            max_tokens (int): The maximum number of tokens.

        Returns:
            dict: The response.
        """
        client = OpenAI(
            api_key=self.api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        completion = client.chat.completions.create(
            model="qwen2-72b-instruct",
            # messages=[
            #     {'role': 'system', 'content': 'You are a helpful assistant.'},
            #     {'role': 'user', 'content': prompt}],
            messages = messages,
            temperature=self.temperature,
            top_p=self.top_k
        )
        return completion.model_dump_json()

    def get_models(self):
        pass

    def verify_access_key(self):
        pass