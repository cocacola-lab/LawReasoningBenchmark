from rouge import Rouge
import json
import jieba
import numpy as np

def load_json(path):
    with open(path, 'r') as f:
        str = f.read()
        data = json.loads(str)
    return data

class WeightedRougeScore():
    def __init__(self, ratio=None):
        if ratio is None:
            ratio = [0.2, 0.3, 0.5]
        self.ratio = ratio
        assert self.ratio[0] + self.ratio[1] + self.ratio[2] == 1.0
        self.rouge = Rouge()

    def calculate_rouge_score(self, pred_txt, ref_txt):
        pred_info = ' '.join(jieba.cut(pred_txt))
        ref_info = ' '.join(jieba.cut(ref_txt))
        rouge_scores = self.rouge.get_scores(pred_info, ref_info, avg=True)
        weighted_score = self.ratio[0] * rouge_scores["rouge-1"]["f"] + \
                         self.ratio[1] * rouge_scores["rouge-2"]["f"] + \
                         self.ratio[2] * rouge_scores["rouge-l"]["f"]
        return  weighted_score

    def get_rouge_1(self, pred_txt, ref_txt):
        pred_info = ' '.join(jieba.cut(pred_txt))
        ref_info = ' '.join(jieba.cut(ref_txt))
        rouge_scores = self.rouge.get_scores(pred_info, ref_info, avg=True)
        return rouge_scores["rouge-1"]["f"]

    def get_rouge_2(self, pred_txt, ref_txt):
        pred_info = ' '.join(jieba.cut(pred_txt))
        ref_info = ' '.join(jieba.cut(ref_txt))
        rouge_scores = self.rouge.get_scores(pred_info, ref_info, avg=True)
        return rouge_scores["rouge-2"]["f"]

    def get_rouge_l(self, pred_txt, ref_txt):
        pred_info = ' '.join(jieba.cut(pred_txt))
        ref_info = ' '.join(jieba.cut(ref_txt))
        rouge_scores = self.rouge.get_scores(pred_info, ref_info, avg=True)
        return rouge_scores["rouge-l"]["f"]

def inter_result_metric_common(matrix: np.array):
    return np.sum(np.max(matrix, axis=1)) / np.max(matrix.shape)

def flink_to_rlink_score(pred_tree, ref_tree, rouge):
    p_node_id = {}
    r_node_id = {}
    for i, p_node in enumerate(pred_tree["node"]):
        p_node_id[p_node["node-id"]] = i
    for i, r_node in enumerate(ref_tree["node"]):
        r_node_id[r_node["node-id"]] = i

    total_relation_rouge = 0
    for i, p_rel in enumerate(pred_tree["relation"]):
        max_relation_rouge = 0
        max_index = -1
        for j, r_rel in enumerate(ref_tree["relation"]):
            temp_rouge = 0
            temp_rouge += rouge.calculate_rouge_score(pred_tree["node"][p_node_id[p_rel["from-id"]]]["info"],
                                                      ref_tree["node"][r_node_id[r_rel["from-id"]]]["info"])

            temp_rouge += rouge.calculate_rouge_score(pred_tree["node"][p_node_id[p_rel["to-id"]]]["info"],
                                                      ref_tree["node"][r_node_id[r_rel["to-id"]]]["info"])
            if max_relation_rouge < temp_rouge:
                max_relation_rouge = temp_rouge
                max_index = j

        if max_index != -1:
            total_relation_rouge += max_relation_rouge
            if ref_tree["relation"][max_index]["exp"]!= "" and pred_tree["relation"][i]["exp"]!= "":
                total_relation_rouge += rouge.calculate_rouge_score(pred_tree["relation"][i]["exp"],
                                                    ref_tree["relation"][max_index]["exp"])
            elif ref_tree["relation"][max_index]["exp"] == "" and pred_tree["relation"][i]["exp"]== "":
                total_relation_rouge += 1

    norm_relation_rouge = total_relation_rouge / (3*max(len(ref_tree["relation"]), len(pred_tree["relation"])))
    return norm_relation_rouge


def reasoning_tree_metric_common(pred_tree, ref_tree):
    rouge = WeightedRougeScore()
    rouge_score = flink_to_rlink_score(pred_tree, ref_tree, rouge=rouge)
    return {
        "weighted-rouge-score": rouge_score,
    }


