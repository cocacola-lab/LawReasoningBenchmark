import json
import os
import time
from arguments import args
from utils import read_json, write_json, extract_json, match_src_sents, match_src_sents_all
from task_template import Task2Template
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

class Task2Handler():
    def __init__(self, args,):
        self.args = args
        self.session = Session()
        if not args.no_agent and args.agentname is not None and args.agentname != "":
            self.agent = basic_setting(args, self.session)
        else:
            self.agent = None
    def extract_evids(self, task2_template: Task2Template):
        dataset_list = os.listdir(self.args.input_dir)
        for data_file in dataset_list:
            data_items = read_json(os.path.join(self.args.input_dir, data_file))
            for item in data_items["case_segments"]:
                # skip the history
                if "evids" in item:
                    continue

                input_forum = task2_template.get_template("evid")
                input_forum["agent_goals"] = input_forum["agent_goals"].replace("{legal_text}", item["case_info"])
                self.args.agent_execution_name = "{}_{}_{}".format(input_forum["agent_name"], data_items["id"], item["seg"])
                run_tfagent_cli(self.session,
                                self.agent,
                                self.args.agent_execution_name,
                                agent_goals=[input_forum["agent_goals"]],
                                tools_list=input_forum["tool_list"])
                time.sleep(25)

        self.session.close()

    def save_evids(self):
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
                # if "evids" in item:
                #     continue
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
                            evid_result_list = []
                            for evid in json_output["evidence"]:
                                evid_result_list.append(evid["text"])
                            item["evids"] = evid_result_list
                        except Exception as e:
                            continue
                        break

            write_json(data_items, os.path.join(args.input_dir, data_file))
        self.session.close()

    def merge_evids(self):
        dataset_list = os.listdir(self.args.input_dir)
        raw_dataset = read_json(self.args.raw_data_path)
        raw_id_dict = {}
        for i, raw_item in enumerate(raw_dataset):
            raw_id_dict[raw_item["id"]] = i

        for data_file in dataset_list:
            data_items = read_json(os.path.join(self.args.input_dir, data_file))
            evid_results = []
            for item in data_items["case_segments"]:
                if "evids" in item:
                    if self.args.task2_match_src:
                        temp_match = []
                        for src_sent in item["evids"]:
                            _, match_text = match_src_sents(item["case_info"], src_sent)
                            temp_match.append(match_text)
                        evid_results.extend(temp_match)

            if self.args.task2_remove_duplicate:
                temp_match = []
                for item in evid_results:
                    if item not in temp_match:
                        temp_match.append(item)
                evid_results = temp_match

            raw_dataset[raw_id_dict[data_items["id"]]]["evids"] = evid_results

        write_json(raw_dataset, self.args.output_path)

    def split_inter_and_evids(self):
        evids_dataset = read_json(self.args.output_path)
        inter_dataset = read_json(self.args.raw_data_path)
        raw_id_dict = {}
        for i, raw_item in enumerate(inter_dataset):
            raw_id_dict[raw_item["id"]] = i

        output_dataset = []
        for data in inter_dataset:
            output_dataset.append({
                "id": data["id"],
                "split": [],
            })

        for inter_item in inter_dataset:
            item = output_dataset[raw_id_dict[inter_item["id"]]]
            inter_dict_list = inter_item["Inter_result"]
            inter_list = []
            inter_id_list = []
            for fact_id, inter in inter_dict_list.items():
                inter_id_list.append(fact_id)
                inter_list.append(inter)

            evids_span_total = []
            evids_sents_total = []
            for evid in evids_dataset[raw_id_dict[inter_item["id"]]]["evids"]:
                span_list, sents_list = match_src_sents_all(inter_dataset[raw_id_dict[inter_item["id"]]]["Case_info"], evid)
                for span, sents in zip(span_list, sents_list):
                    if span in evids_span_total:
                        continue

                    evids_span_total.append(span)
                    evids_sents_total.append(sents)

            split_counter = 0

            for fact_id, inter in zip(inter_id_list, inter_list):
                span_pool = []
                evid_pool = []
                for span, sents in zip(evids_span_total, evids_sents_total):
                    span_pool.append(span)
                    evid_pool.append(sents)

                    if len(span_pool) >= args.task2_pool_num:
                        evids_split = json.dumps(evid_pool, ensure_ascii=False)
                        item["split"].append(
                            {
                                "id": split_counter,
                                "fact": inter,
                                "fact_id": fact_id,
                                "evids": evids_split,
                                "evids_span": span_pool
                            }
                        )
                        span_pool = []
                        evid_pool = []
                        split_counter += 1

                if len(span_pool) > 0:
                    evids_split = json.dumps(evid_pool, ensure_ascii=False)
                    item["split"].append(
                        {
                            "id": split_counter,
                            "fact": inter,
                            "fact_id": fact_id,
                            "evids": evids_split,
                            "evids_span": span_pool
                        }
                    )
        write_json(output_dataset, self.args.evids_split_path)

    def evids_link(self, task2_template: Task2Template):
        evids_split_dataset = read_json(self.args.evids_split_path)

        for raw_item in evids_split_dataset:
            for item in raw_item["split"]:

                input_forum = task2_template.get_template("link")
                criminal_fact = item["fact"]
                criminal_evid = item["evids"]
                input_forum["agent_goals"] = (input_forum["agent_goals"].replace("{criminal_fact}", criminal_fact).
                                              replace("{criminal_evidence}", criminal_evid))

                args.agent_execution_name = "{}_{}_{}".format(input_forum["agent_name"], raw_item["id"], item["id"])
                run_tfagent_cli(self.session,
                                self.agent,
                                self.args.agent_execution_name,
                                agent_goals=[input_forum["agent_goals"]],
                                tools_list=input_forum["tool_list"], )
                time.sleep(25)
        self.session.close()

    def save_link(self):
        db_user = self.session.query(User).filter(User.email == args.useremail).first()
        organisation = self.session.query(Organisation).filter(Organisation.id == db_user.organisation_id).first()
        project = Project.find_or_create_project(self.session, organisation_id=organisation.id, project_name=args.projectname)
        agent = Agent.get_last_agent_by_project_and_name(self.session, project.id, args.agentname)
        agent = Agent.get_agent_from_id(self.session, agent_id=agent.id)
        # 从数据库中读取数据
        evid_split_dataset = read_json(self.args.evids_split_path)
        raw_dataset = read_json(self.args.raw_data_path)

        raw_id_dict = {}
        for i, raw_item in enumerate(raw_dataset):
            raw_id_dict[raw_item["id"]] = i

        for raw_item in evid_split_dataset:
            evid_links = []
            evid_dict2pos = {}

            for f_id, fact_key in enumerate(raw_dataset[raw_id_dict[raw_item["id"]]]["Inter_result"].keys()):
                evid_dict2pos[fact_key] = len(evid_links)
                evid_links.append(
                    {
                        fact_key: []
                    }
                )
            # 将历史链接数据加入
            if "Evidence_link" in raw_dataset[raw_id_dict[raw_item["id"]]]:
                evid_links = raw_dataset[raw_id_dict[raw_item["id"]]]["Evidence_link"]

            for item in raw_item["split"]:
                # skip the history
                agent_execution_name = "{}_{}_{}".format(args.agentname, raw_item["id"], item["id"])
                try:
                    agent_execution = AgentExecution.get_agent_execution_by_agent_id_and_name(self.session, agent.id, agent_execution_name)
                    agent_execution_feeds = AgentExecutionFeed.fetch_agent_execution_feeds(self.session, agent_execution.id)
                except Exception:
                    continue
                for i in range(len(agent_execution_feeds) - 1, -1, -1):
                    agent_execution_feed = agent_execution_feeds[i]
                    if (agent_execution_feed.feed.startswith("Tool " + "UniversalReflectionTool")
                            and "error" not in agent_execution_feed.feed.lower()):
                        try:
                            json_output = extract_json(agent_execution_feed.feed)
                        except Exception:
                            continue
                        if "checklist" not in json_output:
                            continue
                        for t, check in enumerate(json_output["checklist"]):
                            if (check["check"] and t < len(item["evids_span"])
                                    and item["evids_span"][t] not in evid_links[evid_dict2pos[item["fact_id"]]][item["fact_id"]]):
                                temp = evid_links[evid_dict2pos[item["fact_id"]]][item["fact_id"]]
                                temp.append(item["evids_span"][t])
                                evid_links[evid_dict2pos[item["fact_id"]]][item["fact_id"]] = temp
                        break

            raw_dataset[raw_id_dict[raw_item["id"]]]["Evidence_link"] = evid_links

        write_json(raw_dataset, args.output_path)
        self.session.close()

def main():
    args.projectname = "Task2 agent"
    task2_template = Task2Template()

    # Extract evidence
    if args.step1:
        args.agentname = task2_template.get_agent_name("Evid")
        args.description = task2_template.get_agent_description("Evid")
        args.knowledge = task2_template.get_agent_knowledge_base("Evid")
        args.max_iterations = task2_template.get_agent_iteration_num("Evid")
        args.input_dir = "./dataset/splitdata/task2"
        task2_handler = Task2Handler(args,)
        task2_handler.extract_evids(task2_template)
    # Save evidence to files and align with raw data
    elif args.step2:
        args.agentname = task2_template.get_agent_name("Evid")
        args.no_agent = True
        args.input_dir = "./dataset/splitdata/task2"
        task2_handler = Task2Handler(args)
        task2_handler.save_evids()

    # Merge evidence into the evidence file
    elif args.step3:
        args.agentname = task2_template.get_agent_name("Evid")
        args.no_agent = True
        args.input_dir = "./dataset/splitdata/task2"
        args.raw_data_path = "./dataset/task2/test_subtask2_input.json"
        args.output_path = "./dataset/output/output_test_subtask2evids.json"
        task2_handler = Task2Handler(args)
        task2_handler.merge_evids()
    # Build the evidence and fact linking dataset
    elif args.step4:
        args.no_agent = True
        args.raw_data_path = "./dataset/task2/test_subtask2_input.json"
        args.output_path = "./dataset/output/output_test_subtask2evids.json"
        args.evids_split_path = "./dataset/output/output_test_subtask2linksplit.json"
        task2_handler = Task2Handler(args)
        task2_handler.split_inter_and_evids()
    # Link evidence and facts
    elif args.step5:
        args.agentname = task2_template.get_agent_name("link")
        args.knowledge = task2_template.get_agent_knowledge_base("link")
        args.description = task2_template.get_agent_description("link")
        args.max_iterations = task2_template.get_agent_iteration_num("link")
        args.evids_split_path = "./dataset/output/output_test_subtask2linksplit.json"
        task2_handler = Task2Handler(args,)
        task2_handler.evids_link(task2_template)
    # Save the linked results to files
    elif args.step6:
        args.agentname = task2_template.get_agent_name("link")
        args.no_agent = True
        args.raw_data_path = "./dataset/output/output_test_subtask2.json"
        args.evids_split_path = "./dataset/output/output_test_subtask2linksplit.json"
        args.output_path = "./dataset/output/output_test_subtask2.json"
        task2_handler = Task2Handler(args)
        task2_handler.save_link()

if __name__ == '__main__':
    main()






