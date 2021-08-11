import argparse
import os
import sys

def main():
  parser = argparse.ArgumentParser(description="Takes a file containing paths to every action and splits it into an arbitrary number of action.txt files")
  parser.add_argument("--all_actions", help="file containing all actions")
  parser.add_argument("--num_files", help="number of files to split all actions into")
  args = parser.parse_args()
  all_actions = args.all_actions
  num_files = int(args.num_files)

  assert all_actions
  assert num_files
  assert isinstance(num_files, int)

  with open(all_actions, 'r') as ifs:
    paths = ifs.readlines()

  print("number of files: ", len(paths))
  print("splitting into {} files".format(num_files))

  output_dir = "actions"

  os.mkdir(output_dir)

  for file_num in range(num_files):
    dir_path = os.path.join(output_dir, str(file_num))
    os.mkdir(dir_path)
    file_path = os.path.join(dir_path, 'actions.txt')
    with open(file_path, 'w') as ofs:
      print("writing to file {} at path {}".format(file_num, file_num))
      for i, path in enumerate(paths):
        if (i % num_files) == file_num:
          ofs.write(path.strip() + '\n')

    






if __name__ == "__main__":
  main()