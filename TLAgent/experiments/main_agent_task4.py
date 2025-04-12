import json
import os
import time
from arguments import args
from utils import read_json, write_json
from task_template import Task2Template, Task3Template
from main_agent_task2 import Task2Handler
from main_agent_task3 import Task3Handler

class Task4Handler():
    def __init__(self, args, agent=None,):
        self.args = args
    def labelinter2id(self, ):
        def func(data):
            data_reformat = {}
            # Starting code
            # start_code = "AX000"
            # Extracting the prefix (AX) and starting number (000)
            prefix = "AX"
            # start_number = int(start_code[2:])

            for i, d in enumerate(data["Inter_result"]):
                data_reformat["{}{}".format(prefix, str(i).zfill(3))] = d
            data["Inter_result"] = data_reformat
            return data

        dataset = read_json(self.args.raw_data_path)
        for i, data in enumerate(dataset):
            if not isinstance(data["Inter_result"], dict):
                data = func(data)
        write_json(dataset, self.args.output_path)

    def interevi2expformat(self,):
        def func(data):
            data["Inter_evidence"] = []
            data_info = data["Case_info"].split("。")
            count = 0
            for i_id in data["Inter_result"]:
                for evis in data["Evidence_link"]:
                    for f_id in evis:
                        if f_id == i_id:
                            for evi in evis[f_id]:
                                data["Inter_evidence"].append({
                                    "ie_id": count,
                                    "Inter": data["Inter_result"][i_id],
                                    "Evidence": "。".join(data_info[evi[0]: evi[1]+1]),
                                })
                                count += 1
            return data

        dataset = read_json(self.args.raw_data_path)
        for i, data in enumerate(dataset):
            data = func(data)
        write_json(dataset, self.args.output_path)

def main():
    args.projectname = "Task4 agent"
    task2_template = Task2Template()
    task3_template = Task3Template()

    # Convert the Inter_result format to the original data format
    if args.step1:
        args.raw_data_path = "./dataset/output/output_test_subtask1.json"
        args.output_path = "./dataset/output/output_test_subtask4.json"
        args.no_agent = True
        task4_handler = Task4Handler(args)
        task4_handler.labelinter2id()
    # Build the evidence and fact linking dataset
    if args.step2:
        args.raw_data_path = "./dataset/output/output_test_subtask4.json"
        args.output_path = "./dataset/output/output_test_subtask2evids.json"
        args.evids_split_path = "./dataset/output/output_test_subtask4linksplit.json"
        args.no_agent = True
        task2_handler = Task2Handler(args)
        task2_handler.split_inter_and_evids()
    # Link evidence and facts
    elif args.step3:
        args.agentname = task2_template.get_agent_name("link")
        args.knowledge = task2_template.get_agent_knowledge_base("link")
        args.description = task2_template.get_agent_description("link")
        args.max_iterations = task2_template.get_agent_iteration_num("link")
        args.evids_split_path = "./dataset/output/output_test_subtask4linksplit.json"
        task2_handler = Task2Handler(args)
        task2_handler.evids_link(task2_template)
    # Save the linked results to files
    elif args.step4:
        args.agentname = task2_template.get_agent_name("link")
        args.no_agent = True
        args.raw_data_path = "./dataset/output/output_test_subtask4.json"
        args.evids_split_path = "./dataset/output/output_test_subtask4linksplit.json"
        args.output_path = "./dataset/output/output_test_subtask4.json"
        task2_handler = Task2Handler(args)
        task2_handler.save_link()
    # Convert the evidence and fact files to match the original format
    elif args.step5:
        args.raw_data_path = "./dataset/output/output_test_subtask4.json"
        args.output_path = "./dataset/output/output_test_subtask4.json"
        task4_handler = Task4Handler(args)
        task4_handler.interevi2expformat()
    # Generate experience
    elif args.step6:
        args.agentname = task3_template.get_agent_name("Exp")
        args.description = task3_template.get_agent_description("Exp")
        args.max_iterations = task3_template.get_agent_iteration_num("Exp")
        args.knowledge = task3_template.get_agent_knowledge_base("Exp")
        args.raw_data_path = "./dataset/output/output_test_subtask4.json"
        task3_handler = Task3Handler(args)
        task3_handler.generate_exp(task3_template)
    # Save experience
    elif args.step7:
        args.agentname = task3_template.get_agent_name("Exp")
        args.no_agent = True
        args.raw_data_path = "./dataset/output/output_test_subtask4.json"
        args.output_path = "./dataset/output/output_test_subtask4.json"
        task2_handler = Task3Handler(args)
        task2_handler.save_exp()


if __name__ == '__main__':
    main()






