from zhipuai import ZhipuAI
from tfagent.config.config import get_config
from tfagent.lib.logger import logger
from tfagent.llms.base_llm import BaseLlm


class chatGlm(BaseLlm):
    def __init__(self, api_key, model="glm-4-0520", temperature=0.6, max_tokens=get_config("MAX_MODEL_TOKEN_LIMIT"),
                 top_p=1):
        """
        Args:
            api_key (str): The ZhipuAI API key.
            model (str): The model.
            temperature (float): The temperature.
            max_tokens (int): The maximum number of tokens.
            top_p (float): The top p.
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.api_key = api_key

    def get_source(self):
        return "zhipu"

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

    def chat_completion(self, messages, max_tokens=get_config("MAX_MODEL_TOKEN_LIMIT")):
        """
        Call the ZhipuAI chat completion API.

        Args:
            prompt
            max_tokens (int): The maximum number of tokens.

        Returns:
            dict: The response.
        """
        client = ZhipuAI(api_key=self.api_key)
        cnt = 0
        repeat_times = 5
        while (cnt < repeat_times):
            cnt += 1
            try:
                # openai.api_key = get_config("OPENAI_API_KEY")
                response = client.chat.completions.create(
                    model=self.model,
                    # messages=[
                    #     {"role": "user", "content": prompt}
                    # ],
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=max_tokens,
                    top_p=self.top_p
                )
                content = response.choices[0].message.content  # 改过
                return {"response": response, "content": content}
            except:
                logger.info("ChatGLM error!")
                return

    def get_models(self):
        pass

    def verify_access_key(self):
        pass