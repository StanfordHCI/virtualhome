import torch
from torch.utils.data import Dataset, DataLoader
import os
from PIL import Image
import numpy as np
import cv2


def get_index_from_name(name):
    index_start = name.find('_')
    index_end = name.find('_', index_start + 1)
    index_str = name[index_start + 1:index_end]
    # print(index_str)
    index = int(index_str)
    return index


def filter_func(name):
    if name.find('Action') == 0:
        return True

    return False


def cmp_file_type(name):
    if name.find('rgb.png') > 0:
        return 1

    if name.find('seg_class.png') > 0:
        return 2

    if name.find('seg_inst.png') > 0:
        return 3

    return 4


def get_class_rgb_to_id_map():
    class_ids_path = "/Users/griffin/Stanford/LOA/summer/CURIS/virtualhome_unity/Assets/Resources/Data/class2rgb.txt"
    rgb_to_id = {}
    rgb_to_class = {}
    with open(class_ids_path) as ifs:
        line_num = 0
        for line in ifs:
            start_rgb = line.find('(')
            end_class = line.find(':')
            rgb = line[start_rgb:].strip()
            rgb_to_id[rgb] = line_num
            rgb_to_class[rgb] = line[:end_class]
            line_num += 1

    return rgb_to_id, rgb_to_class


class PointCloudDataset(Dataset):
    def __init__(self, data_dir) -> None:
        self.data_dir = data_dir
        files = os.listdir(data_dir)
        files = list(filter(filter_func, files))
        files = sorted(files, key=get_index_from_name)
        self.files = files
        self.rgb_to_id_map, self.rgb_to_class_map = get_class_rgb_to_id_map()

    def __len__(self):
        return len(self.files) // 4

    def __getitem__(self, idx):
        subset = self.files[4 * idx:4 * idx + 4]
        subset = sorted(subset, key=cmp_file_type)
        rgb, seg_class, seg_inst, point_cloud = subset
        print(rgb, seg_class, seg_inst, point_cloud)

        rgb_path = self.data_dir + "/" + rgb
        seg_class_path = self.data_dir + "/" + seg_class
        seg_inst_path = self.data_dir + "/" + seg_inst
        point_cloud_path = self.data_dir + "/" + point_cloud

        data = []
        with Image.open(rgb_path) as rgb_im:
            with Image.open(seg_class_path) as seg_class_im:
                with Image.open(seg_inst_path) as seg_inst_im:
                    # open cv uses BGR order
                    # thus depth is [z, y, x]
                    point_cloud_arr = cv2.imread(point_cloud_path, cv2.IMREAD_UNCHANGED)
                    rgb_arr = np.array(rgb_im)
                    seg_class_arr = np.array(seg_class_im)
                    seg_inst_arr = np.array(seg_inst_im)

                    # rgb_im.show()

                    assert point_cloud_arr.shape[0] == rgb_arr.shape[0]
                    assert rgb_arr.shape[0] == seg_class_arr.shape[0]
                    assert seg_inst_arr.shape[0] == seg_class_arr.shape[0]
                    assert point_cloud_arr.shape[1] == rgb_arr.shape[1]
                    assert rgb_arr.shape[1] == seg_class_arr.shape[1]
                    assert seg_class_arr.shape[1] == seg_inst_arr.shape[1]

                    height = point_cloud_arr.shape[0]
                    width = point_cloud_arr.shape[1]

                    for row in range(0, height):
                        for col in range(0, width):

                            # open cv uses BGR order
                            # thus depth is [z, y, x]
                            # however use BGR ordering because of render texture in unity
                            x = point_cloud_arr[row, col, 0]
                            y = point_cloud_arr[row, col, 1]
                            z = point_cloud_arr[row, col, 2]
                            r = rgb_arr[row, col, 0] / 255
                            g = rgb_arr[row, col, 1] / 255
                            b = rgb_arr[row, col, 2] / 255

                            rgb_encoded_id = "({},{},{})".format(seg_class_arr[row, col, 0], seg_class_arr[row, col, 1],
                                                                 seg_class_arr[row, col, 2])

                            if rgb_encoded_id not in self.rgb_to_id_map:
                                continue

                            class_id = self.rgb_to_id_map[rgb_encoded_id]
                            # print(class_id)

                            instance_id = int(seg_inst_arr[row, col, 0]) + int(seg_inst_arr[row, col, 1]) + int(
                                seg_inst_arr[row, col, 2])

                            # data.append("{} {} {} {} {} {}\n".format(x, y, z, r, g, b))
                            # Final data format
                            # data.append("{} {} {} {} {} {} {} {}\n".format())
                            data.append([x, y, z, r, g, b, class_id, instance_id])

                    # TODO don't use constant
                    data_len = len(data)
                    while data_len < 60000:
                        data.append([0, 0, 0, 0, 0, 0, 0, 0])
                        data_len += 1

                    data = np.array(data)
                    # print(point_cloud_arr.shape, rgb_arr.shape, seg_class_arr.shape, seg_inst_arr.shape)
                    # print(data.shape)
        return data


class S3DISDataset(PointCloudDataset):
    def __init__(self, data_dir) -> None:
        super().__init__(data_dir)

        # map from s3dis to synonymous virtual home classes
        # TODO fill out s3dis_virtual_home_class_synonyms
        self.s3dis_virtual_home_class_synonyms = {
            "ceiling": [],
            "floor": [],
            "wall": [],
            "beam": [],
            "column": [],
            "window": [],
            "door": [],
            "table": [],
            "chair": [],
            "sofa": [],
            "bookcase": [],
            "board": [],
            "clutter": []
        }

        # TODO abstract these two sections into another class
        # build map from virtual home class to s3dis class
        self.virtual_home_to_s3dis_class = {}
        for s3dis_class in self.s3dis_virtual_home_class_synonyms.keys():
            for virtual_home_synonym in self.s3dis_virtual_home_class_synonyms[s3dis_class]:
                self.virtual_home_to_s3dis_class[virtual_home_synonym] = s3dis_class

        print("Virtual home to s3dis class mapping: ", self.virtual_home_to_s3dis_class)
        self.rgb_to_id_map = {}
        for rgb_id in self.rgb_to_class_map.keys():
            virtual_home_class = self.rgb_to_class_map[rgb_id]

            if virtual_home_class in self.virtual_home_to_s3dis_class:
                self.rgb_to_id_map[rgb_id] = self.virtual_home_to_s3dis_class[virtual_home_class]
            else:
                self.rgb_to_id_map[rgb_id] = -100

        # print(self.rgb_to_id_map)


class ScannetDataset(PointCloudDataset):
    def __init__(self, data_dir) -> None:
        super().__init__(data_dir)

        # map from scannets classes to synonymous virtual home classes
        # TODO fill out scannet_virtual_home_class_synonyms
        self.scannet_virtual_home_class_synonyms = {
            "wall": [],
            "chair": [],
            "floor": [],
            "table": [],
            "door": [],
            "couch/sofa": [],
            "cabinet": [],
            "shelf": [],
            "desk": [],
            "(office)chair": [],
            "bed": [],
            # TODO fix "?"
            "?": [],
            "sink": [],
            "window": [],
            "coffee table": [],
            "lamp": [],
            "TV": [],
            "nightstand": [],
            "dresser": [],
            "cushion": [],
        }

        self.virtual_home_to_scannet_class = {}
        for scannet_class in self.scannet_virtual_home_class_synonyms.keys():
            for virtual_home_synonym in self.scannet_virtual_home_class_synonyms[scannet_class]:
                self.virtual_home_to_scannet_class[virtual_home_synonym] = scannet_class

        print("Virtual home to scannet class mapping: ", self.virtual_home_to_scannet_class)
        self.rgb_to_id_map = {}
        for rgb_id in self.rgb_to_class_map.keys():
            virtual_home_class = self.rgb_to_class_map[rgb_id]

            if virtual_home_class in self.virtual_home_to_scannet_class:
                self.rgb_to_id_map[rgb_id] = self.virtual_home_to_scannet_class[virtual_home_class]
            else:
                self.rgb_to_id_map[rgb_id] = -100

        # print(self.rgb_to_id_map)


def main():
    output_dir = '/Users/griffin/stanford/LOA/summer/CURIS/virtualhome_unity/Output/script/0'
    ds = PointCloudDataset(output_dir)
    s3dis_ds = S3DISDataset(output_dir)
    scannet_ds = ScannetDataset(output_dir)

    print(s3dis_ds[0].shape)
    scannet_ds[0]

    # train_dataloader = DataLoader(ds, batch_size=16, shuffle=True)
    # train_features = next(iter(train_dataloader))
    # print(f"Feature batch shape: {train_features.size()}")
    # # # ds[0]
    # # for i in range(0, len(ds)):
    # #   print("loading frame {}".format(i))
    # #   ds[i]
    # # # ds[90]


if __name__ == "__main__":
    main()
