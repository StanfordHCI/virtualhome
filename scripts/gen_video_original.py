# Generate video for a program. Make sure you have the executable open
from simulation.unity_simulator.comm_unity import UnityCommunication
from simulation.unity_simulator import utils_viz
from demo.utils_demo import *

#
# script = ['<char0> [Walk] <tv> (1)', '<char0> [switchon] <tv> (1)', '<char0> [Walk] <sofa> (1)',
#           '<char0> [Sit] <sofa> (1)', '<char0> [Watch] <tv> (1)']  # Add here your script


comm = UnityCommunication()


###### Task 1
comm.reset()
success, graph = comm.environment_graph()
door = find_nodes(graph, class_name='door')[0]
door['states'] = ['CLOSED']
success = comm.expand_scene(graph)
comm.add_character('Chars/Female1', initial_room="kitchen")
script_r1_to_r4 = [
    '<char0> [Walk] <bedroom> (346)',
    '<char0> [Open] <door> (47)',
    '<char0> [switchon] <light> (402)']  # Add here your script

comm.render_script(script_r1_to_r4, find_solution=False)
comm.reset()
comm.add_character('Chars/Female1', initial_room="bedroom")
script_r4_to_r1 = [
    '<char0> [Walk] <kitchen> (11)',
    '<char0> [Open] <door> (47)',
    '<char0> [switchon] <light> (58)']  # Add here your script

comm.render_script(script_r4_to_r1, find_solution=False)

# success, graph = comm.environment_graph()
# l1 = find_nodes(graph, class_name='lightswitch')[0]
# l4 = find_nodes(graph, class_name='lightswitch')[4]
# l1['states'] = ['OFF']
# l4['states'] = ['ON']
# success = comm.expand_scene(graph)

# success, graph = comm.environment_graph();
# fridge = find_nodes(graph, class_name='fridge')[0]
# fridge['states'] = ['OPEN']
# success = comm.expand_scene(graph)
#
# print('Generated, find video in simulation/unity_simulator/output/')

# success, message = comm.render_script(script=script,
#                                       processing_time_limit=60,
#                                       find_solution=False,
#                                       image_width=320,
#                                       image_height=240,
#                                       skip_animation=False,
#                                       recording=True,
#                                       save_pose_data=True,
#                                       file_name_prefix='relax')
# # Enter here the path to the video, it should be in the same location where you stored your executable
# path_video = "../simulation/Output/"
# utils_viz.generate_video(input_path=path_video, prefix='relax', output_path='.')
