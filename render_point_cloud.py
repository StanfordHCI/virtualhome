
import open3d as o3d

# df_pos = pd.read_csv("./data/unity_complete_pos_data.csv", sep=',', header=None)

# df_rgba = pd.read_csv("./data/unity_complete_rgba_data.csv", sep=',', header=None)

# print(df_pos)
# print(df_rgba)

# df_pos += 0.01 * np.random.randn(df_pos.shape[0], df_pos.shape[1])

# pos = df_pos.to_numpy()
# rgba = df_rgba.to_numpy()

# rgb = rgba[:, 0:3]

# data = []

# assert rgb.shape[0] == pos.shape[0]

# for i in range(0, rgb.shape[0]):
#   data.append(list(pos[i, :])+ list(rgb[i, :]))

# #  print("Shape: ", data.shape)

# with open("./data/point_cloud_data.xyzrgb", 'w') as ofs:
#   for item in data:
#     ofs.write("{} {} {} {} {} {}\n".format(item[0], item[1], item[2], item[3], item[4], item[5])) 


# point_cloud = df.to_numpy()
# # im = np.fromfile("./data/data")
# # print(im)

# # num_points = 10000
# # point_cloud = np.random.uniform(0, 10, 3 * num_points).reshape(num_points, 3)
# # print(point_cloud)
# # print(point_cloud[:, 0:6].shape)
# pcd = o3d.geometry.PointCloud()
# pcd.points = o3d.utility.Vector3dVector(point_cloud[:, 0:6])

pcd = o3d.io.read_point_cloud("./data/point_cloud_data.xyzrgb")
# o3d.visualization.draw(pcd)
# Zhuoyue: the draw function doesn't work..
o3d.visualization.draw_geometries([pcd])