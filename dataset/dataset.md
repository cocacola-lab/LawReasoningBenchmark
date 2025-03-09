# Datasets
The **T**ransparent **L**aw-Reasoning with Tree-Organized Structures (**TL** for short), which aims to generate the hierarchical and layered tree-organized structure from the unstructured textual case description. 

Specifically, we break it down into three subtasks, namely **Factum Probandum Generation**, **Evidence Reasoning**, and **Experience Generation**. Furthermore, we designed a hierarchical and layered tree-organized framework, structured through interconnected nodes and edges, to evaluate the comprehensive capabilities of the LLMs to construct such complex structures.

Each subtask contains two files, one for the input of the task (the file with "input" and one for the label of the task (the file without the "input").

## Subtask1 Factum Probandum Generation
The `Case_info` field contains the content of criminal judgments. The `Inter_result` is a dictionary，and each interim probandum within it is extracted from the `Case_info`。Finally, the content of the `Final_result` field is the `Case_info` obtained from the Ultimate Probandum. Please refer to [task1](./test/task1) for more details.

This subtask aims to test the capability to extract the interim probandum from `Case_info` and analyze relevant content and summarize the Ultimate Probandum.

## Subtask2 Evidence Reasoning
This task requires extracting criminal evidence from `Case_info` while determining whether each piece of evidence can infer the interim probandum in `Inter_result`. `Evidence_link` is a list where each item is a dictionary, with keys match the keys of the interim probandum in `Inter_result`. The values are evidence collection, where each element represents an evidence span. Each span is denoted by $[p_s, p_e]$, indicating the start and end positions within `Case_info`. 

It is worth noting that each evidence span is segmented based on the Chinese full stop （。） in the `Case_info`, and the end position is the end of the evidence, not the next sentence of the evidence. Please refer to [task2](./test/task2) for more details.

## Subtask3 Experience Generation 
In this subtask, each element in the `Inter_evidence` list  consists of a fact-evidence pair,  where `Inter` represents an interim probandum and `Evidence` denotes the associated evidence. The objective of this task is to generate the human common sense and experience, referred to as `Exp`, which is necessary to infer the interim probandum from the available criminal evidence. Please refer to [task3](./test/task3) for more details.

## Comprehensive Score
We designed a hierarchical and layered tree-organized framework to evaluate the comprehensive capabilities of the LLMs to construct such complex structures.

In each case, there are two lists: `node` and `relation`. The `node` list comprises three categories of nodes: "Inter_result", "Final_result", and "Evidence". Each node contains a `node-id`, which is the node id, a `node-type`, which specifies the category of node, and `info`, which provides the node's content. Conversely, each entry in the `relation` list represents a directed inference pathway from an "Evidence" node to an "Inter_result" node. These entries include `relation-id`, indicating the path id, as well as `from-id` and `to-id`, which specify the starting and ending node id, respectively. The `exp-type` denotes whether human experience is required, while `exp` refers to the content of human experienceor common knowledge. Please refer to [ALL Dir](./test/ALL) for more details.








