from enum import Enum


class EmbeddingType(Enum):
    OPENAIEMBEDDING = 'OpenAiEmbedding'
    PALMEMBEDDING = 'PalmEmbedding'
    HUGGINGLOCALEMBEDDING = 'HuggingLocalEmbedding'

    @classmethod
    def get_embedding_type(cls, store):
        store = store.upper()
        if store in cls.__members__:
            return cls[store]
        raise ValueError(f"{store} is not a valid embedding name.")

    def __str__(self):
        return self.value