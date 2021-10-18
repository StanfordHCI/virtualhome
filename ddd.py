#
# from numpy import load
# data = load('../scene_category_full.npy', allow_pickle=True)
# # data = load('../synthetic/sentence_w2v_synthetic_test.npz', allow_pickle=True)
# # data = load('../real/real_train.npz', allow_pickle=True)
# # lst = data.files
# for item in data:
#     print(item)
#     print(data[item])
#


# # Zhuoyue: the following program is used to loop over the folders
# import os
#
# # HOME_FOLDER = '../programs_processed_precond_nograb_morepreconds/test'
# # HOME_FOLDER = '../programs_processed_precond_nograb_morepreconds/state_list'
# # folders = ["executable_programs", "state_list", "init_and_final_graphs", "withoutconds", "initstate"]
# folders = ["results_intentions_march-13-18",
#            "results_text_rebuttal_specialparsed_programs_turk_july",
#            "results_text_rebuttal_specialparsed_programs_turk_robot",
#            "results_text_rebuttal_specialparsed_programs_upworknturk_second",
#            "results_text_rebuttal_specialparsed_programs_upwork_kellensecond",
#            "results_text_rebuttal_specialparsed_programs_upwork_july",
#            "results_text_rebuttal_specialparsed_programs_turk_third"]
# for folder in folders:
#
#     print(folder)
#     HOME_FOLDER = '../augment_location/withoutconds/{}'.format(folder)
#     # HOME_FOLDER = '../programs_processed_precond_nograb_morepreconds/withoutconds/{}'.format(folder)
#
#     noOfFiles = 0
#     noOfDir = 0
#
#     for base, dirs, files in os.walk(HOME_FOLDER):
#         # print('Looking in : ', base)
#         for d in dirs:
#             noOfDir += 1
#         for f in files:
#             if not f.startswith('.'):  # neglect files such as ".DS_Store"
#                 noOfFiles += 1
#
#     print('Number of files', noOfFiles)
#     print('Number of Directories', noOfDir)
#     print('Total:', (noOfDir + noOfFiles))
#     print()

# HOME_FOLDER = '../programs_processed_precond_nograb_morepreconds/withoutconds/results_intentions_march-13-18'
#
# noOfFiles = 0
# noOfDir = 0
#
# for base, dirs, files in os.walk(HOME_FOLDER):
#     # print('Looking in : ', base)
#     for d in dirs:
#         noOfDir += 1
#     for f in files:
#         if not f.startswith('.'):  # neglect files such as ".DS_Store"
#             noOfFiles += 1
#
# print('Number of files', noOfFiles)
# print('Number of Directories', noOfDir)
# print('Total:', (noOfDir + noOfFiles))
# print()


# Zhuoyue: the following program is used to show all files under a specific dir
# from bs4 import BeautifulSoup
# import requests
#
# url = 'http://virtual-home.org/release/programs/'
# ext = 'zip'
#
#
# def listFD(url, ext=''):
#     page = requests.get(url).text
#     print(page)
#     soup = BeautifulSoup(page, 'html.parser')
#     return [url + '/' + node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext)]
#
#
# for file in listFD(url, ext):
#     print(file)


# zhuoyue: parse the String:
lst1 = [6.30453539, 6.90640354, 6.412946, 6.782587, 6.32956362, 6.883473, 6.437553, 6.80585766, 11.8651991, 2.82654834,
        6.30272436, 12.1245222, 10.14036, 6.778306, 1.329767, 10.442605, 13.5402708, 7.150556, 11.512001, 13.7682648,
        9.78351, 11.7793179, 6.70106649, 10.096694, 10.1551352, 10.3385229, 5.018119, 10.4572115, 13.364274, 5.60428524,
        10.0328741, 13.5952311, 6.21752357, 11.8435736, 4.44491959, 6.69953442, 12.3670683, 5.09739876, 11.5777407,
        12.6162806]

lst2 = [8.813534, 6.87189245, 2.05128813, 9.161589, 10.6975317, 3.2348268, 6.400514, 10.9860592, 14.2397451, 4.48285,
        3.89090633, 14.4565363, 14.195282, 4.62171459, 3.72489572, 14.4127426, 14.2605238, 7.66986036, 10.7669687,
        14.47718, 11.8336611, 11.0523205, 7.252627, 12.09387, 14.2071772, 14.2748289, 9.264297, 14.4246445, 17.707653,
        9.59446049, 14.0550432, 17.8826027, 10.5866814, 13.9954748, 6.206235, 10.8767643, 16.2236748, 6.68905926,
        13.7712431, 16.4144382]

lst3 = [8.998564, 7.68408966, 1.33825469, 9.33972549, 11.4879131, 2.8367672, 7.265598, 11.75706, 14.2840538, 5.29133034,
        2.95039773, 14.5001822, 14.7345324, 3.86341071, 4.666592, 14.9441462, 13.9259338, 7.4895587, 10.1834,
        14.1477137, 11.8362713, 10.4846458, 7.06168, 12.0964241, 14.7452812, 15.185668, 9.924765, 14.9549265, 18.528368,
        10.2336426, 14.9792538, 18.6956387, 11.3742256, 14.9463158, 7.18615055, 11.6447058, 17.1726074, 7.60703135,
        14.7365608, 17.3529415]

kkk = []
# for lst in [lst1, lst2, lst3]:
#     print(min(lst))
#     print(max(lst))
#     print()

for iii in lst3:
    kkk.append(int(iii <= 7))

print(kkk)
print(len(kkk))
print(lst3[-1])
