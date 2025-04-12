import argparse

def Arguments():
    parser = argparse.ArgumentParser(description='Create a new agent.')
    # search user
    parser.add_argument('--useremail', type=str, default="admin@tfagent.com",
                        help='user email.')
    # project config
    parser.add_argument('--projectname', type=str, default="Default Project",
                        help='project name.')

    # task config
    # No setup is required
    parser.add_argument('--agentname', type=str, help='Agent name for the script.')
    parser.add_argument('--description', type=str, help='Agent description for the script.')
    parser.add_argument('--goals', type=str, nargs='+', help='Agent goals for the script.')
    parser.add_argument('--agent-execution-name', type=str, help='Agent Execution name.')

    # execution config
    parser.add_argument("--permissiontype", type=str, default="",
                        choices=["God Mode", "Restrict"],
                        help='if you choose Restrict, the agent use the tool when you agree')
    parser.add_argument("--workflow", type=str, default="Goal Based Workflow",
                        choices=["Goal Based Workflow", "Dynamic Task Workflow", "Fixed Task Workflow",
                                 "Fact Workflow 2"],
                        help='Agent description for the script.')

    # The path to the experiment file
    parser.add_argument("--input-dir", type=str, default="./dataset/splitdata/task1", )
    parser.add_argument("--raw_data_path", type=str, default="./dataset/task1/test_subtask1_input.json", )
    parser.add_argument("--output_path", type=str, default="./dataset/output/output_test_subtask1_ab.json" )
    # max_segment_length
    parser.add_argument("--max-seg-length", type=int, default=2000, )
    # no agent
    parser.add_argument("--no-agent", action="store_true", )

    # step
    parser.add_argument("--step1", action="store_true", )
    parser.add_argument("--step2", action="store_true", )
    parser.add_argument("--step3", action="store_true", )
    parser.add_argument("--step4", action="store_true", )
    parser.add_argument("--step5", action="store_true", )
    parser.add_argument("--step6", action="store_true", )
    parser.add_argument("--step7", action="store_true", )

    # task1 config
    # in step 3
    parser.add_argument("--task1-match-src", action="store_true", )
    parser.add_argument("--task1-remove-duplicate", action="store_true", )

    # task2 config
    # in step 3
    parser.add_argument("--task2-match-src", action="store_true", )
    parser.add_argument("--task2-remove-duplicate", action="store_true", )

    # in step 4
    parser.add_argument("--task2-pool-num", type=int, default=3, )
    parser.add_argument("--evids-split-path", type=str, default="./dataset/output/evids_split_subtask2.json", )

    # task3 config
    # in step 1
    parser.add_argument("--task3-pool-num", type=int, default=2, )
    args = parser.parse_args()
    return args

args = Arguments()