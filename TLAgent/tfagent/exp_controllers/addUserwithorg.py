import argparse

from tfagent.models.organisation import Organisation
from tfagent.models.project import Project
from tfagent.models.user import User
from tfagent.lib.logger import logger
from tfagent.models.models_config import ModelsConfig

from tfagent.models.db import connect_db
from sqlalchemy.orm import sessionmaker

engine = connect_db()
Session = sessionmaker(bind=engine)
session = Session()

def args_parser():
    parser = argparse.ArgumentParser(description='Create new model.')
    parser.add_argument('--org', type=str, default="tfagent organisation",
                        help='The user organisation.')
    parser.add_argument('--orgdesc', type=str, default="tfagent organisation",
                        help='organisation description.')

    parser.add_argument('--username', type=str, default="admin",
                        help='the provider of the model.')
    parser.add_argument('--useremail', type=str, default="admin@tfagent.com",
                        help='user email.')
    parser.add_argument('--userpasswd', type=str, default="123456",
                        help='user password')


    args = parser.parse_args()

    return args

def create_user(args):
    """
    Create a new user.

    Args:
        user (UserIn): User data.

    Returns:
        User: The created user.

    Raises:
        HTTPException (status_code=400): If there is an issue creating the user.

    """

    # check user exist
    db_user = session.query(User).filter(User.email == args.useremail).first()
    if db_user:
        logger.info("User exist", db_user)
        return

    # create orgnisation
    organisation = Organisation(name=args.org, description=args.orgdesc)
    session.add(organisation)
    session.flush()  # Flush pending changes to generate the agent's ID
    session.commit()
    logger.info(organisation)

    # create user
    db_user = User(name=args.username, email=args.useremail, password=args.userpasswd, organisation_id=organisation.id)
    session.add(db_user)
    session.commit()
    session.flush()

    Project.find_or_create_default_project(session, organisation.id)
    logger.info("User created", db_user)

    # adding local llm configuration
    # ModelsConfig.add_llm_config(session, organisation.id)
    return

if __name__ == "__main__":
    args = args_parser()
    create_user(args)