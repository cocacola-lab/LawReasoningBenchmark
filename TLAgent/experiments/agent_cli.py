from datetime import datetime
from sqlalchemy.orm import sessionmaker

from tfagent.lib.logger import logger
from tfagent.worker import execute_agent
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

from arguments import args


def ask_user_for_goals():
    goals = []
    while True:
        goal = input("Enter a goal (or 'q' to quit): ")
        if goal == 'q':
            break
        goals.append(goal)
    return goals


def basic_setting(args, session):
    # organization
    db_user = session.query(User).filter(User.email == args.useremail).first()
    logger.info(db_user)
    organisation = session.query(Organisation).filter(Organisation.id == db_user.organisation_id).first()
    logger.info(organisation)
    # Find or Create project associated with the organization
    project = Project.find_or_create_project(session, organisation_id=organisation.id, project_name=args.projectname)
    logger.info(project)

    # Agent
    agent_workflow = AgentWorkflow.find_by_name(session=session, name=args.workflow)
    agent = Agent(name=args.agentname, description=args.description, project_id=project.id, agent_workflow_id=agent_workflow.id)
    session.add(agent)
    session.flush()
    session.commit()
    logger.info(agent)

    # Agent Config
    agent_config_values = {
        "agent_type": "Type Non-Queue",
        "constraints": [],
        "instructions": ["None"],
        "exit": "Default",
        "iteration_interval": 0,
        "model": "gpt-4o-mini",
        "permission_type": "Default",
        "LTM_DB": None,
        "memory_window": 10,
        "max_iterations": args.max_iterations if args.max_iterations else None, # 如果是证据事实链接，或者工具比较少的agent，max_iterations=10即可，工具比较多的agent max_iterations=15
        "knowledge": args.knowledge  if args.knowledge else None,
    }

    agent_configurations = [
        AgentConfiguration(agent_id=agent.id, key=key, value=str(value))
        for key, value in agent_config_values.items()
    ]

    session.add_all(agent_configurations)
    session.commit()
    logger.info("Agent Config : ")
    logger.info(agent_configurations)
    return agent

def run_tfagent_cli(session, agent, agent_execution_name=None, agent_goals=None, tools_list=None, ):
    # demo
    # fact finding agent
    # fact finding
    # 请找出instruction文本中的事实,以原文内容返回。

    start_step = AgentWorkflow.fetch_trigger_step_id(session=session,
                                                     workflow_id=agent.agent_workflow_id)

    iteration_step_id = IterationWorkflow.fetch_trigger_step_id(session,
                                                                start_step.id).id if start_step.action_type == "ITERATION_WORKFLOW" else -1

    # Create agent execution in RUNNING state associated with the agent
    execution = AgentExecution(status='RUNNING',
                               agent_id=agent.id,
                               name=agent_execution_name,
                               current_agent_step_id=start_step.id,
                               iteration_workflow_step_id=iteration_step_id, # 如果iteration_workflow_step_id = -1 表示没有
                               last_execution_time=datetime.utcnow())

    session.add(execution)
    session.commit()

    logger.info("Final Execution")
    logger.info(execution)

    # agent execution
    agent_execution_configs = {
        "goal":agent_goals,
        "instruction": eval(AgentConfiguration.get_agent_config_by_key_and_agent_id(session, "instructions", agent.id).value),
        "constraints": eval(AgentConfiguration.get_agent_config_by_key_and_agent_id(session, "constraints", agent.id).value),
        "exit": AgentConfiguration.get_agent_config_by_key_and_agent_id(session, "exit", agent.id).value,
        "tools": tools_list,
        "iteration_interval": AgentConfiguration.get_agent_config_by_key_and_agent_id(session, "iteration_interval", agent.id).value,
        "model": AgentConfiguration.get_agent_config_by_key_and_agent_id(session, "model", agent.id).value,
        "permission_type": AgentConfiguration.get_agent_config_by_key_and_agent_id(session, "permission_type", agent.id).value,
        "LTM_DB": AgentConfiguration.get_agent_config_by_key_and_agent_id(session, "LTM_DB", agent.id).value,
        "max_iterations": AgentConfiguration.get_agent_config_by_key_and_agent_id(session, "max_iterations", agent.id).value,
        "user_timezone": None,
        "knowledge": AgentConfiguration.get_agent_config_by_key_and_agent_id(session, "knowledge", agent.id).value,
    }

    AgentExecutionConfiguration.add_or_update_agent_execution_config(session=session, execution=execution,
                                                                     agent_execution_configs=agent_execution_configs)

    # execute_agent_serial(execution.id, datetime.now())
    execute_agent.delay(execution.id, datetime.now())