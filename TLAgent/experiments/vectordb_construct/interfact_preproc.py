import os, sys
import time
import random

from langchain.docstore.document import Document
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma

from utils import readjson, writejson, match_src_sents

# seed
random.seed(1)

# save path
traindata_path = "knowledge_rawdata/new_train.json"
# 证据事实抽取的知识库构建
output_pos_fact_path = "knowledge/raw_pos_fact.json"
output_neg_fact_path = "knowledge/raw_neg_fact.json"
# output_fact_db = "dataset/db/interfact"

def get_pos_inter(dataset):
    inter_list = []
    count = 0
    for data in dataset:
        for f_id in data["Inter_result"]:
            inter_list.append({
                "id": count,
                "page_content": data["Inter_result"][f_id],
                "type": "interim_fact",
                "is_type": True,
            })
            count+=1

    writejson(inter_list, output_pos_fact_path)
    return inter_list

def get_neg_inter(dataset):
    # 定位事实所在的位置
    case_fact_position = []
    for data in dataset:
        fact_position = []
        for f_id in data["Inter_result"]:
            fact = data["Inter_result"][f_id]
            pos, _ = match_src_sents(data["Case_info"], fact)
            fact_position.append(pos)
        case_fact_position.append(fact_position)

    no_inter_list = []
    count = 0
    for data in dataset:
        case_info_list = data["Case_info"].split("。")
        info_list_len = len(case_info_list)
        s_pos = 0
        while s_pos < info_list_len:
            offset = random.randint(1, 4)
            not_fact = True
            for fact_span in case_fact_position[data["id"]]:
                if not (s_pos + offset < fact_span[0] or s_pos > fact_span[1]):
                    not_fact = False
                    break
            if not_fact:
                no_inter_list.append({
                    "id": count,
                    "page_content": "。".join(case_info_list[s_pos:s_pos + offset]) + "。",
                    "type": "interim_fact",
                    "is_type": False,
                })
                count += 1
            s_pos += offset
        writejson(no_inter_list, output_neg_fact_path)
    return no_inter_list

def main():
    dataset = readjson(traindata_path)
    get_pos_inter(dataset)
    get_neg_inter(dataset)
    # total_docs = []
    # pos_docs = convert_jsonlist2docs(output_pos_fact_path)
    # neg_docs = convert_jsonlist2docs(output_neg_fact_path)
    # total_docs.extend(pos_docs)
    # neg_docs = random.sample(neg_docs, len(pos_docs)*2)
    # total_docs.extend(neg_docs)

if __name__ == "__main__":
    main()





