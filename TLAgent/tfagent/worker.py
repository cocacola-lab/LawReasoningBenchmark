from __future__ import absolute_import
import os, sys

from sqlalchemy.orm import sessionmaker

from tfagent.helper.tool_helper import handle_tools_import
from tfagent.lib.logger import logger

from datetime import timedelta
from celery import Celery

from tfagent.config.config import get_config


#redis configuration
redis_url = get_config('REDIS_URL', 'super__redis:6379')

app = Celery("tfagent", include=["tfagent.worker"], imports=["tfagent.worker"])
app.conf.broker_url = "redis://" + redis_url + "/0"
app.conf.result_backend = "redis://" + redis_url + "/0"
app.conf.worker_concurrency = 10
app.conf.accept_content = ['application/x-python-serialize', 'application/json']

beat_schedule = {
    'initialize-schedule-agent': {
        'task': 'initialize-schedule-agent',
        'schedule': timedelta(minutes=5),
    },
    'execute_waiting_workflows': {
        'task': 'execute_waiting_workflows',
        'schedule': timedelta(minutes=2),
    },
}
app.conf.beat_schedule = beat_schedule

# # 使用redis异步运行
@app.task(name="execute_agent", autoretry_for=(Exception,), retry_backoff=2, max_retries=5)
def execute_agent(agent_execution_id: int, time):
    """Execute an agent step in background."""
    from tfagent.jobs.agent_executor import AgentExecutor
    handle_tools_import()
    logger.info("Execute agent:" + str(time) + "," + str(agent_execution_id))

    AgentExecutor().execute_next_step(agent_execution_id=agent_execution_id)

# def execute_agent_serial(agent_execution_id: int, time):
#     """Execute an agent step in background."""
#     from tfagent.jobs.agent_executor import AgentExecutor
#     handle_tools_import()
#     logger.info("Execute agent:" + str(time) + "," + str(agent_execution_id))
#     AgentExecutor().execute_next_step(agent_execution_id=agent_execution_id)


