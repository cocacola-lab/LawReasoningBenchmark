import os
import argparse

from tfagent.models.models_config import ModelsConfig
from tfagent.models.organisation import Organisation
from tfagent.models.models import Models
from tfagent.models.user import User
from tfagent.models.vector_dbs import Vectordbs
from tfagent.models.vector_db_configs import VectordbConfigs
from tfagent.models.vector_db_indices import VectordbIndices
from tfagent.vector_store.vector_factory import VectorFactory
from tfagent.models.db import connect_db

from sqlalchemy.orm import sessionmaker
from tfagent.lib.logger import logger


engine = connect_db()
Session = sessionmaker(bind=engine)
session = Session()


def args_parser():
    parser = argparse.ArgumentParser(description='Create new model.')
    parser.add_argument('--useremail', type=str, default="admin@tfagent.com",
                        help='user email.')

    parser.add_argument('--name', type=str, default="evid knowledge",
                        help='the name of the custom chromadb.')
    # --collections collectionname1 collectionname2 ....
    parser.add_argument('--collections', nargs="+",
                        help='collection name list')

    #

    # parser.add_argument('--contextlength', type=str, help='The context')

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = args_parser()

    # organization
    db_user = session.query(User).filter(User.email == args.useremail).first()
    logger.info(db_user)
    organisation = session.query(Organisation).filter(Organisation.id == db_user.organisation_id).first()
    logger.info(organisation)

    db_creds = {"embedding_name": "BAAI/bge-large-zh-v1.5",
                "embedding_type": "HuggingLocalEmbedding"}

    for collection in args.collections:
        try:
            vector_db_storage = VectorFactory.build_vector_storage("chroma", collection, **db_creds)
            db_connect_for_index = vector_db_storage.get_index_stats()
            index_state = "Custom" if db_connect_for_index["vector_count"] > 0 else "None"
        except:
            raise Exception("Unable to connect chroma")

    chroma_db = Vectordbs.add_vector_db(session, args.name, "chroma", organisation)
    VectordbConfigs.add_vector_db_config(session, chroma_db.id, db_creds)

    for collection in args.collections:
        VectordbIndices.add_vector_index(session, collection, chroma_db.id, index_state,
                                         db_connect_for_index["dimensions"])

    session.close()