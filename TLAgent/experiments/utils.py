import re
import json
import difflib
import pandas as pd

def read_prompt(path):
    with open(path, "r", encoding="utf-8") as f:
        prompt = f.read()
    return prompt

def read_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
def write_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def extract_json(text):
    print(text)
    if "```json" not in text:
        # 使用正则表达式查找 JSON 部分
        pattern = r'{.*}'
        matches = re.findall(pattern, text, re.DOTALL)
    else:
        pattern =  r'```json\n(.*?)\n```'
        matches = re.findall(pattern, text, re.DOTALL)

    if len(matches) > 0:
        json_obj = json.loads(matches[0])
    else:
        json_obj = json.loads(text)

    return json_obj


# string list 去重
def remove_short_strings(lst, min_length=5):
    result = []
    for item in lst:
        if item!= "" and len(item) >= min_length:  # 只添加不为空字符串的元素
            result.append(item)
    return result

# dict list去重
def unique_by_key(list_of_dicts, key):
    temp_dict = []
    temp_list = []
    for d in list_of_dicts:
        if d[key] not in temp_list:
            temp_dict.append(d)
            temp_list.append(d[key])
    return temp_dict

def match_src_sents(source_data, parah):
    # 将段落b分割成句子，这里简单使用句号、感叹号和问号作为分割标志
    # 实际应用中可能需要根据具体情况调整
    sents = parah.split("。")
    if sents[-1] == "":
        del sents[-1]
    source_sents = source_data.split("。")
    offset = len(sents)
    max_similarity = 0
    max_similarity_start = 0
    for start in range(0, len(source_sents)-offset):
        norm_similarity = 0.0
        for src_sent, sent in zip(source_sents[start: start+offset], sents):
            similarity = difflib.SequenceMatcher(None, src_sent, sent).ratio()
            norm_similarity += similarity
        norm_similarity /= offset
        if norm_similarity > max_similarity:
            max_similarity = norm_similarity
            max_similarity_start = start

    return [max_similarity_start, max_similarity_start+offset-1], \
           "。".join(source_sents[max_similarity_start: max_similarity_start+offset])

def match_src_sents_all(source_data, parah):
    # 将段落b分割成句子，这里简单使用句号、感叹号和问号作为分割标志
    # 实际应用中可能需要根据具体情况调整
    sents = parah.split("。")
    if sents[-1] == "":
        del sents[-1]
    source_sents = source_data.split("。")
    offset = len(sents)
    max_similarity = 0
    max_similarity_start = 0

    span_list = []
    sents_list = []

    for start in range(0, len(source_sents)-offset):
        norm_similarity = 0.0
        for src_sent, sent in zip(source_sents[start: start+offset], sents):
            similarity = difflib.SequenceMatcher(None, src_sent, sent).ratio()
            norm_similarity += similarity
        norm_similarity /= offset
        if norm_similarity > max_similarity:
            max_similarity = norm_similarity
            max_similarity_start = start
            if norm_similarity >=0.90:
                span_list.append([max_similarity_start, max_similarity_start+offset-1])
                sents_list.append(
                    "。".join(source_sents[max_similarity_start: max_similarity_start + offset])
                )

    if span_list == [] and sents_list == []:
        span_list.append([max_similarity_start, max_similarity_start+offset-1])
        sents_list.append(
            "。".join(source_sents[max_similarity_start: max_similarity_start + offset])
        )

    return span_list, sents_list

def extract_first_matched_curly_braces(text):
    # Using regular expression to find the first matched set of curly braces
    # This handles nested structures
    stack = []
    start, end = -1, -1

    for i, char in enumerate(text):
        if char == '{':
            stack.append(i)
            if start == -1:
                start = i
        elif char == '}' and stack:
            start = stack.pop()  # Get the position of the matching opening brace
            end = i  # Current position is the closing brace
            if not stack:
                break

    return text[start:end+1] if start != -1 and end != -1 else None
