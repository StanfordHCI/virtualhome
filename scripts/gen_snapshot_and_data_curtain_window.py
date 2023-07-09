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
    num_interactions = 200  # each iteration has 2.36363636 (4*5/11 + 1*6/11) times function calls
    output = "../output"
    comm = UnityCommunication()
    comm.reset(ENV)

    graph_state = json.load(open("./base-new-big-window.json", ))
    #  the order is, 5 lights, 3 doors, 2 (day/night, curtain on/off), all on at the beginning
    iot_state = [1] * 10
    light_ids = [node['id'] for node in graph_state['nodes'] if node['class_name'] == 'light']
    door_ids = [node['id'] for node in graph_state['nodes'] if node['class_name'] == 'door']
    iot_ids_lookup_table = light_ids + door_ids

    frame_id = 0
    sensors = []
    cameras_select = [str(i) for i in range(20)]
    # cameras_select = [str(i) for i in range(16, 20)]
    # cameras_select = ['0']
    for _ in tqdm(range(num_interactions)):
        # so basically graph_state and iot_state both keep track of the states, but graph_state is for Unity
        # iot_state is for model training
        random_idx = randrange(0, 10)  # will generate 0,1,2,3,4,5,6,7,8,9 randomly, and we will toggle that iot
        # if random_idx == 7:  # TODO remove this before running
        #     random_idx = 4
        iot_state[random_idx] = 1 - iot_state[random_idx]  # 1-x will toggle the x
        if random_idx <= 7:  # if lights and doors
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
        if random_idx == 8:
            comm.update_day_and_night(iot_state[random_idx])
        if random_idx == 9:  # random_idx == 9
            comm.update_curtain(iot_state[random_idx])
            # if lights, we need to repeat extra 3 times
        num_rep = 3 if random_idx <= 4 else 0
        for _ in range(num_rep):
            obtain_snapshots_local(graph_state, comm, output, cameras_select)
        obtain_snapshots_local(graph_state, comm, output, cameras_select, frame_id)
        print(frame_id)
        print(iot_state.copy())
        sensors.append(torch.tensor(iot_state.copy(), dtype=torch.float32))
        frame_id += 1

    torch.save(sensors, output + '/sensors.pth')
