import argparse
from datetime import datetime
from time import time
from tfagent.lib.logger import logger

from sqlalchemy.orm import sessionmaker

from tfagent.worker import execute_agent_serial, execute_agent
from tfagent.models.agent import Agent
from tfagent.models.agent_config import AgentConfiguration
from tfagent.models.agent_execution import AgentExecution
from tfagent.models.db import connect_db
from tfagent.models.organisation import Organisation
from tfagent.models.project import Project
from tfagent.models.user import User
from tfagent.models.workflows.agent_workflow import AgentWorkflow
from tfagent.models.workflows.iteration_workflow import IterationWorkflow

from tfagent.models.agent_execution_config import AgentExecutionConfiguration

parser = argparse.ArgumentParser(description='Create a new agent.')
# search user
parser.add_argument('--useremail', type=str, default="admin@tfagent.com",
                    help='user email.')
# task config
parser.add_argument('--name', type=str, help='Agent name for the script.')
parser.add_argument('--description', type=str, help='Agent description for the script.')
parser.add_argument('--goals', type=str, nargs='+', help='Agent goals for the script.')

# execution config
parser.add_argument("--permissiontype", type=str, default="",
                    choices=["God Mode", "Restrict"],
                    help='if you choose Restrict, the agent use the tool when you agree')
parser.add_argument("--workflow", type=str, default="Goal Based Workflow",
                    choices=["Goal Based Workflow", "Dynamic Task Workflow", "Fixed Task Workflow", "Split Json Items Workflow"],
                    help='Agent description for the script.')



args = parser.parse_args()

agent_name = args.name
agent_description = args.description
agent_goals = args.goals

engine = connect_db()
Session = sessionmaker(bind=engine)
session = Session()



def ask_user_for_goals():
    goals = []
    while True:
        goal = input("Enter a goal (or 'q' to quit): ")
        if goal == 'q':
            break
        goals.append(goal)
    return goals


def run_tfagent_cli(agent_name=None, agent_description=None, agent_goals=None):

    # organization
    db_user = session.query(User).filter(User.email == args.useremail).first()
    logger.info(db_user)
    organisation = session.query(Organisation).filter(Organisation.id == db_user.organisation_id).first()
    logger.info(organisation)


    # Create default project associated with the organization
    project = Project(name='Default Project', description='Default project description',
                      organisation_id=organisation.id)
    session.add(project)
    session.flush()  # Flush pending changes to generate the agent's ID
    session.commit()
    logger.info(project)

    # Agent
    if agent_name is None:
        agent_name = input("Enter agent name: ")
    if agent_description is None:
        agent_description = input("Enter agent description: ")

    agent_workflow = AgentWorkflow.find_by_name(session=session, name=args.workflow)

    agent = Agent(name=agent_name, description=agent_description, project_id=project.id, agent_workflow_id=agent_workflow.id)

    session.add(agent)
    session.flush()
    session.commit()
    logger.info(agent)

    # demo
    # fact finding agent
    # fact finding
    # Agent Config
    # Create Agent Configuration
    agent_config_values = {
        "goal": ask_user_for_goals() if agent_goals is None else agent_goals,
        "agent_type": "Type Non-Queue",
        "constraints": [],
        # "constraints":  ["~4000 word limit for short term memory. ",
        #                 # "Your short term memory is short, so immediately save important information to files.",
        #                 "If you are unsure how you previously did something or want to recall past events, thinking about similar events will help you remember.",
        #                 #"No user assistance",
        #                 "Exclusively use the commands listed in double quotes e.g. \"command name\""
        #                 ],
        "instructions": [], # ["When conducting the fact extraction task, it is necessary to first use the FactFindingHeadTool to extract the criminal facts in the text. Analyze the problems existing in the results obtained in the previous step, call as many other appropriate tools as possible to obtain external legal knowledge, update the extraction results of criminal facts, and improve the accuracy of the results. Note that the UniversalReflectionTool is mainly used to combine external knowledge to judge whether the extraction results are accurate and update the extraction results at the same time. Therefore, the UniversalReflectionTool cannot be used alone as a tool. It must be used after calling other tools once."],
        "tools": [16, 22, 23, 25, 26, 27],
        "exit": "Default",
        "iteration_interval": 0,
        "model": "gpt-4o-mini",
        "permission_type": "Default",
        "LTM_DB": None,
        "memory_window": 10,
        "max_iterations": 15,
    }

    start_step = AgentWorkflow.fetch_trigger_step_id(session=session,
                                                     workflow_id=agent.agent_workflow_id)

    agent_configurations = [
        AgentConfiguration(agent_id=agent.id, key=key, value=str(value))
        for key, value in agent_config_values.items()
    ]

    session.add_all(agent_configurations)
    session.commit()
    logger.info("Agent Config : ")
    logger.info(agent_configurations)

    iteration_step_id = IterationWorkflow.fetch_trigger_step_id(session,
                                                                start_step.id).id if start_step.action_type == "ITERATION_WORKFLOW" else -1

    # Create agent execution in RUNNING state associated with the agent
    execution = AgentExecution(status='RUNNING',
                               agent_id=agent.id,
                               name="New Run",
                               current_agent_step_id=start_step.id,
                               iteration_workflow_step_id=iteration_step_id, # 如果iteration_workflow_step_id = -1 表示没有
                               last_execution_time=datetime.utcnow())

    session.add(execution)
    session.commit()

    logger.info("Final Execution")
    logger.info(execution)

    # agent execution
    agent_execution_configs = {
        "goal": agent_config_values["goal"],
        "instruction": agent_config_values["instructions"],
        "constraints": agent_config_values["constraints"],
        "exit": agent_config_values["exit"],
        "tools": agent_config_values["tools"],
        "iteration_interval": agent_config_values["iteration_interval"],
        "model": agent_config_values["model"],
        "permission_type": agent_config_values["permission_type"],
        "LTM_DB": agent_config_values["LTM_DB"],
        "max_iterations": agent_config_values["max_iterations"],
        "user_timezone": None,
        "knowledge": None,
    }

    AgentExecutionConfiguration.add_or_update_agent_execution_config(session=session, execution=execution,
                                                                     agent_execution_configs=agent_execution_configs)

    # execute_agent_serial(execution.id, datetime.now())
    execute_agent.delay(execution.id, datetime.now())

if __name__ == '__main__':
    run_tfagent_cli(agent_name=agent_name, agent_description=agent_description, agent_goals=agent_goals)





