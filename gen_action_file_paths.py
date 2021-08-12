import os
from pprint import pprint

root = 'programs_processed_precond_nograb_morepreconds/executable_programs'
dirs = os.listdir(root)

paths = [ os.path.join(root, dir) for dir in dirs ]

scene_dirs = []
for path in paths:
  scene_dirs += os.listdir(path)

paths = [ os.path.join(path, scene_dir) for scene_dir in scene_dirs ]

print("number of scene directories: ", len(paths))

file_names = []
for path in paths:
  file_names += os.listdir(path)

paths = [ os.path.join(path, file_name) for file_name in file_names ]

print("number of files: ", len(paths))

with open("all_actions.txt", 'w') as ofs:
  for path in paths:
    path = path[path.find('/') + 1:]
    ofs.write(path + '\n')