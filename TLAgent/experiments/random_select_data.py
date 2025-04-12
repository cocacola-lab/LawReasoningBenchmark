import os.path
import random
from utils import read_json, write_json

random.seed(1)
data_dir = "./dataset/task2"
output_dir = "./dataset_ab/task2"

if __name__ == '__main__':
     task_name = data_dir.split("/")[-1]
     test_input_path = os.path.join(data_dir, f"test_sub{task_name}_input.json")
     test_raw_path = os.path.join(data_dir, f"test_sub{task_name}.json")

     test_input = read_json(test_input_path)
     test_raw = read_json(test_raw_path)

     # sample_list = list(range(len(test_input)))
     # select_numbers = random.sample(sample_list, 10)
     # select_numbers = sorted(select_numbers)
     # print(select_numbers)

     select_numbers = [4, 7, 8, 16, 24, 25, 28, 30, 31, 36]

     test_input_ab = []
     test_raw_ab = []
     for i in select_numbers:
          test_input_ab.append(test_input[i])
          test_raw_ab.append(test_raw[i])

     output_test_ab = os.path.join(output_dir, f"test_sub{task_name}_input_ab.json")
     output_raw_ab = os.path.join(output_dir, f"test_sub{task_name}_ab.json")

     write_json(test_input_ab, output_test_ab)
     write_json(test_raw_ab, output_raw_ab)

     # test_compre_path = os.path.join(data_dir, f"test_compre.json")
     # test_compre = read_json(test_compre_path)
     #
     # test_compre_ab = []
     # for i in select_numbers:
     #      test_compre_ab.append(test_compre[i])
     #
     # output_test_compre_ab = os.path.join(output_dir, f"test_compre_ab.json")
     # write_json(test_compre_ab,  output_test_compre_ab)