# Generate snapshot for a program. Make sure you have the executable open
import json
import sys 
import numpy as np
import random
import cv2

sys.path.append('./simulation')
sys.path.append('./dataset_utils/')

from tqdm import tqdm
from unity_simulator.comm_unity import UnityCommunication
import add_preconds
import evolving_graph.check_programs as check_programs
import evolving_graph.utils as utils
import evolving_graph.scripts as scripts
import argparse
import os
import re


ENV = 4

# # regular expression to get actions
re_compiled = re.compile("^\[.+\] <[a-zA-Z_]+> \(1\)(| <[a-zA-Z_]+> \(1\))$")

def read_action_file(action_file: str):
    actions = []
    with open(action_file, 'r') as action_ifs:
        for line in action_ifs:
            match = re_compiled.match(line.strip())
            if match:
                actions.append(match.group())

    return actions

# Add here your script
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

# Load script from file
script = read_action_file(action_file)
print(script)

def build_grid_images(images):
    image_steps = []
    for image_step in images:
        img_step_cameras = np.concatenate(image_step, 1)
        image_steps.append(img_step_cameras)
    final_image = np.concatenate(image_steps, 0)
    return final_image

def obtain_snapshots(graph_state_list, reference_graph, comm):
    s, home_capture_camera_ids = comm.home_capture_camera_ids()
    cameras_select = [ str(i) for i in home_capture_camera_ids ][:1]
    
    seed = random.randint(1,100)
    messages_expand, images = [], []
    for graph_state in tqdm(graph_state_list):
        comm.reset(ENV)
        comm.add_character()

        message = comm.expand_scene(graph_state, randomize=True, random_seed=seed)
        messages_expand.append(message)
        print(message)
        # _ = comm.camera_image(cameras_select, mode='rgb', image_height=480,  image_width=640)
        ok, imgs = comm.camera_image(cameras_select, mode='rgb', image_height=480,  image_width=640)
        images.append(imgs)

    return messages_expand, images


comm = UnityCommunication()

print('Inferring preconditions...')
# script = ['[Walk] <television> (1)', '[SwitchOn] <television> (1)', 
#           '[Walk] <sofa> (1)', '[Find] <controller> (1)',
#           '[Grab] <controller> (1)']
preconds = add_preconds.get_preconds_script(script).printCondsJSON()
print(preconds)

print('Loading env and character')
comm.reset(ENV)
comm.add_character()
# _, graph_input = comm.environment_graph()
print('Executing script')
print(script)
# graph_input = check_programs.translate_graph_dict_nofile(graph_input)

graph_path = 'init_and_final_graphs/TrimmedTestScene2_graph/results_intentions_march-13-18/file97_1/0.json'
info = check_programs.check_script(
        script, preconds, graph_path=os.path.join(action_dir, graph_path))

message, final_state, graph_state_list, graph_dict, id_mapping, info, helper, modif_script = info
success = (message == 'Script is executable')
print(message)

if success:
    print('Generating snapshots')
    messages, images = obtain_snapshots(graph_state_list, None, comm)
    grid_img = build_grid_images(images)
    cv2.imwrite('snapshot_test.png', grid_img)
    print('Snapshot saved in demo/snapshot_test.png')
    
