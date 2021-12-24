# import torch

import numpy as np
import sys

import glob
import os

import open3d

import zmq
import json



# pred_frame_id = 99
# chunk_id = 0
# # path = '/chunk/%d-%d.npz' % (pred_frame_id, chunk_id)
# # print(path)
#
#
# for i in range(267):
#     print (i)
#     chunk_points = np.load('/Users/zhuoyuelyu/Downloads/chunk/%d-%d.npz' % (pred_frame_id, i))['arr_0']
#     chunk_cloud = open3d.geometry.PointCloud()
#     chunk_cloud.points = open3d.utility.Vector3dVector(chunk_points[:, :3])
#     chunk_cloud.colors = open3d.utility.Vector3dVector(chunk_points[:, 3:])
#     open3d.io.write_point_cloud('%s/%d.ply' % ('temp-zy-99', i), chunk_cloud)





from_ = '/Users/zhuoyuelyu/Documents/a-Stanford/StanfordHCI/virtualhome-11/Assets/ply-99'
to_ = '/Users/zhuoyuelyu/Documents/a-Stanford/StanfordHCI/virtualhome-11/Assets/ply-common'
import shutil, os
import time
print("Hi")
print("start copying")
for i in range(6):
    time.sleep(3)
    print(i)
    shutil.copy('%s/%d.ply' % (from_, i), to_)
