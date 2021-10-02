from simulation.unity_simulator import comm_unity
from PIL import Image
import numpy as np
import open3d as o3d


def arr_to_numpy(arr):
    return np.array(arr).reshape(4, 4).T


def camera_to_point_cloud(camera_index, camera_count, cameras, images):
    camera = cameras[camera_index]
    # world_to_camera_matrix = arr_to_numpy(camera['world_to_camera_matrix'])
    camera_to_world_matrix = arr_to_numpy(camera['camera_to_world_matrix'])
    proj_matrix = arr_to_numpy(camera['projection_matrix'])

    # print(world_to_camera_matrix)
    # print(np.linalg.inv(world_to_camera_matrix))
    print(camera_to_world_matrix)
    print(camera_to_world_matrix.dot(np.array([0, 0, 0, 1])))

    # converts from camera's projection space to world space coords
    proj_inv_matrix = np.linalg.inv(proj_matrix)
    # print(proj_inv_matrix)

    # s, graph = comm.environment_graph()
    # nodes = graph['nodes']

    # for i in range(0, 10):
    #     print(nodes[i])

    print("Number of images:", camera_count)
    image = np.array(images[camera_index])
    im = image[:, :, 0]

    width = im.shape[1]
    height = im.shape[0]

    print("Width: {}, Height: {}".format(width, height))

    transform = np.array([-width / 2, -height / 2])
    print("Transform:", transform)

    focus = -camera_to_world_matrix.dot(proj_inv_matrix.dot(np.array([0.0, 0.0, 1.0, 1.0])))
    focus = focus[0:3]
    focus = focus / np.linalg.norm(focus)

    print("Forward {}: {}".format(camera_index, camera['forward']))
    print("Focus:", focus)

    print("Depth image shape:", im.shape)
    max = np.max(im)
    min = np.min(im)
    im = im / max
    im = im * 255

    point_cloud = []
    for x in range(0, width):
        x_int = x
        for y in range(0, height):
            y_int = y
            x_float = 2 * (x / width) - 1
            y_float = 2 * (y / height) - 1
            uv = np.array([x_float, y_float, 1.0, 1.0])
            world_coord = -camera_to_world_matrix.dot(proj_inv_matrix.dot(uv))
            world_coord = world_coord[0:3] / np.linalg.norm(world_coord[0:3])

            depth = im[y_int, x_int]
            point_cloud.append(world_coord * depth)

    im = Image.fromarray(im)
    im.show()

    return point_cloud


def main():
    mode = 'manual'  # auto / manual
    if mode == 'auto':
        exec_file = '../simulation/macos_exec'
        comm = comm_unity.UnityCommunication(file_name=exec_file)
    else:
        comm = comm_unity.UnityCommunication()

    env_id = 0  # env_id ranges from 0 to 6
    comm.reset(env_id)

    s, camera_count = comm.camera_count()
    indices = [i for i in range(0, camera_count)]
    s, images = comm.camera_image(indices, mode='rgb')
    # s, images = comm.camera_image(indices, mode='depth')
    # s, images = comm.camera_image(indices, mode='point_cloud')
    # s, images = comm.camera_image(indices, mode='seg_class')
    s, cameras = comm.camera_data(indices)
    # print(cameras[0])

    point_cloud = camera_to_point_cloud(1, camera_count, cameras, images)
    # point_cloud = point_cloud + camera_to_point_cloud(1, camera_count, cameras, images)
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(point_cloud)

    # o3d.visualization.draw(pcd)
    # Zhuoyue: the draw function doesn't work..
    o3d.visualization.draw_geometries([pcd])


if __name__ == "__main__":
    main()

# s, images = comm.camera_image([i for i in range (0, camera_count)])

# Image.fromarray(images[0]).show()
