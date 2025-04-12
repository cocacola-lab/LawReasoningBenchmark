import json
import re
import difflib

def readprompt(path):
    with open(path, "r", encoding="utf-8") as f:
        prompt = f.read()
    return prompt

def readjson(path):
    with open(path, 'r', encoding="utf-8") as f:
        str = f.read()
        data_info_list = json.loads(str)
    return data_info_list

def writejson(dataset, path):
    with open(path, 'w', encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False)

def writevocab(dataset, path):
    with open(path, 'w', encoding="utf-8") as f:
        if isinstance(dataset, dict):
            for word, freq in dataset.items():
                if not isinstance(freq, str):
                    freq = str(freq)
                f.write(word + "\t" + freq + "\n")
        else:
            print("输入的数据集类型错误")


def extract_json_content(text):
    # 匹配1到3个反引号，后面跟着"json"和任意数量的空白字符，然后是任意文本，最后是1到3个反引号
    # pattern = r'```json\s*(\{.*?\})\s*```'
    pattern = r'\[([^\]]*?)\]'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1)
    return None

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

def match_src_sents(source_data, parah):
    # 将段落b分割成句子，这里简单使用句号、感叹号和问号作为分割标志
    # 实际应用中可能需要根据具体情况调整
    sents = parah.split("。")
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
            if max_similarity >=0.90:
                break

    return [max_similarity_start, max_similarity_start+offset-1], \
           "。".join(source_sents[max_similarity_start: max_similarity_start+offset])