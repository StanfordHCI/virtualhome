# Code to execute a script from the dataset using the python simulator
from tqdm import tqdm
import re
import glob
import sys
import os
import copy
import requests.exceptions
import json
import cv2

curr_dirname = os.path.dirname(__file__)
sys.path.append('{}/../simulation/'.format(curr_dirname))
from evolving_graph import scripts, check_programs, utils

helper = utils.graph_dict_helper()

# parses a file from the executable folder
def parse_exec_script_file(file_name):
    with open(file_name, 'r') as f:
        content = f.readlines()
        content = [x.strip() for x in content]
        title = content[0]
        description = content[1]
        script_raw = content[4:]

    script = []
    for elem in script_raw:
        print(elem)

        tmp = elem
        start_idx = 0
        while True:
            start = tmp.find('(', start_idx)
            end = tmp.find('.')

            if end == -1:
                break

            tmp = tmp[:start + 1] + tmp[end + 1:]
            start_idx = end + 1

        print(tmp)
        script.append(tmp)

    return title, description, script

# given a file name of an environment, get an id
def obtain_scene_id_from_path(path):
    scene_name = [x for x in path.split('/') if 'TrimmedTestScene' in x][0]
    scene_number = int(scene_name.split('TrimmedTestScene')[1].split('_graph')[0])
    return scene_number

# given the message obtained from extending a scene, gets the objects that 
# could not be expanded
def obtain_objects_from_message(message):
    objects_missing = []
    for x in ['unplaced', 'missing_destinations', 'missing_prefabs']:
        if x in message.keys():
            objects_missing += message[x]
    return objects_missing

# Given a path from executable_programs, and a graph, executes the script
def render_script_from_path(comm, path_executable_file, path_graph, output, character):
    scene_id = obtain_scene_id_from_path(path_graph)
    title, description, script = parse_exec_script_file(path_executable_file)
    with open(path_graph, 'r') as f:
        content = json.load(f)
        init_graph = content['init_graph']

    result = render_script(comm, script, init_graph, scene_id-1, output, character)
    return result


# regular expression to get actions
re_compiled = re.compile("^\[.+\] <[a-zA-Z_]+> \([0-9]+\)(| <[a-zA-Z_]+> \([0-9]+\))$")

# gets the step type
re_step_type = re.compile("\[.+\]")

# gets step itmes (type and target id)
re_step_items = re.compile("<[a-zA-Z_]+> \([0-9]+\)")

# gets step type
re_object_type = re.compile("<[a-zA-Z_]+>")

# gets step obj id 
re_object_id = re.compile("\([0-9]+\)")    
def process_action(action, graph, env_graph):
    step_obj_id_to_type = {}
    step_obj_id_to_graph_id = {}

    with open('resources/class_name_equivalence.json', 'r') as ifs:
        name_equiv = json.load(ifs)

    print(name_equiv)

    step_pipeline = []
    for step in action:
        step_type = re_step_type.match(step).group()[1:-1]
        
        print("step_type: {}".format(step_type))

        step_items = []
        
        while True:
            step_item = re_step_items.search(step)
            
            if step_item:
                step_items.append(step_item.group())
                step = step[step_item.end():]
            else:
                break

        print("step_items:", step_items)

        pipeline_item = { 'step_type': step_type, 'objects': []}
        for step_item in step_items:
            object_type = re_object_type.match(step_item).group()[1:-1]
            print('object_type:', object_type)
            object_id = re_object_id.search(step_item).group()[1:-1]
            print('object_id:', object_id)

            if object_id not in step_obj_id_to_type:
                step_obj_id_to_type[object_id] = object_type

            pipeline_item['objects'].append({'object_type': object_type, 'object_id': object_id})

        step_pipeline.append(pipeline_item)
    
    # pprint.pprint(step_pipeline)

    for obj_id in step_obj_id_to_type:
        obj_type = step_obj_id_to_type[obj_id]
        # print(obj_id, obj_type)
        
        node = next((n for n in graph['nodes'] if n['class_name'] == obj_type))
        
        if obj_id not in step_obj_id_to_graph_id:
            step_obj_id_to_graph_id[obj_id] = node['id']
            # print(obj_id, node['id'])

    proc_steps = []
    for pipeline_item in step_pipeline:
        step_string = "[{}]".format(pipeline_item['step_type'])
        
        for object_data in pipeline_item['objects']:
            object_type = object_data['object_type']

            items = [item for item in env_graph['nodes'] if item['class_name'] in name_equiv[object_type]]
            print("Found {} items of type {} in env_graph".format(len(items), object_type))
            assert len(items) > 0

            object_id = object_data['object_id']
            step_string += " <{}> ({})".format(items[0]['class_name'], items[0]['id'])
            print(items[0])
            
        proc_steps.append(step_string)
    
    return proc_steps

# Renders a script , given a scene and initial environment
def render_script(comm, script, init_graph, scene_num, output, character):
    comm.reset(scene_num)
    if type(script) == list:
        script_content = scripts.read_script_from_list_string(script)
    else:
        script_content = scripts.read_script_from_string(script)

    script_content, _ = check_programs.modify_objects_unity2script(helper, script_content)
    success, message = comm.expand_scene(init_graph)
    
    if type(message) != dict:
        comm.reset()
        return {'success_expand': False, 
                'message': ('There was an error expanding the scene.', message)}
    else:
        objects_missing = obtain_objects_from_message(message)
        objects_script = [x[0].replace('_', '') for x in script_content.obtain_objects()]
        intersection_objects = list(set(objects_script).intersection(objects_missing))
        message_missing = 'Some objects appearing in the script were not properly initialized'
        if len(intersection_objects) > 0:
            return {'succes_expand': False, 
                    'message': (message_missing, intersection_objects)}
        else:

            comm.add_character(character)
            print(output)

            # use custom id system
            s, env_graph = comm.environment_graph()
            script = process_action(script, init_graph, env_graph)

            # render only for char0

            script = [ ('<char0> ' + elem).lower() for elem in script ]
            print("script: ", script)

            s, home_capture_camera_ids = comm.home_capture_camera_ids()

            camera_modes = [ str(i) for i in home_capture_camera_ids ]

            print('cameras: {}'.format(camera_modes))

            success, message_exec = comm.render_script(script, recording=True, frame_rate=5,
            image_synthesis=['rgb', 'point_cloud', 'seg_class', 'seg_inst'],
            image_width=300, image_height=200, processing_time_limit=10000,
            output_folder=output, camera_mode=camera_modes, find_solution=False)
            
            if success:
                return {'success_expand': True, 'success_exec': True, 'message': (message_exec, None)}
            else:
                return {'success_expand': True, 
                        'success_exec': False, 
                        'message': (message_exec, None)}

    



