from sparkai.llm.llm import ChatSparkLLM, ChunkPrintHandler
from sparkai.core.messages import ChatMessage
from base_llm import BaseLlm


class sparkApi(BaseLlm):
    def __init__(self, SPARKAI_APP_ID, SPARKAI_API_SECRET, SPARKAI_API_KEY, SPARKAI_URL='wss://spark-api.xf-yun.com/v4.0/chat', SPARKAI_DOMAIN = '4.0Ultra', temperature=0.6, max_tokens=4036, top_k=1):
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
        self.spark_api_url = SPARKAI_URL
        self.spark_app_id = SPARKAI_APP_ID
        self.api_key = SPARKAI_API_KEY
        self.spark_api_secret = SPARKAI_API_SECRET
        self.spark_llm_domain = SPARKAI_DOMAIN

    def get_source(self):
        return "Spark"

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
        return {"Domain":self.spark_llm_domain, "Url":self.spark_api_url}

    def chat_completion(self, prompt, max_tokens=4036):
        """
        Call the Spark chat completion API.

        Args:
            messages (list): The messages.
            max_tokens (int): The maximum number of tokens.

        Returns:
            dict: The response.
        """
        spark = ChatSparkLLM(
            spark_api_url=self.spark_api_url,
            spark_app_id=self.spark_app_id,
            spark_api_key=self.api_key,
            spark_api_secret=self.spark_api_secret,
            spark_llm_domain=self.spark_llm_domain,
            streaming=False,
        )
        cnt = 0
        repeat_times = 5
        while (cnt < repeat_times):
            cnt += 1
            try:
                messages = [ChatMessage(
                    role="user",
                    content=prompt
                )]   # hhq这里可以自己实现一下这个函数
                handler = ChunkPrintHandler()
                a = spark.generate([messages], callbacks=[handler])
                return {"content":a.generations[0][0].text}
            except:
                # logger.info("ChatGLM error!")
                print("SparkApi error!")
                return

    def get_models(self):
        pass

    def verify_access_key(self):
        pass