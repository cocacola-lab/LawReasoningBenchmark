import os
import time
from arguments import args
from utils import read_json, write_json, extract_json, match_src_sents
from task_template import Task1Template
from agent_cli import basic_setting, run_tfagent_cli

from sqlalchemy.orm import sessionmaker
from tfagent.models.db import connect_db

from tfagent.models.organisation import Organisation
from tfagent.models.project import Project
from tfagent.models.agent import Agent
from tfagent.models.user import User
from tfagent.models.agent_execution import AgentExecution
from tfagent.models.agent_execution_feed import AgentExecutionFeed
from tfagent.models.workflows.agent_workflow import AgentWorkflow
from tfagent.models.workflows.iteration_workflow import IterationWorkflow

engine = connect_db()
Session = sessionmaker(bind=engine)

class Task1Handler():
    def __init__(self, args):
        self.args = args
        self.session = Session()
        if not args.no_agent and args.agentname is not None and args.agentname != "":
            self.agent = basic_setting(args, self.session)
        else:
            self.agent = None
    def extract_inter(self, task1_template: Task1Template):
        dataset_list = os.listdir(self.args.input_dir)
        for data_file in dataset_list:
            data_items = read_json(os.path.join(self.args.input_dir, data_file))
            for item in data_items["case_segments"]:
                # skip the history
                if "Inter_result" in item:
                    continue
                input_forum = task1_template.get_template("fact")
                input_forum["agent_goals"] = input_forum["agent_goals"].replace("{legal_text}", item["case_info"])
                args.agent_execution_name = "{}_{}_{}".format(input_forum["agent_name"], data_items["id"], item["seg"])
                run_tfagent_cli(self.session,
                                self.agent,
                                self.args.agent_execution_name,
                                agent_goals=[input_forum["agent_goals"]],
                                tools_list=input_forum["tool_list"])
                time.sleep(30)
        self.session.close()

    def save_inter(self):
        db_user = self.session.query(User).filter(User.email == args.useremail).first()
        organisation = self.session.query(Organisation).filter(Organisation.id == db_user.organisation_id).first()
        project = Project.find_or_create_project(self.session, organisation_id=organisation.id, project_name=args.projectname)
        agent = Agent.get_last_agent_by_project_and_name(self.session, project.id, args.agentname)
        # 从数据库中读取数据
        dataset_list = os.listdir(args.input_dir)
        for data_file in dataset_list:
            data_items = read_json(os.path.join(args.input_dir, data_file))
            for item in data_items["case_segments"]:
                # skip the history
                if "Inter_result" in item:
                    continue
                agent_execution_name = "{}_{}_{}".format(args.agentname, data_items["id"], item["seg"])
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
                            Inter_result_list = []
                            if json_output != {}:
                                for fact in json_output["fact"]:
                                    Inter_result_list.append(fact["text"])
                                item["Inter_result"] = Inter_result_list
                                break
                        except Exception as e:
                            continue
            write_json(data_items, os.path.join(args.input_dir, data_file))
        self.session.close()

    def merge_inter(self):
        dataset_list = os.listdir(self.args.input_dir)
        raw_dataset = read_json(self.args.raw_data_path)
        raw_id_dict = {}
        for i, raw_item in enumerate(raw_dataset):
            raw_id_dict[raw_item["id"]] = i

        for data_file in dataset_list:
            data_items = read_json(os.path.join(self.args.input_dir, data_file))
            Inter_results = []
            for item in data_items["case_segments"]:
                if "Inter_result" in item:
                    if self.args.task1_match_src:
                        temp_match = []
                        for src_sent in item["Inter_result"]:
                            _, match_text = match_src_sents(item["case_info"], src_sent)
                            temp_match.append(match_text)
                        item["Inter_result"] = temp_match
                    if self.args.task1_remove_duplicate:
                        temp_match = []
                        for src_sent in item["Inter_result"]:
                            if src_sent not in temp_match:
                                temp_match.append(src_sent)
                        item["Inter_result"] = temp_match
                    Inter_results.extend(item["Inter_result"])

            raw_dataset[raw_id_dict[data_items["id"]]]["Inter_result"] = Inter_results

        write_json(raw_dataset, self.args.output_path)

    def predict_final(self, task1_template: Task1Template):
        raw_dataset = read_json(self.args.output_path)
        for raw_item in raw_dataset:
            # skip the history
            if "Final_result" in raw_item:
                continue

            input_forum = task1_template.get_template("final")
            goals = ("。".join(raw_item["Inter_result"]))[:args.max_seg_length]
            input_forum["agent_goals"] = input_forum["agent_goals"].replace("{legal_text}", goals)
            args.agent_execution_name = "{}_{}".format(input_forum["agent_name"], raw_item["id"])
            run_tfagent_cli(self.session,
                            self.agent,
                            self.args.agent_execution_name,
                            agent_goals=[input_forum["agent_goals"]],
                            tools_list=input_forum["tool_list"],)

            time.sleep(30)
        self.session.close()


    def save_final(self):
        db_user = self.session.query(User).filter(User.email == args.useremail).first()
        organisation = self.session.query(Organisation).filter(Organisation.id == db_user.organisation_id).first()
        project = Project.find_or_create_project(self.session, organisation_id=organisation.id, project_name=args.projectname)
        agent = Agent.get_last_agent_by_project_and_name(self.session, project.id, args.agentname)
        # 从数据库中读取数据
        raw_dataset = read_json(self.args.output_path)
        for raw_item in raw_dataset:
            # skip the history
            if "Final_result" in raw_item:
                continue
            agent_execution_name = "{}_{}".format(args.agentname, raw_item["id"])
            agent_execution = AgentExecution.get_agent_execution_by_agent_id_and_name(self.session, agent.id, agent_execution_name)
            agent_execution_feeds = AgentExecutionFeed.fetch_agent_execution_feeds(self.session, agent_execution.id)
            for i in range(len(agent_execution_feeds) - 1, -1, -1):
                agent_execution_feed = agent_execution_feeds[i]
                if (agent_execution_feed.feed.startswith("Tool " + "FinalDecisionHeadTool")
                        and "error" not in agent_execution_feed.feed.lower()):
                    try:
                        json_output = extract_json(agent_execution_feed.feed)
                    except Exception as e:
                        json_output = agent_execution_feed.feed

                    if isinstance(json_output, dict):
                        if "properties" in json_output:
                            json_output = json_output["properties"]
                        if "value" in json_output["finalfact"]:
                            json_output["finalfact"] = json_output["finalfact"]["value"]
                        raw_item["Final_result"] = json_output["finalfact"]
                    else:
                        raw_item["Final_result"] = json_output
                    break

        write_json(raw_dataset, args.output_path)
        self.session.close()


def main():
    args.projectname = "Task1 agent"
    task1_template = Task1Template()

    # 生成中间事实
    if args.step1:
        args.agentname = task1_template.get_agent_name("Fact")
        args.description = task1_template.get_agent_description("Fact")
        args.knowledge = task1_template.get_agent_knowledge_base("Fact")
        args.max_iterations = task1_template.get_agent_iteration_num("Fact")
        task1_handler = Task1Handler(args)
        task1_handler.extract_inter(task1_template)
    # 将中间事实存入文件
    elif args.step2:
        args.agentname = task1_template.get_agent_name("Fact")
        args.no_agent = True
        task1_handler = Task1Handler(args)
        task1_handler.save_inter()
    # 将分开的中间事实输入到原始结果文件。
    elif args.step3:
        task1_handler = Task1Handler(args)
        args.no_agent = True
        task1_handler.merge_inter()
    # 根据中间事实生成最终犯罪事实。
    elif args.step4:
        args.agentname = task1_template.get_agent_name("Final")
        args.knowledge = task1_template.get_agent_knowledge_base("Final")
        args.max_iterations = task1_template.get_agent_iteration_num("Final")
        task1_handler = Task1Handler(args)
        task1_handler.predict_final(task1_template)
    # 将最终事实存入结果文件。
    elif args.step5:
        args.agentname = task1_template.get_agent_name("Final")
        args.no_agent = True
        task1_handler = Task1Handler(args)
        task1_handler.save_final()


if __name__ == '__main__':
    main()






