# Evaluation

You can use `evaluator.py` to evaluate the output of your model.

## Usage
**The installation of evaluating env.**

```bash
pip install -r requirements.txt
```

**Evaluate different subtasks.**
```bash
# task1
python evaluator.py --pred=/path/to/pred --ref=/path/to/test_subtask1.json --tid="task1"
# task2
python evaluator.py --pred=/path/to/pred --ref=/path/to/test_subtask2.json --tid="task2"
# task3
python evaluator.py --pred=/path/to/pred --ref=/path/to/test_subtask3.json --tid="task3"
```

**Calculate the comprehensive score.**

Before calculating the comprehensive score, you need to run through all the processes of task1 -> task2 -> task3. If the output is in the following JSON format, you can use the script [ALL_postproc.py](./ALL_postproc.py) to convert the format and proceed with the evaluation.

处理前的数据格式：

```json
[
    {
        "id": 1,
        "Case_info": "xxx",
        "Inter_result": {
            "AX000": "xxx",
            "AX001": "xxx",
            ...
        },
        "Final_result": "xxx",
        "Evidence_link": {
            "AX000": [
                [
                    148,
                    148
                ],
                [
                    ...
                ]
                ...
            ]
        },
        "Inter_evidence": [
            {
                "ie_id": 0,
                "Inter": "xxx",
                "Evidence": "xxx",
                "Exp": "xxx"
            },
            ...
        ]
    },
    ...
]
```

Use the script to convert raw format into a hierarchical and layered tree-organized framework.

```bash
python ALL_postproc.py /path/to/pred /path/to/pred_post.json
```

Evaluate using scripts.

```bash
python evaluator.py --pred=/path/to/pred_post.json --ref=/path/to/test_compre.json --tid="ALL"
```