from simulation.unity_simulator import comm_unity
import argparse
import os
from dataset_utils.execute_script_utils import parse_exec_script_file, render_script_from_path, render_script
import time
import re
import sys

sys.path.append('./simulation')
sys.path.append('./dataset_utils/')

from unity_simulator.comm_unity import UnityCommunication
import add_preconds
import evolving_graph.check_programs as check_programs

ENV = 2

GRAPH_PATH_START = "init_and_final_graphs"  # subdirectory of root where graphs are saved

re_compiled = re.compile("^\[.+\] <[a-zA-Z_]+> \(1\)(| <[a-zA-Z_]+> \(1\))$")


def read_action_file(action_file: str):
    actions = []
    with open(action_file, 'r') as action_ifs:
        for line in action_ifs:
            # zhuoyue: here I loosely used '[' to check if it's a legit line, which is not quite strict,
            # but as long as we make sure the script is good, this should be good as well
            if '[' in line:
                actions.append(line.strip())

    return actions


def get_graph_file(action_dir: str, action: str):
    # replace action path with graph path
    first_slash = action.find('/')

    # replace .txt with .json
    graph_path = GRAPH_PATH_START + action[first_slash:-3] + "json"
    graph_path = os.path.join(action_dir, graph_path)

    assert os.path.isfile(graph_path)

    return graph_path


def get_video_script(action_dir: str, action: str):
    print("get_video_script: action_dir={}, action={}".format(action_dir, action))
    path = "executable_programs/TrimmedTestScene{}_graph/"

    re_end = re.compile("[a-zA-Z0-9\-_]+\/[a-zA-Z0-9\-_]+\/[a-zA-Z0-9\-._]+$")

    match = re_end.search(action.strip())
    if match:
        path_end = match.group()

    print("path_end={}".format(path_end))
    path = path + path_end
    print("path={}".format(path))

    exists = False
    for i in range(1, 8):
        tmp_path = "executable_programs/TrimmedTestScene{}_graph/".format(i)
        if os.path.isfile(path):
            exists = True
            print("get_video_script: found file for env={}".format(i))
        else:
            print("get_video_script: file invalid for env={}".format(i))

    assert (exists)


def convert_to_video_script(script):
    re_match = re.compile("^\[.+\]")

    video_script = []
    for line in script:
        match = re_match.match(line)

        assert (match)

        upper_version = match.group().upper()

        new_version = re_match.sub(upper_version, line)

        print("convert_to_video_script: new script line: {}".format(new_version))

        video_script.append(new_version)

    return video_script


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

    # Load script from file
    script = read_action_file(action_file)
    print(script)
    print('Inferring preconditions...')
    # script = ['[Walk] <television> (1)', '[SwitchOn] <television> (1)',
    #           '[Walk] <sofa> (1)', '[Find] <controller> (1)',
    #           '[Grab] <controller> (1)']
    preconds = add_preconds.get_preconds_script(script).printCondsJSON()
    print(preconds)

    print('Loading graph')
    comm = UnityCommunication()
    comm.reset(ENV)
    comm.add_character()
    _, graph_input = comm.environment_graph()
    print('Executing script')
    print(script)
    graph_input = check_programs.translate_graph_dict_nofile(graph_input)
    info = check_programs.check_script(
        script, preconds, graph_path=None, inp_graph_dict=graph_input)

    message, final_state, graph_state_list, graph_dict, id_mapping, info, helper, modif_script = info
    success = (message == 'Script is executable')
    print(message)

    video_script = convert_to_video_script(script)
    print("video_script: {}".format(video_script))

    last_slash = action_file.rfind("/")
    file_name = action_file[last_slash + 1:]
    output = 'Output/{}'.format(file_name)

    before = time.time()
    try:
        # zhuoyue: ok, I think I get it, it takes the `video_script` as actions,
        # graph_state_list[0] as the initial states of everything, and everything from now on happens in Unity
        res = render_script(comm, video_script, graph_state_list[0], ENV, output, find_solution=True)
        print(res)
    except Exception as e:
        print("exception in render_script_from_path")
        print(e)
    after = time.time()
    diff = after - before
    print("time to complete:", diff)


if __name__ == "__main__":
    main()
