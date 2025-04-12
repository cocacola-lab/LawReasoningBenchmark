import random

from langchain.docstore.document import Document

from utils import readjson, writejson


# seed
random.seed(1)

# save path
traindata_path = "knowledge_rawdata/new_train.json"
# 证据事实抽取的知识库构建
output_pos_evid_path = "knowledge/raw_pos_evid.json"
output_neg_evid_path = "knowledge/raw_neg_evid.json"

def get_pos_evid(dataset):
    ev_list = []
    ev_span_list = []
    count = 0
    for data in dataset:
        data_info = data["Case_info"].split("。")
        for f_id in data["Evidence_link"]:
            for e_span in data["Evidence_link"][f_id]:
                if e_span not in ev_span_list:
                    ev_span_list.append(e_span)
        for ev_span in ev_span_list:
            if data_info[ev_span[0]: ev_span[1]+1] != []:
                ev_list.append({
                    "id": count,
                    "page_content": "。".join(data_info[ev_span[0]: ev_span[1]+1]) + "。",
                    "type": "evidence",
                    "is_type": True,
                })
                count+=1
        ev_span_list = []
    writejson(ev_list, output_pos_evid_path)
    return ev_list

def get_neg_evid(dataset):
    # 定位证据所在的位置
    case_evid_position = []
    for data in dataset:
        evid_position = []
        for f_id in data["Evidence_link"]:
            for e_span in data["Evidence_link"][f_id]:
                if e_span not in evid_position:
                    evid_position.append(e_span)
        case_evid_position.append(evid_position)

    no_evid_list = []
    count = 0
    for data in dataset:
        case_info_list = data["Case_info"].split("。")
        info_list_len = len(case_info_list)
        s_pos = 0
        while s_pos < info_list_len:
            offset = random.randint(1, 4)
            not_evid = True
            for evid_span in case_evid_position[data["id"]]:
                if not (s_pos + offset < evid_span[0] or s_pos > evid_span[1]):
                    not_evid = False
                    break
            if not_evid:
                no_evid_list.append({
                    "id": count,
                    "page_content": "。".join(case_info_list[s_pos:s_pos + offset]) + "。",
                    "type": "evidence",
                    "is_type": False,
                })
                count += 1
            s_pos += offset
        writejson(no_evid_list, output_neg_evid_path)
    return no_evid_list

def convert_jsonlist2docs(json_path):
    raw_documents = readjson(json_path)
    docs = []
    for data in raw_documents:
        docs.append(Document(
            page_content=data["page_content"],
            metadata={
                "type": data["type"],
                "is_type": data["is_type"],
            }
        ))
        # Chroma.from_documents()
    # 制作每一个分割文本的索引，用这个索引做成本地知识库
    return docs

def main():
    dataset = readjson(traindata_path)
    get_pos_evid(dataset)
    get_neg_evid(dataset)


if __name__ == "__main__":
    main()
