import os
import argparse

from tfagent.models.models_config import ModelsConfig
from tfagent.models.organisation import Organisation
from tfagent.models.models import Models
from tfagent.models.user import User

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

    parser.add_argument('--modelprovider', type=str, default="OpenAI",
                        help='the provider of the model.')
    parser.add_argument('--apikey', type=str, help='The apikey of the llm.')
    parser.add_argument('--modelname', type=str, help='The name of llm.')
    parser.add_argument('--modeldesc', type=str, help='The model description of the llm.')
    parser.add_argument('--endpoint', type=str, default="",
                        help='The end_point for the model.3001' )
    parser.add_argument('--model-features', type=str, default="",
                        help='The features of the llm')
    parser.add_argument("--type", type=str,  default="custom",
                        help='The type of llm.')
    parser.add_argument("--tokenlimit", type=int,  default=4096,
                        help='the token limit of llm.')

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

    if args.modelprovider != "OpenAI":
        Models.store_model_details(session=session,
                                   organisation_id=organisation.id,
                                   model_name=args.modelname,
                                   description=args.modeldesc,
                                   end_point=args.endpoint,
                                   model_provider_id=args.modelprovider,
                                   token_limit=args.tokenlimit,
                                   type=args.type,
                                   version="",
                                   context_length=0)


    ModelsConfig().store_api_key(session=session,
                                 organisation_id=organisation.id,
                                 model_provider=args.modelprovider,
                                 model_api_key=args.apikey)

    session.close()