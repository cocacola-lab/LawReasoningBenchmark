import openai
from tfagent.vector_store.embedding.base import BaseEmbedding

class OpenAiEmbedding(BaseEmbedding):
    def __init__(self, api_key, embed_url="https://api.openai.com/v1", model="text-embedding-3-small"):
        self.model = model
        self.api_key = api_key
        self.embed_url = embed_url
        
    async def get_embedding_async(self, text: str):
        try:
            openai.api_key = self.api_key

            response = await openai.Embedding.create(
                                input=[text],
                engine=self.model
            )
            return response['data'][0]['embedding']
        except Exception as exception:
            return {"error": exception}    

               
    def get_embedding(self, text):
        try:
            # openai.api_key = get_config("OPENAI_API_KEY")

            response = openai.Embedding.create(
                api_key=self.api_key,
                api_base=self.embed_url,
                input=[text],
                engine=self.model
            )
            return response['data'][0]['embedding']
        except Exception as exception:
            return {"error": exception}
