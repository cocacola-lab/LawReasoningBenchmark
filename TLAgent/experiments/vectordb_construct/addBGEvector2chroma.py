import os
import random
import argparse
from tfagent.config.config import get_config
from tfagent.types.embedding_type import EmbeddingType
from tfagent.vector_store.chromadb import ChromaDB

from tfagent.vector_store.embedding.openai import OpenAiEmbedding
from tfagent.vector_store.embedding.palm import PalmEmbedding
from tfagent.vector_store.embedding.hugginglocalembed import HuggingFaceLocalEmbed

from utils import readjson

random.seed(1)

def args_parser():
    parser = argparse.ArgumentParser(description='Create new chroma collection.')
    # embedding model
    parser.add_argument('--embedding-model', type=str, default="HuggingLocalEmbedding",
                        choices=["OpenAiEmbedding","PalmEmbedding","HuggingLocalEmbedding"],
                        help='the name of embedding model')
    parser.add_argument('--api-key', type=str,
                        help='The apikey of the embedding model.')
    parser.add_argument("--embed-url", type=str,
                        help="The url of the embedding model.")
    parser.add_argument("--embed-name", type=str, default="BAAI/bge-large-zh-v1.5",
                        choices=["BAAI/bge-large-zh-v1.5"],
                        help="The name the embedding model.")
    # chromadb
    parser.add_argument("--collection-name", type=str, required=True,
                        help="The name of the collection.")
    parser.add_argument('--text-field', type=str, default="",
                        help='The name of the text field.')

    # the path of knowledge data
    parser.add_argument('--knowledge-data', type=str, default="./knowledge/raw_neg_evid.json",
                        help='The path of knowledgedata.')
    # max number of knowledge chunk
    parser.add_argument('--batch-size', type=int, default=10,
                        help='The number of processing text at one time')
    parser.add_argument("--sample-num", type=int, default=-1,
                        help='Is it necessary to sample part of the data set to add to the database, '
                             'if -1 is not required to sample, if a positive number is the number of samples')

    args = parser.parse_args()
    return args


def EmbeddingModel(embed_type: str, apikey: str, embedurl:str, model_name:str=None):
    if embed_type == EmbeddingType.OPENAIEMBEDDING:
        return OpenAiEmbedding(apikey, embedurl)
    if embed_type == EmbeddingType.PALMEMBEDDING:
        return PalmEmbedding(apikey, embedurl)
    if embed_type == EmbeddingType.HUGGINGLOCALEMBEDDING:
        return HuggingFaceLocalEmbed(model_name)


def main():
    args = args_parser()

    embed_type = EmbeddingType.get_embedding_type(args.embedding_model)
    embed_model = EmbeddingModel(embed_type, args.api_key, args.embed_url, args.embed_name)

    # args.collection_name = "fact"
    # args.collection_name = "evidence"

    ChromaDB.create_collection(args.collection_name)
    chroma_client = ChromaDB(collection_name=args.collection_name,
                             embedding_model=embed_model,
                             text_field=args.text_field, )

    # load files
    raw_knowledge = readjson(args.knowledge_data)

    # sample
    if args.sample_num > 0:
        raw_knowledge = random.sample(raw_knowledge, args.sample_num)

    batch = []
    for i, item in enumerate(raw_knowledge):
        if len(batch) < args.batch_size and i <= len(raw_knowledge) - 1:
            batch.append(item)

        if len(batch) == args.batch_size:
            print(f"process the {i+1} data...")
            chroma_client.add_texts(texts=[it["page_content"] for it in batch],
                                    metadatas=batch,)
            batch = []

if __name__ == '__main__':
    main()


# For testing
# collectionname == test1

# Fact-related database
# collectionname == fact
# The following two files need to be imported into the fact-related database
# knowledge-data = raw_pos_fact.json
# Generally, for negative samples, sampling is required, with a ratio of pos_fact:neg_fact approximately 1:2 or 1:3
# knowledge-data = raw_neg_fact.json

# Evidence-related database
# collectionname == evidence
# The following two files need to be imported into the evidence-related database
# knowledge-data = raw_pos_evid.json
# Generally, for negative samples, sampling is required, with a ratio of pos_evid:neg_evid approximately 1:2 or 1:3