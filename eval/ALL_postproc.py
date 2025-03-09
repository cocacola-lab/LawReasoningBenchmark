import sys
import json

input_file_path = sys.argv[1]
output_file_path = sys.argv[2]

def find_id(value, dict):  # 按值找键
    for i in dict:
        if dict[i] == value:
            return i
    return "error"

def read_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
def write_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def to_compre(case, id):
    cased = {}

    node = []
    relation = []

    sents = case["Case_info"].split("。")

    # node 最终事实
    final_result = {}
    final_result["node-id"] = "FR001"
    final_result["node-type"] = "Final_result"
    final_result["info"] = case["Final_result"]
    node.append(final_result)

    # node 证据
    # 证据列表
    evidence = []
    evi_id = 0
    # 证据坐标与id的对应字典，方便关系检索
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

    # node 中间事实
    # 中间事实索引与id的对应字典
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

    # relation 证据到中间事实
    relation_id = 0
    for i, v in enumerate(case["Evidence_link"]):
        key_id = list(v.keys())[0]
        for e in v[key_id]:
            rela = {}
            rela["relation-id"] = "ZDS" + str(relation_id)
            # 检索证据e的id
            rela["from-id"] = find_id(e, evi_id_dict)
            # i的id
            rela["to-id"] = "Inter" + str(i)
            if rela["from-id"] == "error":
                print("error")
            # 检索Experiences
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


