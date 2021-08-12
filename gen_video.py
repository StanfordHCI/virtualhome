from simulation.unity_simulator import comm_unity
import argparse
import os
from dataset_utils.execute_script_utils import parse_exec_script_file, render_script_from_path
import time


GRAPH_PATH_START = "init_and_final_graphs" #subdirectory of root where graphs are saved


def get_graph_file(action_dir: str, action: str):
    # replace action path with graph path
    first_slash = action.find('/')

    # replace .txt with .json
    graph_path = GRAPH_PATH_START + action[first_slash:-3] + "json"
    graph_path = os.path.join(action_dir, graph_path)

    assert os.path.isfile(graph_path)

    return graph_path


def main():
  parser = argparse.ArgumentParser(description="Generates video sequence for a given action_dir and action")
  parser.add_argument("--action_dir", help="Directory containing actions")
  parser.add_argument("--action", help="Path from action_dir to action file")
  args = parser.parse_args()
  action = args.action
  action_dir = args.action_dir

  assert action
  assert action_dir

  action_file = os.path.join(action_dir, action)
  
  print("action_dir={}\naction={}\naction_file={}\n".format(action_dir, action, action_file))

  assert os.path.isdir(action_dir)
  assert os.path.isfile(action_file)

  graph_path = get_graph_file(action_dir, action)
  print("graph_path: {}".format(graph_path))

  print("starting unity server...")
  mode = 'manual' # auto / manual
  if mode == 'auto':
      exec_file = '../simulation/macos_exec'
      comm = comm_unity.UnityCommunication(file_name=exec_file)
  else:
      comm = comm_unity.UnityCommunication(timeout_wait=5*60)
  print("unity server running")

  title, description, script = parse_exec_script_file(action_file)
  print("title={}, description={}, script={}".format(title, description, script))

  s, home_capture_camera_ids = comm.home_capture_camera_ids()

  print("home_capture_camera_ids:", home_capture_camera_ids)

  camera_modes = [ str(i) for i in home_capture_camera_ids ]

  last_slash = action_file.rfind("/")
  file_name = action_file[last_slash + 1:]
  output = 'Output/{}'.format(file_name)

  print("saving rendered result to {}".format(output))

  before = time.time()
  try:
    res = render_script_from_path(comm, action_file, graph_path, output, 'Chars/Female2')
  except:
    print("exception in render_script_from_path")
  print(res)
  after = time.time()
  diff = after - before
  print("time to complete:", diff)


if __name__ == "__main__":
  main()
