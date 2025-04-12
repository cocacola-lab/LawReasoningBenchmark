import os
import argparse

from tfagent.types.embedding_type import EmbeddingType
from tfagent.vector_store.chromadb import ChromaDB

from tfagent.vector_store.embedding.openai import OpenAiEmbedding
from tfagent.vector_store.embedding.palm import PalmEmbedding
from tfagent.vector_store.embedding.hugginglocalembed import HuggingFaceLocalEmbed

def args_parser():
    parser = argparse.ArgumentParser(description='Create new chroma collection.')
    # embedding model
    parser.add_argument('--embeddingmodel', type=str, default="OpenAiEmbedding",
                        choices=["OpenAiEmbedding","PalmEmbedding"],
                        help='the name of embedding model')
    parser.add_argument('--apikey', type=str,
                        help='The apikey of the embedding model.')
    parser.add_argument("--embedurl", type=str,
                        help="The url of the embedding model.")

    # chromadb
    parser.add_argument("--collectionname", type=str, required=True,
                        help="The name of the collection.")
    parser.add_argument('--textfield', type=str, default="",
                        help='The name of the text field.')


    args = parser.parse_args()
    return args


def EmbeddingModel(embed_type: str, apikey: str, embedurl:str, model_name:str=None):
    if embed_type == EmbeddingType.OPENAIEMBEDDING:
        return OpenAiEmbedding(apikey, embedurl)
    if embed_type == EmbeddingType.PALMEMBEDDING:
        return PalmEmbedding(apikey, embedurl)
    if embed_type == EmbeddingType.HUGGINGLOCALEMBEDDING:
        return HuggingFaceLocalEmbed(model_name)


if __name__ == '__main__':
    args = args_parser()

    embed_type = EmbeddingType.get_embedding_type(args.embeddingmodel)
    embed_model = EmbeddingModel(embed_type, args.apikey, args.embedurl)
    # 用于测试
    # collectionname == test1
    # 事实相关的数据库
    # collectionname == fact
    # 证据相关的数据库
    # collectionname == evidence
    collection = ChromaDB.create_collection(args.collectionname)
    chroma_client = ChromaDB(collection_name = args.collectionname,
            embedding_model = embed_model,
            text_field=args.textfield,)

    collections = chroma_client.client.list_collections()

    chroma_client.add_texts(texts=["test1hhh"], metadatas=[], ids=None)
