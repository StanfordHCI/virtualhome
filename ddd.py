#
from numpy import load
data = load('../scene_category_full.npy', allow_pickle=True)
# data = load('../synthetic/sentence_w2v_synthetic_test.npz', allow_pickle=True)
# data = load('../real/real_train.npz', allow_pickle=True)
# lst = data.files
for item in data:
    print(item)
    print(data[item])



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
