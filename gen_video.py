from simulation.unity_simulator import comm_unity

mode = 'manual' # auto / manual
if mode == 'auto':
    exec_file = '../simulation/macos_exec'
    comm = comm_unity.UnityCommunication(file_name=exec_file)
else:
    comm = comm_unity.UnityCommunication()

comm.reset(0)
comm.add_character('Chars/Female2')

s, g = comm.environment_graph()

# Get nodes for salmon and microwave
print(g['nodes'])
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
comm.render_script(script, recording=True, frame_rate=5,
  image_synthesis=['rgb', 'point_cloud', 'seg_class', 'seg_inst'],
  image_width=300, image_height=200)