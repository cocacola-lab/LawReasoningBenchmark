from tfagent.config.config import get_config
from tfagent.vector_store.embedding.base import BaseEmbedding


from langchain.embeddings import HuggingFaceBgeEmbeddings

#
class HuggingFaceLocalEmbed(BaseEmbedding):
    def __init__(self, model_name, ):
        """
        Args:
            model (str): The name of huggingface model.
        """
        self.model_name = model_name
        self.device = get_config("HUGGING_MODEL_DEVICE", "cpu")
        self.embedding_model = None

        if "bge" in self.model_name:
            self.embedding_model = HuggingFaceBgeEmbeddings(
                model_name=self.model_name,
                model_kwargs={'device': self.device},
                encode_kwargs={'normalize_embeddings': True}, )

    def get_embedding(self, text):
        """
            Get the embedding vector for the given text.

           The embed function is called to build the database when the default text is of type list,
           and the query function is called to retrieve the database when the text is of type str.

            Parameters:
            - text (list[str] | str): The input text or list of texts for which to generate the embedding vectors.

            Returns:
            - list[float] | dict: A list of embedding vectors
        """
        try:
            if isinstance(text, list):
                return self.embedding_model.embed_documents(text)
            elif isinstance(text, str):
                return self.embedding_model.embed_query(text)
            else:
                raise ValueError("The incorrect type of input text")

        except Exception as exception:
            return {"error": exception}
