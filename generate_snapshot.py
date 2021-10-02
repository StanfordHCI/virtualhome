# Generate snapshot for a program. Make sure you have the executable open
import json
import sys
import numpy as np
import random
import cv2
import base64

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

ENV = 2

# # regular expression to get actions
re_compiled = re.compile("^\[.+\] <[a-zA-Z_]+> \(\d+\)(| <[a-zA-Z_]+> \(\d+\))$") # zhuoyue: we should match all kinds of ids, not just 1s.
# re_compiled = re.compile("^\[.+\] <[a-zA-Z_]+> \(1\)(| <[a-zA-Z_]+> \(1\))$")


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


def obtain_snapshots(graph_state_list, reference_graph, comm, output):
    s, home_capture_camera_ids = comm.home_capture_camera_ids()
    cameras_select = [str(i) for i in home_capture_camera_ids][:1]

    seed = random.randint(1, 100)

    frame_num = 0
    comm.reset(ENV)
    comm.add_character()
    for graph_state in tqdm(graph_state_list): # tqdm is progress bar
        message = comm.expand_scene(graph_state, randomize=False)
        print(message)
        new_data = []


        # Save iot raw data directly in JSON
        # with open("{}/{}.json".format(output, frame_num), 'w') as file_obj:  # open the file in write mode
        #     json.dump( graph_state["nodes"], file_obj)


        # cleaning the data such that we only leave the ids and states (for binary IoT), sorted by id
        for data_entry in graph_state["nodes"]:
            local_new = {}
            local_states = data_entry["states"] # tracking binary for now
            if "ON" in local_states or "OPEN" in local_states:
                local_new["id"] = data_entry["id"]
                local_new["state"] = 1
                local_new["class_name"] = data_entry["class_name"]
                new_data.append(local_new)
            elif "OFF" in local_states or "CLOSED" in local_states:
                local_new["id"] = data_entry["id"]
                local_new["state"] = 0
                local_new["class_name"] = data_entry["class_name"]
                new_data.append(local_new)
        sorted_new_data = sorted(new_data, key = lambda i: i["id"])
        with open("{}/{}.json".format(output, frame_num), 'w') as file_obj:  # open the file in write mode
            json.dump(sorted_new_data, file_obj)

        _, rgb_imgs = comm.camera_image(cameras_select, mode='rgb', image_height=480, image_width=640)
        # _, point_cloud_imgs = comm.camera_image(cameras_select, mode='point_cloud', image_height=480, image_width=640)

        # Currently Zhengze don't need seg data
        # _, seg_class_imgs = comm.camera_image(cameras_select, mode='seg_class', image_height=480, image_width=640)
        # _, seg_inst_imgs = comm.camera_image(cameras_select, mode='seg_inst', image_height=480, image_width=640)

        for i in range(len(cameras_select)):
            with open("{}/{}-{}-rgb.png".format(output, frame_num, i), 'wb') as ofs:
                data = base64.b64decode(rgb_imgs[i])
                ofs.write(data)

            # with open("{}/{}-{}-point_cloud.exr".format(output, frame_num, i), 'wb') as ofs:
            #     data = base64.b64decode(point_cloud_imgs[i])
            #     ofs.write(data)

            # with open("{}/{}-{}-seg_class.png".format(output, frame_num, i), 'wb') as ofs:
            #     data = base64.b64decode(seg_class_imgs[i])
            #     ofs.write(data)
            #
            # with open("{}/{}-{}-seg_inst.png".format(output, frame_num, i), 'wb') as ofs:
            #     data = base64.b64decode(seg_inst_imgs[i])
            #     ofs.write(data)

        frame_num += 1


comm = UnityCommunication()

print('Inferring preconditions...')
# script = ['[Walk] <television> (1)', '[SwitchOn] <television> (1)', 
#           '[Walk] <sofa> (1)', '[Find] <controller> (1)',
#           '[Grab] <controller> (1)']
preconds = add_preconds.get_preconds_script(script).printCondsJSON()
print(preconds)

print('Loading graph')
comm.reset(ENV)
comm.add_character()
_, graph_input = comm.environment_graph()
print('Executing script')
print(script)
graph_input = check_programs.translate_graph_dict_nofile(graph_input)

# print('Checking graph_input')
# print(graph_input)

info = check_programs.check_script(
    script, preconds, graph_path=None, inp_graph_dict=graph_input)

message, final_state, graph_state_list, graph_dict, id_mapping, info, helper, modif_script = info
success = (message == 'Script is executable')
print(message)

if success:
    print('Generating snapshots')
    output = "Output/"
    if not os.path.isdir(output):
        os.mkdir(output)

    obtain_snapshots(graph_state_list, graph_input, comm, output)
    # zhuoyue: the `obtain_snapshots` does not have reture statement, so I guess we don't need the followings?
    # messages, images = obtain_snapshots(graph_state_list, graph_input, comm, output)
    # grid_img = build_grid_images(images)
    # cv2.imwrite('snapshot_test_zy.png', grid_img)
    # print('Snapshot saved in demo/snapshot_test.png')
