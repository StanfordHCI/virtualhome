import json
import torch
import base64
from random import randrange
from tqdm import tqdm
from simulation.unity_simulator.comm_unity import UnityCommunication


def obtain_snapshots_local(graph_state, comm, output, cameras_select, frame_num=None):
    comm.expand_scene(graph_state, randomize=False)
    if frame_num is not None:  # can't do "if frame_num"  because if so, 0 will be excluded
        _, rgb_imgs = comm.camera_image(cameras_select, mode='rgb', image_height=480, image_width=640)
        _, point_cloud_imgs = comm.camera_image(cameras_select, mode='point_cloud', image_height=480, image_width=640)
        for i in range(len(cameras_select)):
            with open("{}/{}-{}-rgb.png".format(output, frame_num, i), 'wb') as ofs:
                data = base64.b64decode(rgb_imgs[i])
                ofs.write(data)

            with open("{}/{}-{}-point_cloud.exr".format(output, frame_num, i), 'wb') as ofs:
                data = base64.b64decode(point_cloud_imgs[i])
                ofs.write(data)


if __name__ == '__main__':
    ENV = 2
    num_interactions = 120  # each iteration has 2.36363636 (4*5/11 + 1*6/11) times function calls
    output = "../output"
    comm = UnityCommunication()
    comm.reset(ENV)

    graph_state = json.load(open("./base.json", ))
    #  the order is, 5 lights, 3 doors, 3 tablelamp, all on at the beginning
    iot_state = [1] * 11
    light_ids = [node['id'] for node in graph_state['nodes'] if node['class_name'] == 'light']
    door_ids = [node['id'] for node in graph_state['nodes'] if node['class_name'] == 'door']
    tablelamp_ids = [node['id'] for node in graph_state['nodes'] if node['class_name'] == 'tablelamp']
    iot_ids_lookup_table = light_ids + door_ids + tablelamp_ids

    frame_id = 0
    sensors = []
    cameras_select = [str(i) for i in range(20)]
    # cameras_select = ['0']
    for _ in tqdm(range(num_interactions)):
        # so basically graph_state and iot_state both keep track of the states, but graph_state is for Unity
        # iot_state is for model training
        random_idx = randrange(0, 11)  # will generate 0,1,2,3,4,5,6,7,8,9,10 randomly, and we will toggle that iot
        iot_state[random_idx] = 1 - iot_state[random_idx]  # 1-x will toggle the x
        for j in range(len(graph_state["nodes"])):
            if graph_state["nodes"][j]["id"] == iot_ids_lookup_table[random_idx]:
                local_states = graph_state["nodes"][j]["states"]
                # toggle the states
                if "ON" in local_states:
                    graph_state["nodes"][j]["states"].remove("ON")
                    graph_state["nodes"][j]["states"].append("OFF")

                elif "OFF" in local_states:
                    graph_state["nodes"][j]["states"].remove("OFF")
                    graph_state["nodes"][j]["states"].append("ON")

                elif "OPEN" in local_states:
                    graph_state["nodes"][j]["states"].remove("OPEN")
                    graph_state["nodes"][j]["states"].append("CLOSED")

                elif "CLOSED" in local_states:
                    graph_state["nodes"][j]["states"].remove("CLOSED")
                    graph_state["nodes"][j]["states"].append("OPEN")

        # if lights, we need to repeat extra 3 times
        num_rep = 3 if random_idx <= 4 else 0
        for _ in range(num_rep):
            obtain_snapshots_local(graph_state, comm, output, cameras_select)
        obtain_snapshots_local(graph_state, comm, output, cameras_select, frame_id)
        sensors.append(torch.tensor(iot_state.copy(), dtype=torch.float32))
        with open("{}/original-{}.json".format(output, frame_id), 'w') as file_obj:  # open the file in write mode
            json.dump(graph_state, file_obj)
        frame_id += 1

    torch.save(sensors, output + '/sensors.pth')

'''
legacy

    # base_iot_state = [1] * 11
    # iot_idx_lookup_table
    
            # base_iot_state[random_idx] = 1 - base_iot_state[random_idx]  # 1-x will toggle the x

'''
