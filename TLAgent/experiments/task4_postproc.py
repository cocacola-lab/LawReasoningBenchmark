import os, sys
import json

from utils import read_json, write_json

input_file_path = "./dataset/output/output_test_subtask4.json"
output_file_path = "dataset_ab/output_ab/ab_all/output_test_subtask4_compre_ab.json"
os.chdir(sys.path[0])


def find_id(value, dict):
    for i in dict:
        if dict[i] == value:
            return i
    return "error"


def to_compre(case, id):
    cased = {}

    node = []
    relation = []

    sents = case["Case_info"].split("。")

    final_result = {}
    final_result["node-id"] = "FR001"
    final_result["node-type"] = "Final_result"
    final_result["info"] = case["Final_result"]
    node.append(final_result)

    evidence = []
    evi_id = 0
    evi_id_dict = {}
    for i, v in enumerate(case["Evidence_link"]):
        key_id = list(v.keys())[0]
        for it in v[key_id]:

            if it not in evidence:
                evidence.append(it)
            else:
                continue

    for i in evidence:
        start = i[0]
        end = i[1]
        evi = {}
        evi["node-id"] = "Evi" + str(evi_id)
        evi["node-type"] = "Evidence"
        evi_id_dict[evi["node-id"]] = i
        evid = sents[start:end + 1]
        evid = '。'.join(map(str, evid))
        evi["info"] = evid
        evi_id += 1
        node.append(evi)


    inter_dict = {}
    inter_id = 0
    for i in case["Inter_result"]:
        inter = {}
        inter["node-id"] = "Inter" + str(inter_id)
        inter["node-type"] = "Inter_result"
        inter["info"] = case["Inter_result"][i]
        inter_dict[inter["node-id"]] = str(inter_id)
        inter_id += 1
        node.append(inter)

    relation_id = 0
    for i, v in enumerate(case["Evidence_link"]):
        key_id = list(v.keys())[0]
        for e in v[key_id]:
            rela = {}
            rela["relation-id"] = "ZDS" + str(relation_id)
            rela["from-id"] = find_id(e, evi_id_dict)
            rela["to-id"] = "Inter" + str(i)
            if rela["from-id"] == "error":
                print("error")
            rela["exp-type"] = "no"
            rela["exp"] = ""
            if "Exp" in case["Inter_evidence"][relation_id]:
                exp = case["Inter_evidence"][relation_id]["Exp"]
                if exp and exp != "":
                    rela["exp-type"] = "yes"
                    rela["exp"] = exp

                relation.append(rela)
                relation_id += 1

    cased["id"] = id
    cased["node"] = node
    cased["relation"] = relation

    print(f"The postproc of case {id} done!")
    return cased


def handle_data(data_list):
    results = []
    for case in data_list:
        id = case["id"]
        results.append(to_compre(case, id))
    return results

def main():
    results = []
    whole = read_json(input_file_path)
    for case in whole:
        id = case["id"]
        results.append(to_compre(case, id))
    write_json(results, output_file_path)


if __name__ == '__main__':
    main()


