import sys
import numpy as np
import argparse

from rouge import Rouge
from metric import reasoning_tree_metric_common, WeightedRougeScore, inter_result_metric_common
from metric import load_json
import jieba
import logging

sys.setrecursionlimit(10000)  # Set to the maximum depth you need

jieba.setLogLevel(logging.INFO) # Turn off jieba log output

def args_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ref", default="/path/to/ref-file", type=str,
                        help="reference jsonfile")
    parser.add_argument("--pred", default="/path/to/pred-file", type=str,
                        help="prediction jsonfile")
    parser.add_argument("--tid", default="task1", type=str, choices=["task1", "task2", "task3", "ALL"],
                    help="prediction jsonfile")
    args = parser.parse_args()
    return args

def dict_to_list(input_dict):
    input_list = []
    for key in input_dict:
        input_list.append(input_dict[key])
    return input_list

def func_f1(ref, gen):
    return len([i for i in gen if i in ref])

class Metric():
    final_key = "Final_result"
    exp_key = "Inter_evidence"
    inter_key = "Inter_result"
    evid_key = "Evidence_link"

    def __init__(self, args):
        """
        load ref and pred file
        :param args: input arguments
        """
        ref_filename = args.ref
        pred_filename = args.pred
        self.ref = load_json(ref_filename)
        self.pred = load_json(pred_filename)

    def extract_key_val(self, jsonfile, key):
        re_dict = []
        count = 0
        for item in jsonfile:
            re_dict.append({
                    "id": item['id'],
                    key: item[key],
                })
            count += 1
        return re_dict

    # Interim probandum metric (Rouge)
    def inter_metric(self,):
        refs = self.extract_key_val(self.ref[:97], self.inter_key)
        preds = self.extract_key_val(self.pred[:97], self.inter_key)
        total_weight1 = 0
        total_weight2 = 0
        total_weightl = 0
        for ref, pred in zip(refs, preds):
            ref = ref["Inter_result"]
            if isinstance(ref, dict):
                ref = dict_to_list(ref)

            pred = pred["Inter_result"]
            if isinstance(pred, dict):
                pred = dict_to_list(pred)
            # Calculate Rouge matrix
            rouge_matrix_1 = np.zeros((len(pred), len(ref)))
            rouge_matrix_2 = np.zeros((len(pred), len(ref)))
            rouge_matrix_l = np.zeros((len(pred), len(ref)))
            rouge = WeightedRougeScore()
            for i, pred_info in enumerate(pred):
                for j, ref_info in enumerate(ref):
                    rouge_matrix_1[i][j] = rouge.get_rouge_1(pred_info, ref_info)
                    rouge_matrix_2[i][j] = rouge.get_rouge_2(pred_info, ref_info)
                    rouge_matrix_l[i][j] = rouge.get_rouge_l(pred_info, ref_info)
            max_weight1 = inter_result_metric_common(rouge_matrix_1)
            max_weight2 = inter_result_metric_common(rouge_matrix_2)
            max_weightl = inter_result_metric_common(rouge_matrix_l)
            total_weight1 += max_weight1
            total_weight2 += max_weight2
            total_weightl += max_weightl
        scores = {"rouge-1": total_weight1 / len(refs),
                  "rouge-2": total_weight2 / len(refs),
                  "rouge-l": total_weightl / len(refs),
                  }
        return scores

    # final_result
    def final_metric(self):
        refs = self.extract_key_val(self.ref[:97], self.final_key)
        preds = self.extract_key_val(self.pred[:97], self.final_key)
        refs_l = []
        preds_l = []
        rouge = Rouge()
        for ref, pred in zip(refs, preds):
            assert ref["id"] == pred["id"]
            refs_l.append(' '.join(jieba.cut(ref[self.final_key])))
            preds_l.append(' '.join(jieba.cut(pred[self.final_key])))

        scores = rouge.get_scores(refs_l, preds_l, avg=True)
        scores = {"rouge-1": scores["rouge-1"]["f"],
                  "rouge-2": scores["rouge-2"]["f"],
                  "rouge-l": scores["rouge-l"]["f"],
                  }
        return scores

    # sub_task1
    def fact_extract_metric(self):
        final_score = self.final_metric()
        inter_score = self.inter_metric()
        scores = {
            "rouge-1": 0.7 * inter_score["rouge-1"] + 0.3 * final_score["rouge-1"],
            "rouge-2": 0.7 * inter_score["rouge-2"] + 0.3 * final_score["rouge-2"],
            "rouge-l": 0.7 * inter_score["rouge-l"] + 0.3 * final_score["rouge-l"],
        }
        return scores

    # sub_task2
    # evidence reasoning metric
    def evid_metric(self):
        refs = self.extract_key_val(self.ref, self.evid_key)
        preds = self.extract_key_val(self.pred, self.evid_key)

        total_tp = 0
        total_tp_fn = 0
        total_tp_fp = 0

        for ref, pred in zip(refs, preds):
            assert ref["id"] == pred["id"]
            for r, p in zip(ref[self.evid_key], pred[self.evid_key]):
                r_id = list(r.keys())[0]
                p_id = list(p.keys())[0]
                total_tp += func_f1(r[r_id], p[p_id])
                total_tp_fp += len(p[p_id])
                total_tp_fn += len(r[r_id])

        precision = total_tp / (total_tp_fp + 1e-7)
        recall = total_tp / (total_tp_fn + 1e-7)
        f1 = 2 * precision * recall / (precision + recall + 1e-7)

        scores = {"precision": precision,
                  "recall": recall,
                  "f1": f1}
        return scores

    # subtask3
    # Experience metric
    def exp_metric(self):
        refs = self.extract_key_val(self.ref, self.exp_key)
        preds = self.extract_key_val(self.pred, self.exp_key)
        refs_l = []
        preds_l = []
        rouge = Rouge()
        for ref, pred in zip(refs, preds):
            assert ref["id"] == pred["id"]
            for r, p in zip(ref[self.exp_key], pred[self.exp_key]):
                refs_l.append(' '.join(jieba.cut(r["Exp"])))
                if "Exp" in p and p["Exp"] != "":
                    preds_l.append(' '.join(jieba.cut(p["Exp"])))
                else:
                    preds_l.append('None')
        scores = rouge.get_scores(preds_l, refs_l, avg=True)
        return scores

    # ALL
    # Maximum (node, edge, node) triplet rouge
    def comprehensive_metric(self, pred_trees, ref_trees):
        assert len(pred_trees) == len(ref_trees)
        total_score = 0
        for pred_tree, ref_tree in zip(pred_trees, ref_trees):
            score = reasoning_tree_metric_common(pred_tree, ref_tree)
            total_score += score["weighted-rouge-score"]

        norm_score = total_score / len(pred_trees)
        return norm_score


def main():
    args = args_parser()
    metric = Metric(args)

    if args.tid == "task1":
        print(metric.fact_extract_metric())
    elif args.tid == "task2":
        print(metric.evid_metric())
    elif args.tid == "task3":
        print(metric.exp_metric())
    elif args.tid == "ALL":
        ref_trees = load_json(args.ref)
        pred_trees = load_json(args.pred)
        print(metric.comprehensive_metric(pred_trees, ref_trees))
    else:
        raise ValueError("Invalid task id")

if __name__ == "__main__":
    main()