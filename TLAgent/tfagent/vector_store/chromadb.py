import uuid
from typing import Any, Optional, Iterable, List, Union

import chromadb
from chromadb import Settings

from tfagent.config.config import get_config
from tfagent.vector_store.base import VectorStore
from tfagent.vector_store.document import Document
from tfagent.vector_store.embedding.base import BaseEmbedding

def build_chroma_client():
    chroma_host_name = get_config("CHROMA_HOST_NAME") or "localhost"
    chroma_port = get_config("CHROMA_PORT") or 8000
    chroma_persist_dir = get_config("CHROMA_PERSIST_DIR") or "./chromadata"
    return chromadb.Client(Settings(chroma_server_host=chroma_host_name,
                                    chroma_server_http_port=chroma_port,
                                    is_persistent = True,
                                    persist_directory=chroma_persist_dir))


class ChromaDB(VectorStore):
    def __init__(
            self,
            collection_name: str,
            embedding_model: BaseEmbedding,
            text_field: Union[str, None] = None,
            namespace: Optional[str] = "",
    ):

        self.client = build_chroma_client()
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        # save source text to the variable
        self.text_field = text_field if text_field else "text"
        self.dimension_field = "dimensions"
        self.namespace = namespace

    @classmethod
    def create_collection(cls, collection_name):
        """Create a Chroma Collection.
        Args:
        collection_name: The name of the collection to create.
        """
        chroma_client = build_chroma_client()
        collection = chroma_client.get_or_create_collection(name=collection_name)
        return collection

    def add_texts(
            self,
            texts: List[str],
            metadatas: Optional[List[dict]] = None,
            ids: Optional[List[str]] = None,
            collection = None,
            namespace: Optional[str] = None,
            batch_size: int = 32,
            **kwargs: Any,
    ) -> List[str]:
        """Add texts to the vector store."""

        ids = ids or [str(uuid.uuid4()) for _ in texts]
        if len(ids) < len(texts):
            raise ValueError("Number of ids must match number of texts.")

        embeds = []

        for text, id in zip(texts, ids):
            embed = self.__get_embeddings(text)
            embeds.append(embed)

            metadata = metadatas.pop(0) if metadatas != [] else {}
            metadata[self.text_field] = text
            metadata[self.dimension_field] = len(embed)
            metadatas.append(metadata)

        collection = self.client.get_collection(name=self.collection_name)

        if collection.metadata is None:
            collection.metadata = {self.dimension_field: len(embeds[0])}
        elif self.dimension_field not in collection.metadata:
            collection.metadata[self.dimension_field] = len(embeds[0])

        collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeds,
        )

        return ids

    def get_matching_text(self, query: str, top_k: int = 5, metadata: Optional[dict] = {}, **kwargs: Any) -> List[Document]:
        """Return docs most similar to query using specified search type."""
        embedding_vector = self.embedding_model.get_embedding(query)
        collection = self.client.get_collection(name=self.collection_name)
        filters = {}
        if metadata is not None:
            for key in metadata.keys():
                filters[key] = metadata[key]
        results = collection.query(
            query_embeddings=embedding_vector,
            include=["documents", "metadatas"],
            n_results=top_k,
            where=filters
        )

        documents = []

        for node_id, text, metadata in zip(
                results["ids"][0],
                results["documents"][0],
                results["metadatas"][0]):
            documents.append(
                Document(
                    text_content=text,
                    metadata=metadata
                )
            )

        return {"documents": documents, "search_res": ""}

    def __get_embeddings(
            self,
            text: str
    ) -> List[float]:
        """Return embedding for text using the embedding model."""
        if self.embedding_model is not None:
            query_vector = self.embedding_model.get_embedding(text)
        else:
            raise ValueError("Embedding model is not set")

        return query_vector

    def get_index_stats(self) -> dict:
        """
        Returns:
            Stats or Information about a collection
        """
        collection_info = self.client.get_collection(name=self.collection_name)
        dimensions = collection_info.metadata[self.dimension_field][0] \
            if (collection_info.metadata and self.dimension_field in collection_info.metadata
                and collection_info.metadata[self.dimension_field]) else None
        vector_count = collection_info.count()

        return {"dimensions": dimensions, "vector_count": vector_count}

    def add_embeddings_to_vector_db(self, embeddings: dict) -> None:
        pass

    def delete_embeddings_from_vector_db(self, ids: List[str]) -> None:
        pass

