import json
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