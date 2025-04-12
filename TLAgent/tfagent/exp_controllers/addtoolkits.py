import argparse

from tfagent.models.user import User

from tfagent.lib.logger import logger

from tfagent.helper.tool_helper import register_toolkits, register_marketplace_toolkits

from tfagent.models.db import connect_db
from tfagent.models.organisation import Organisation

from sqlalchemy.orm import sessionmaker

engine = connect_db()
Session = sessionmaker(bind=engine)
session = Session()

def args_parser():
    parser = argparse.ArgumentParser(description='Create new model.')
    parser.add_argument('--useremail', type=str, default="admin@tfagent.com",
                        help='user email.')

    args = parser.parse_args()

    return args

def register_agent_toolkits(args):
    """
    Register agent toolkits.

    Args:
        user (UserIn): User data.

    Returns:
        User: The created user.

    Raises:
        HTTPException (status_code=400): If there is an issue creating the user.

    """

    # check user exist
    # organization
    db_user = session.query(User).filter(User.email == args.useremail).first()
    logger.info(db_user)
    organisation = session.query(Organisation).filter(Organisation.id == db_user.organisation_id).first()
    logger.info(organisation)
    tool_paths = ["D:/Code/PyProject/Law_TF_refine/tfagent/tools"]
    register_toolkits(session=session, organisation=organisation, tool_paths=tool_paths)

    return

if __name__ == "__main__":
    args = args_parser()
    register_agent_toolkits(args)