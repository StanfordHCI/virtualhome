# Generate snapshot for a program. Make sure you have the executable open
import json
import numpy as np
import base64
import argparse
import os
import re

from tqdm import tqdm
from simulation.unity_simulator.comm_unity import UnityCommunication
import simulation.evolving_graph.check_programs as check_programs
import dataset_utils.add_preconds as add_preconds

ENV = 2

# regular expression to get actions
# zhuoyue: we should match all kinds of ids, not just 1s.
# also, Griffin's original regular expression prevent things like "standup", so I add the `|\[.+\]`
re_compiled = re.compile(
    "^\[.+\] <[a-zA-Z_]+> \(\d+\)|\[.+\] <[a-zA-Z_]+> \(\d+(\.\d+)\)|( <[a-zA-Z_]+> \(\d+\)) |\[.+\]$")


def read_action_file(action_file: str):
    actions = []
    with open(action_file, 'r') as action_ifs:
        for line in action_ifs:
            # zhuoyue: here I loosely used '[' to check if it's a legit line, which is not quite strict,
            # but as long as we make sure the script is good, this should be good as well
            if '[' in line:
                actions.append(line.strip())

            # zhuoyue: original code
            # match = re_compiled.match(line.strip())
            # if match:
            #     actions.append(match.group())

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


def obtain_snapshots(graph_state_list, comm, output, num_scene_cameras=20, num_char_cameras=2):
    s, scene_camera_ids = comm.home_capture_camera_ids()
    # cameras_select = [str(i) for i in scene_camera_ids][:num_scene_cameras]
    cameras_select = [str(i) for i in scene_camera_ids]
    # s, char_camera_ids = comm.character_cameras()

    # because the ids of char cameras starts from 20 (there are 20 scene cameras, 8 character cameras)
    # cameras_select.extend([str(i + len(scene_camera_ids)) for i in range(num_char_cameras)])
    # only show the first camera (id: 0) and the one mounted on the person ( id:28 the 29th camera)
    # cameras_select = ['0', '1', '2', '3', '28']
    cameras_select = ['0']
    print(cameras_select)

    frame_num = 0
    # for i in range(2):
    for graph_state in tqdm(graph_state_list):  # tqdm is progress bar
        # the following doesn't help with the weird location issue
        # graph_state['nodes'] = sorted(graph_state['nodes'], key=lambda i: i["id"])
        # if graph_state['nodes'][0]['id'] == 163:
        #     graph_state['nodes'][0]['states'] = ["CLEAN", "PLUGGED_IN", "CLOSED"]

        # with open("{}/{}.json".format(output, frame_num), 'w') as file_obj:  # open the file in write mode
        #     json.dump(graph_state, file_obj)

        # f = open("{}/{}.json".format(output, i),)
        # graph_state = json.load(f)
        message = comm.expand_scene(graph_state, randomize=False)
        print(message)

        ## Save iot raw data directly in JSON
        # with open("{}/{}.json".format(output, frame_num), 'w') as file_obj:  # open the file in write mode
        #     json.dump(graph_state["nodes"], file_obj)

        new_data = []
        # cleaning the data such that we only leave the ids and states (for binary IoT), sorted by id
        for data_entry in graph_state["nodes"]:
            local_new = {}
            local_states = data_entry["states"]  # tracking binary for now
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
        sorted_new_data = sorted(new_data, key=lambda i: i["id"])

        _, motion_sensors_distances = comm.get_motion_sensor_states()
        num_sensors_per_room = 8  # zhuoyue: changeable, currently we have 8 corners per room so
        threshold = 7  # zhuoyue, because, typically the min distance is 1,0-3.0, max is about 17 or 18.
        # And when the character stand in the center of the room, the distances to 8 corners are around 6.3 to 6.9
        latest_id = sorted_new_data[-1]["id"]

        # loop through the motion_sensor_distance
        dis_list = json.loads(motion_sensors_distances)
        for i in range(len(dis_list)):
            local_new = {"id": latest_id + 1 + i,
                         "state": int(dis_list[i] <= threshold),
                         "class_name": 'motion_sensor_of_room_{}'.format(i // num_sensors_per_room)}
            sorted_new_data.append(local_new)

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
preconds = add_preconds.get_preconds_script(script).printCondsJSON()
print(preconds)

print('Loading graph')
comm.reset(ENV)
comm.add_character_camera()
comm.add_character()
_, graph_input = comm.environment_graph()
print('Executing script')
print(script)
graph_input = check_programs.translate_graph_dict_nofile(graph_input)

message, final_state, graph_state_list, graph_dict, id_mapping, info, helper, modif_script = check_programs.check_script(
    script, preconds, graph_path=None, inp_graph_dict=graph_input)

# zhuoyue: graph_state_list is basically a list of nodes, each node is a list of states, which has been looped
# in the `for graph_state in tqdm(graph_state_list)`

if message == 'Script is executable':
    print('Generating snapshots')
    output = "Output/"
    if not os.path.isdir(output):
        os.mkdir(output)
    # the last two argument is about the number of cameras for scene (static) and character (moving with the person)
    # scene cameras (20 in total): [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
    # character cameras (8 in total): ["PERSON_FRONT","PERSON_TOP","FIRST_PERSON","PERSON_FROM_BACK","PERSON_FROM_LEFT","PERSON_RIGHT","PERSON_LEFT","PERSON_BACK"]
    # if you do the `comm.add_character_camera()` before, there will be another "new_camera" at the end of the list
    obtain_snapshots(graph_state_list, comm, output)
else:
    print("Not executable!!!")
    print(message)
    # # load json
    # for i in range(4):
    #     f = open("{}/{}.json".format(output, i),)
    #     data = json.load(f)
    #     # with open("{}/{}.json".format(output, i), 'r') as file_obj:  # open the file in write mode
    #     #     gg = json.load(file_obj)
    #     message = comm.expand_scene(data, randomize=False)
    #     print(message)
