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

print(g['nodes'])