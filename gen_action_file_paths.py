import os
from pprint import pprint

root = 'programs_processed_precond_nograb_morepreconds/executable_programs'
dirs = os.listdir(root)

paths = [ os.path.join(root, dir) for dir in dirs ]

file_paths = []
for path in paths:
  scene_dirs = os.listdir(path)
  new_paths = [ os.path.join(path, scene_dir) for scene_dir in scene_dirs ]

  for new_path in new_paths:
    file_names = os.listdir(new_path)
    file_paths += [ os.path.join(new_path, file_name) for file_name in file_names ]

print("number of files: ", len(file_paths))

with open("all_actions.txt", 'w') as ofs:
  for path in file_paths:
    path = path[path.find('/') + 1:]
    ofs.write(path + '\n')