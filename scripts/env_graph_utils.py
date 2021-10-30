from simulation.unity_simulator import comm_unity
import json
from pprint import pprint
import os

DEFAULT_ENV_GRAPHS = 'default_env_graphs.json'


# Generates a json file containing the default scene environment graphs
def generate_default_env_graph_files(comm: comm_unity.UnityCommunication):
    defaults = {}
    for scene_num in range(0, 7):
        print("Getting default graph for scene_num={}".format(scene_num))

        s = comm.reset(scene_num)
        assert s == True

        s, graph = comm.environment_graph()
        assert s == True

        defaults[scene_num] = graph

    with open("default_env_graphs.json", 'w') as ofs:
        json.dump(defaults, ofs)


def get_default_env_graph_hashes():
    assert os.path.isfile(DEFAULT_ENV_GRAPHS)

    with open(DEFAULT_ENV_GRAPHS, 'r') as ifs:
        defaults = json.load(ifs)

    hashes = {}
    for key in defaults:
        print("\nscene: {}".format(key))
        rooms = [node['class_name'] for node in defaults[key]['nodes'] if node['category'] == 'Rooms']
        pprint(rooms)
        string_repr = ''
        for room in rooms:
            string_repr += room

        hash_repr = hash(string_repr)
        print("hash: {}".format(hash_repr))
        hashes[hash_repr] = key

    return hashes


def get_env_graph_hash(graph):
    rooms = [node['class_name'] for node in graph['nodes'] if node['category'] == 'Rooms']
    print("rooms: {}".format(rooms))

    string_repr = ''
    for room in rooms:
        string_repr += room

    hash_repr = hash(string_repr)
    print("hash: {}".format(hash_repr))

    return hash_repr


def main():
    print("Starting Unity server...")
    mode = 'manual'  # auto / manual
    if mode == 'auto':
        exec_file = '../simulation/macos_exec'
        comm = comm_unity.UnityCommunication(file_name=exec_file)
    else:
        comm = comm_unity.UnityCommunication(timeout_wait=5 * 60)
    print("Unity server running")

    # generate_default_env_graph_files(comm)
    get_default_env_graph_hashes()


if __name__ == "__main__":
    main()
