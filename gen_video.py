from simulation.unity_simulator import comm_unity

mode = 'manual' # auto / manual
if mode == 'auto':
    exec_file = '../simulation/macos_exec'
    comm = comm_unity.UnityCommunication(file_name=exec_file)
else:
    comm = comm_unity.UnityCommunication(timeout_wait=2*60)

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

comm.reset(1)
comm.add_character('Chars/Female2')

s, num_cameras = comm.camera_count()

camera_modes = [ str(i) for i in range(num_cameras)]

print("reset 1 cameras:", camera_modes, num_cameras)

s, home_capture_camera_ids = comm.home_capture_camera_ids()

print("reset 1 home_capture_camera_ids:", home_capture_camera_ids)

camera_modes = [ str(i) for i in home_capture_camera_ids ]

# comm.render_script(script, recording=True, frame_rate=5,
# image_synthesis=['rgb', 'point_cloud', 'seg_class', 'seg_inst'],
# image_width=300, image_height=200, processing_time_limit=10000,
# output_folder='Output/0', camera_mode=camera_modes)

# comm.render_script(script, recording=True, frame_rate=5,
# image_synthesis=['rgb', 'point_cloud', 'seg_class', 'seg_inst'],
# image_width=300, image_height=200, processing_time_limit=10000,
# output_folder='Output/1')