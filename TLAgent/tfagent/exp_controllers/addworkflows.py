from tfagent.agent.workflow_seed import IterationWorkflowSeed, AgentWorkflowSeed
from tfagent.models.db import connect_db
from sqlalchemy.orm import sessionmaker


engine = connect_db()
Session = sessionmaker(bind=engine)
session = Session()

if __name__ == '__main__':
    IterationWorkflowSeed.build_single_step_agent(session)
