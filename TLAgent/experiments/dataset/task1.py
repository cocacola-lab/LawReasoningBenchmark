# Note: you need to be using OpenAI Python v0.27.0 for the code below to work
from utils import read_prompt, read_json, write_json
from task_utils import segdata

input_datapath = "task1/test_subtask1_input.json"
output_prefix = "splitdata/task1"

def main():
    data_info_list = read_json(input_datapath)
    segments = []
    for i, data in enumerate(data_info_list):
        segment = segdata(data, 2000)
        segments.append(segment)

    for i, segment in enumerate(segments):
        output_path = output_prefix + "/" + "task1_c" + str(segment["id"])+".json"
        write_json(segment, output_path)

if __name__ == '__main__':
    main()
