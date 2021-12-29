# Generate snapshot for a program. Make sure you have the executable open
import json
import numpy as np
import base64
from tqdm import tqdm
from simulation.unity_simulator.comm_unity import UnityCommunication
import simulation.evolving_graph.check_programs as check_programs


def obtain_snapshots_local(graph_state, comm, output, frame_num, j):
    # s, scene_camera_ids = comm.home_capture_camera_ids()
    # cameras_select = [str(i) for i in scene_camera_ids]
    # cameras_select = ['18', '8']
    cameras_select = [str(i) for i in range(16, 20)]
    # cameras_select = ['0']
    print(cameras_select)
    # comm.reset(ENV)
    _ = comm.expand_scene(graph_state, randomize=False)
    _, rgb_imgs = comm.camera_image(cameras_select, mode='rgb', image_height=480, image_width=640)

    for i in range(len(cameras_select)):
        with open("{}/{}-{}-{}-rgb.png".format(output, frame_num, i, j), 'wb') as ofs:
            data = base64.b64decode(rgb_imgs[i])
            ofs.write(data)


if __name__ == '__main__':
    ENV = 2
    output = "../output/"
    comm = UnityCommunication()
    print('Loading graph')
    comm.reset(ENV)
    _, graph_input = comm.environment_graph()
    graph_input = check_programs.translate_graph_dict_nofile(graph_input)
    # graph_state_list = get_graph_state()
    # obtain_snapshots(graph_state_list, comm, output)

    for i in range(1):
        f = open("../graph_states/{}.json".format(i), )
        data = json.load(f)
        for j in range(4):
            obtain_snapshots_local(data, comm, output, i, j)
