import random

num_to_process = 100

with open('filtered_files.txt', 'r') as f:
  lines = f.readlines()

num_files = len(lines)
random_idxs = random.sample(range(num_files), num_to_process)
selected_files = [lines[idx] for idx in random_idxs]

with open('selected_files.txt', 'w') as f:
  f.writelines(selected_files)
