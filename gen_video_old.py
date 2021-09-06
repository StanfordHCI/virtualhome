from simulation.unity_simulator import comm_unity

print("Starting Unity server...")
mode = 'manual' # auto / manual
if mode == 'auto':
    exec_file = '../simulation/macos_exec'
    comm = comm_unity.UnityCommunication(file_name=exec_file)
else:
    comm = comm_unity.UnityCommunication(timeout_wait=5*60)
print("Unity server running")

comm.reset(0)
comm.add_character('Chars/Female2')

s, g = comm.environment_graph()

# Get nodes for salmon and microwave
salmon_id = [node['id'] for node in g['nodes'] if node['class_name'] == 'towel'][0]
microwave_id = [node['id'] for node in g['nodes'] if node['class_name'] == 'microwave'][0]

# Put salmon in microwave
script = [
    '<char0> [walk] <salmon> ({})'.format(salmon_id),
    '<char0> [grab] <salmon> ({})'.format(salmon_id),
    '<char0> [open] <microwave> ({})'.format(microwave_id),
    '<char0> [putin] <salmon> ({}) <microwave> ({})'.format(salmon_id, microwave_id),
    '<char0> [close] <microwave> ({})'.format(microwave_id)
]

s, num_cameras = comm.camera_count()

camera_modes = [ str(i) for i in range(num_cameras)]

print("reset 0 cameras: ", camera_modes, num_cameras)

s, home_capture_camera_ids = comm.home_capture_camera_ids()

print("reset 0 home_capture_camera_ids:", home_capture_camera_ids)

camera_modes = [ str(i) for i in home_capture_camera_ids ]

# comm.reset(1)
# comm.add_character('Chars/Female2')

# s, num_cameras = comm.camera_count()

# camera_modes = [ str(i) for i in range(num_cameras)]

# print("reset 1 cameras:", camera_modes, num_cameras)

# s, home_capture_camera_ids = comm.home_capture_camera_ids()

# print("reset 1 home_capture_camera_ids:", home_capture_camera_ids)

# camera_modes = [ str(i) for i in home_capture_camera_ids ]
import time

before = time.time()
success, message_exec = comm.render_script(script, recording=True, frame_rate=5, save_every_n_frames=100,
            image_synthesis=['rgb', 'point_cloud', 'seg_class', 'seg_inst'],
            image_width=640, image_height=400, processing_time_limit=20*60,
            output_folder='Output/0', camera_mode=camera_modes, find_solution=False, skip_animation=True)
after = time.time()
diff = after - before
print("time to complete:", diff)


# comm.render_script(script, recording=True, frame_rate=5,
# image_synthesis=['rgb', 'point_cloud', 'seg_class', 'seg_inst'],
# image_width=300, image_height=200, processing_time_limit=10000,
# output_folder='Output/1')

# import argparse
# import os
# import re
# import pprint
# import json
# import time

# GRAPH_PATH_START = "init_and_final_graphs" #subdirectory of root where graphs are saved

# # regular expression to get actions
# re_compiled = re.compile("^\[.+\] <[a-zA-Z_]+> \([0-9]\.[0-9]+\)(| <[a-zA-Z_]+> \([0-9]\.[0-9]+\))$")

# # gets the step type
# re_step_type = re.compile("\[.+\]")

# # gets step itmes (type and target id)
# re_step_items = re.compile("<[a-zA-Z_]+> \([0-9]\.[0-9]+\)")

# # gets step type
# re_object_type = re.compile("<[a-zA-Z_]+>")

# # gets step obj id 
# re_object_id = re.compile("\([0-9]\.[0-9]+\)")


# def read_action_file(action_file: str):
#     actions = []
#     with open(action_file, 'r') as action_ifs:
#         for line in action_ifs:
#             match = re_compiled.match(line.strip())
#             if match:
#                 actions.append(match.group())

#     return actions


# def read_env_graph(action_dir: str, action: str):
#     # replace action path with graph path
#     first_slash = action.find('/')

#     # replace .txt with .json
#     graph_path = GRAPH_PATH_START + action[first_slash:-3] + "json"
#     graph_path = os.path.join(action_dir, graph_path)

#     assert os.path.isfile(graph_path)

#     print("graph path:", graph_path)
#     with open(graph_path, 'r') as graph_ifs:
#         return json.load(graph_ifs)['init_graph']

# # merges the existing environment graph
# # with a new graph ensuring no conflicting ids
# def merge_env_graph(new_graph, comm: comm_unity.UnityCommunication):
#     s, old_graph = comm.environment_graph()
#     assert s == True

#     ids = [ node['id'] for node in old_graph['nodes']]
#     ids.sort()

#     max_id = ids[-1]
#     print("max_id={}".format(max_id))

#     new_ids = [ node['id'] for node in new_graph['nodes']]
#     new_ids.sort()

#     # map each id to a new id that is compatible with old graph
#     id_to_id = {}
#     num_new_ids = len(new_ids)
    
#     new_id = max_id + 1
#     for i in range(num_new_ids):
#         id_to_id[new_ids[i]] = new_id
#         new_id += 1

#     for node in new_graph['nodes']:
#         node['id'] = id_to_id[node['id']]

#     for edge in new_graph['edges']:
#         edge['from_id'] = id_to_id[edge['from_id']]
#         edge['to_id'] = id_to_id[edge['to_id']]
    
#     [old_graph['nodes'].append(node) for node in new_graph['nodes']]
#     [old_graph['edges'].append(edge) for edge in new_graph['edges']]

#     return old_graph
    


# def process_action(action, graph, env_graph):
#     step_obj_id_to_type = {}
#     step_obj_id_to_graph_id = {}

#     step_pipeline = []
#     for step in action:
#         step_type = re_step_type.match(step).group()[1:-1]
        
#         print("step_type: {}".format(step_type))

#         step_items = []
        
#         while True:
#             step_item = re_step_items.search(step)
            
#             if step_item:
#                 step_items.append(step_item.group())
#                 step = step[step_item.end():]
#             else:
#                 break

#         print("step_items:", step_items)

#         pipeline_item = { 'step_type': step_type, 'objects': []}
#         for step_item in step_items:
#             object_type = re_object_type.match(step_item).group()[1:-1]
#             print('object_type:', object_type)
#             object_id = re_object_id.search(step_item).group()[1:-1]
#             print('object_id:', object_id)

#             if object_id not in step_obj_id_to_type:
#                 step_obj_id_to_type[object_id] = object_type

#             pipeline_item['objects'].append({'object_type': object_type, 'object_id': object_id})

#         step_pipeline.append(pipeline_item)
    
#     # pprint.pprint(step_pipeline)

#     for obj_id in step_obj_id_to_type:
#         obj_type = step_obj_id_to_type[obj_id]
#         # print(obj_id, obj_type)
        
#         node = next((n for n in graph['nodes'] if n['class_name'] == obj_type))
        
#         if obj_id not in step_obj_id_to_graph_id:
#             step_obj_id_to_graph_id[obj_id] = node['id']
#             # print(obj_id, node['id'])

#     proc_steps = []
#     for pipeline_item in step_pipeline:
#         step_string = "[{}]".format(pipeline_item['step_type'])
        
#         for object_data in pipeline_item['objects']:
#             object_type = object_data['object_type']

#             items = [item for item in env_graph['nodes'] if item['class_name'] == object_type]
#             print("Found {} items of type {} in env_graph".format(len(items), object_type))

#             object_id = object_data['object_id']
#             step_string += " <{}> ({})".format(object_type, step_obj_id_to_graph_id[object_id])
            
#         proc_steps.append(step_string)
    
#     return proc_steps


# def render_action(proc_action, action_file: str, graph, scene_num, comm: comm_unity.UnityCommunication):
#     assert scene_num >= 0 and scene_num < 7

#     last_slash = action_file.rfind("/")
#     file_name = action_file[last_slash + 1:]
#     output = 'Output/{}_{}'.format(file_name, scene_num)

#     s, message = comm.expand_scene(graph)
#     print("expand scene message:", message)

#     assert s == True

#     s, home_capture_camera_ids = comm.home_capture_camera_ids()

#     print("home_capture_camera_ids:", home_capture_camera_ids)

#     camera_modes = [ str(i) for i in home_capture_camera_ids ]

#     print("saving rendered result to {}".format(output))

#     before = time.time()
#     # comm.render_script(proc_action, recording=True, frame_rate=5,
#     # image_synthesis=['rgb', 'point_cloud', 'seg_class', 'seg_inst'],
#     # image_width=300, image_height=200, processing_time_limit=10000,
#     # output_folder=output, camera_mode=camera_modes)
#     after = time.time()
#     diff = after - before

#     print("time to complete: {}s".format(diff))


# def main():
#     parser = argparse.ArgumentParser(description="Generates video sequence for a given action_dir and action")
#     parser.add_argument("--action_dir", help="Directory containing actions")
#     parser.add_argument("--action", help="Path from action_dir to action file")
#     args = parser.parse_args()
#     action = args.action
#     action_dir = args.action_dir

#     assert action
#     assert action_dir

#     action_file = os.path.join(action_dir, action)
    
#     print("action_dir={}\naction={}\naction_file={}\n".format(action_dir, action, action_file))

#     assert os.path.isdir(action_dir)
#     assert os.path.isfile(action_file)

#     print("Starting Unity server...")
#     mode = 'manual' # auto / manual
#     if mode == 'auto':
#         exec_file = '../simulation/macos_exec'
#         comm = comm_unity.UnityCommunication(file_name=exec_file)
#     else:
#         comm = comm_unity.UnityCommunication(timeout_wait=5*60)
#     print("Unity server running")

#     scene_num = 0

#     print("Resetting scene: scene_num={}".format(scene_num))
#     s = comm.reset(scene_num)

#     print("Getting environment graph")
#     s, env_graph = comm.environment_graph()

#     # pprint.pprint([ node for node in old_graph['nodes'] if node['category'] == "Rooms"])

#     print("reading action file")
#     unproc_action = read_action_file(action_file)

#     print("reading environment graph from file")
#     graph = read_env_graph(action_dir, action)

#     comm.expand_scene(graph)

#     # hash_to_scene_num = get_default_env_graph_hashes()
#     # print("hash to scene num mapping: {}".format(hash_to_scene_num))

#     # graph_hash = get_env_graph_hash(graph)
#     # print("graph hash: {}".format(graph_hash))
    
#     # pprint.pprint([ node for node in graph['nodes'] if node['category'] == "Rooms"])

#     # print("merging environment graph with existing environment graph")
#     # graph = merge_env_graph(graph, comm)

#     # print("processing action")
#     # proc_action = process_action(unproc_action, graph, env_graph)
#     # pprint.pprint(proc_action)

#     # render_action(proc_action, action_file, graph, scene_num, comm)
    

if __name__ == "__main__":
    main()
