from simulation.unity_simulator import comm_unity

mode = 'manual' # auto / manual
if mode == 'auto':
    exec_file = '../simulation/macos_exec'
    comm = comm_unity.UnityCommunication(file_name=exec_file)
else:
    comm = comm_unity.UnityCommunication()

s, graph = comm.environment_graph()
