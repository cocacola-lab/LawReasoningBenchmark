import os
import argparse

from tfagent.models.models_config import ModelsConfig
from tfagent.models.organisation import Organisation
from tfagent.models.models import Models
from tfagent.models.user import User
from tfagent.models.vector_db_indices import VectordbIndices
from tfagent.models.knowledges import Knowledges
from tfagent.models.vector_dbs import Vectordbs
from tfagent.models.knowledge_configs import KnowledgeConfigs
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
    parser.add_argument('--knowledgename', type=str, default="test1knowledge",
                        help='knowledge name.')
    parser.add_argument('--vecindexname', type=str, default="test1",
                        help='vectordb index name or collection name.')
    parser.add_argument('--description', type=str, default="test",
                        help='the description of the knowledge database.')


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

    vector_db_index = VectordbIndices.get_vector_index_from_name(session, args.vecindexname)

    knowledge_data = {
        "id": -1,
        "name": args.knowledgename,
        "description": args.description,
        "index_id": vector_db_index.id,
        "organisation_id": organisation.id,
        "contributed_by": organisation.name,
    }

    new_knowledge = Knowledges.add_update_knowledge(session, knowledge_data)

    vector_database_index = VectordbIndices.get_vector_index_from_id(session, knowledge_data["index_id"])
    vector_database = Vectordbs.get_vector_db_from_id(session, vector_database_index.vector_db_id)

    knowledge_config = {
        "name": knowledge_data["name"],
        "description": knowledge_data["description"],
        "vector_database_index": {
            "id": vector_database_index.id,
            "name": vector_database_index.name
        },
        "vector_database": vector_database.name,
        "installation_type": vector_database_index.state
    }

    # knowledge_config = KnowledgeConfigs.add_update_knowledge_config(session, new_knowledge.id, knowledge_config)

    session.close()