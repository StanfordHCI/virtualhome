from simulation.unity_simulator import comm_unity
import numpy as np
import open3d as o3d

mode = 'manual'  # auto / manual
if mode == 'auto':
    exec_file = '../simulation/macos_exec'
    comm = comm_unity.UnityCommunication(file_name=exec_file)
else:
    comm = comm_unity.UnityCommunication()

s, point_cloud = comm.point_cloud()

points = []
for obj in point_cloud:

    local_points = []
    for point_collection in obj['points']:
        local_points.append(point_collection)

    points += local_points

point_cloud = np.array(points)

# print(point_cloud)

pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(point_cloud)
# o3d.visualization.draw(pcd)
# Zhuoyue: the draw function doesn't work..
o3d.visualization.draw_geometries([pcd])
