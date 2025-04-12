import json
import os
import time
from arguments import args
from utils import read_json, write_json, extract_json
from task_template import Task3Template
from agent_cli import basic_setting, run_tfagent_cli

from sqlalchemy.orm import sessionmaker
from tfagent.models.db import connect_db

from tfagent.models.organisation import Organisation
from tfagent.models.project import Project
from tfagent.models.agent import Agent
from tfagent.models.user import User
from tfagent.models.agent_execution import AgentExecution
from tfagent.models.agent_execution_feed import AgentExecutionFeed


engine = connect_db()
Session = sessionmaker(bind=engine)

class Task3Handler():
    def __init__(self, args):
        self.args = args
        self.session = Session()
        if not args.no_agent and args.agentname is not None and args.agentname != "":
            self.agent = basic_setting(args, self.session)
        else:
            self.agent = None
    def generate_exp(self, task3_template: Task3Template):
        raw_dataset = read_json(self.args.raw_data_path)
        for raw_item in raw_dataset:
            exp_id_list = []
            prompt_suffix = ""
            for i, item in enumerate(raw_item["Inter_evidence"]):
                # skip the history
                exp_id_list.append(item["ie_id"])
                prompt_suffix = prompt_suffix + "犯罪事实" + str(len(exp_id_list)) + ": " + \
                                    item["Inter"] + "\n" + \
                                    "犯罪证据" + str(len(exp_id_list)) + ": " + \
                                    item["Evidence"] + "\n\n"

                if len(exp_id_list) >= args.task3_pool_num or i + 1 >= len(raw_item["Inter_evidence"]):
                    # skip history
                    if "Exp" in raw_item["Inter_evidence"][exp_id_list[0]] and "Exp" in raw_item["Inter_evidence"][exp_id_list[-1]]\
                            and raw_item["Inter_evidence"][exp_id_list[0]]!="" and raw_item["Inter_evidence"][exp_id_list[-1]]!="":
                        exp_id_list = []
                        continue

                    input_forum = task3_template.get_template("Exp")
                    goals = prompt_suffix
                    input_forum["agent_goals"] = input_forum["agent_goals"].replace("{fact_evidence_text}", goals)
                    args.agent_execution_name = "{}_{}_{}_{}".format(input_forum["agent_name"], raw_item["id"], exp_id_list[0], exp_id_list[-1])
                    run_tfagent_cli(self.session,
                                    self.agent,
                                    self.args.agent_execution_name,
                                    agent_goals=[input_forum["agent_goals"]],
                                    tools_list=input_forum["tool_list"],)
                    time.sleep(30)
                    exp_id_list = []
                    prompt_suffix = ""

        self.session.close()


    def save_exp(self):
        db_user = self.session.query(User).filter(User.email == args.useremail).first()
        organisation = self.session.query(Organisation).filter(Organisation.id == db_user.organisation_id).first()
        project = Project.find_or_create_project(self.session, organisation_id=organisation.id, project_name=args.projectname)
        agent = Agent.get_last_agent_by_project_and_name(self.session, project.id, args.agentname)
        # Read data from the database
        raw_dataset = read_json(self.args.raw_data_path)
        for raw_item in raw_dataset:
            exp_id_list = []
            for i, item in enumerate(raw_item["Inter_evidence"]):
                exp_id_list.append(item["ie_id"])
                if len(exp_id_list) >= args.task3_pool_num or i + 1 >= len(raw_item["Inter_evidence"]):
                    # skip history
                    if ("Exp" in raw_item["Inter_evidence"][exp_id_list[0]]
                            and "Exp" in raw_item["Inter_evidence"][exp_id_list[-1]]):
                        exp_id_list = []
                        continue

                    agent_execution_name = "{}_{}_{}_{}".format(args.agentname, raw_item["id"], exp_id_list[0], exp_id_list[-1])
                    try:
                        agent_execution = AgentExecution.get_agent_execution_by_agent_id_and_name(self.session, agent.id, agent_execution_name)
                        agent_execution_feeds = AgentExecutionFeed.fetch_agent_execution_feeds(self.session, agent_execution.id)
                    except Exception as e:
                        continue
                    for i in range(len(agent_execution_feeds) - 1, -1, -1):
                        agent_execution_feed = agent_execution_feeds[i]
                        if (agent_execution_feed.feed.startswith("Tool " + "UniversalReflectionTool")
                                and "error" not in agent_execution_feed.feed.lower()):
                            try:
                                json_output = extract_json(agent_execution_feed.feed)
                            except Exception as e:
                                continue
                            for i, t in enumerate(exp_id_list):
                                if ("explist" in json_output and i<len(json_output["explist"])
                                        and json_output["explist"][i]["check"]):
                                    raw_item["Inter_evidence"][t]["Exp"] = json_output["explist"][i]["exp"]
                                else:
                                    raw_item["Inter_evidence"][t]["Exp"] = ""
                            break
                    exp_id_list = []
        write_json(raw_dataset, self.args.output_path)
        self.session.close()


def main():
    args.projectname = "Task3 agent"
    task3_template = Task3Template()

    # Extract evidence
    if args.step1:
        args.agentname = task3_template.get_agent_name("Exp")
        args.description = task3_template.get_agent_description("Exp")
        args.max_iterations = task3_template.get_agent_iteration_num("Exp")
        args.knowledge = task3_template.get_agent_knowledge_base("Exp")
        args.raw_data_path = "./dataset/output/output_test_subtask3.json"
        task3_handler = Task3Handler(args)
        task3_handler.generate_exp(task3_template)
    # Save evidence to files and align with raw data
    elif args.step2:
        args.agentname = task3_template.get_agent_name("Exp")
        args.no_agent = True
        args.raw_data_path = "./dataset/output/output_test_subtask3.json"
        args.output_path = "./dataset/output/output_test_subtask3.json"
        task3_handler = Task3Handler(args)
        task3_handler.save_exp()


if __name__ == '__main__':
    main()






