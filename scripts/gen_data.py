import os
import re
import random
from bs4 import BeautifulSoup
from html_data import return_html


class DataGenerator():
    def __init__(self, path):
        self.path = path
        # self.available_actions = ["walk", "run", "walktowards", "walkforward",
        #                           "turnleft", "turnright", "sit", "standup", "grab",
        #                           "open", "close", "put", "putin", "switchon", "switchoff",
        #                           "drink", "touch", "lookat"]  # it's weird that it doesn't support "find"

        # TODO
        # it's weird that it doesn't support "find"
        # also, 2 we don't know if something is grabbed twice, os I just remove it.
        # also PUTIN has error without grab also Drink, also sit...
        # "Script is not executable, since Too many things on <chair> (1012) when executing "[SIT] <chair> (1012) [92]""
        #  3 Script is not executable, since <character> (1) does not face <couch>
        #  (1006) when executing "[LOOKAT] <couch> (1006) [37]"
        # so I remove the lookat
        self.available_actions = ["walk", "run", "walktowards", "walkforward",
                                  "turnleft", "turnright", "standup",
                                  "open", "close", "put", "switchon", "switchoff", "touch", "find"]

        self.available_rooms = ['home_office', 'kitchen', 'living_room', 'bathroom',
                                'dining_room', 'bedroom', 'kids_bedroom', 'entrance_hall']

        self.available_rooms_real = ['kitchen', 'living_room', 'bathroom', 'bedroom']
        self.doors_states = [1, 1, 1, 1]  # zhuoyue: all opened at the beginning
        self.lights_states = [1, 1, 1, 1]
        self.equivalent_rooms = {
            "kitchen": "dining_room",
            "dining_room": "kitchen",
            "entrance_hall": "living_room",
            "home_office": "living_room",
            "living_room": "home_office",
            "kids_bedroom": "bedroom"
        }
        # this will keep track of all the open and close states of appliances (such as the fridge)
        # so we don't open something when it's already opened (would cause trouble on the Unity side)
        self.open_close_dic = {}
        self.switch_on_off_dic = {}
        self.actions = []
        self.curr_room = ''

    def deal_with_room(self, obj_match, line):
        """
        whenever we see a room, we turn on the light/door for the room we are heading to
        turn off the light/door for the room we are leaving.

        TODO:
        1. if the original script already has switchOn light, it might get switch on twice
        2. if it says go to "sofa", we would have no idea which room the sofa is in.
        I guess we can just track as much as we can, even if the character go to some other rooms in this process
        3. For door if the character pass the kitchen to reach bedroom,
        so the door is with the kitchen then this won't work?
        """
        if obj_match in ['home_office', 'entrance_hall', 'kids_bedroom', 'dining_room']:
            obj_match = self.equivalent_rooms[obj_match]
        room_id_old = self.available_rooms_real.index(self.curr_room)
        room_id_new = self.available_rooms_real.index(obj_match)
        # +10 because we dont want to mix the default id = 1
        if self.doors_states[room_id_old] is 1:
            turnoff_light = ['[Walk] <lightswitch> ({})'.format(room_id_old + 10),
                             '[Find] <lightswitch> ({})'.format(room_id_old + 10),
                             '[SwitchOff] <lightswitch> ({})'.format(room_id_old + 10)]
            self.lights_states[room_id_old] = 0
        else:
            turnoff_light = []

        if self.lights_states[room_id_new] is 0:
            turnon_light = ['[Walk] <lightswitch> ({})'.format(room_id_new + 10),
                            '[Find] <lightswitch> ({})'.format(room_id_new + 10),
                            '[SwitchOn] <lightswitch> ({})'.format(room_id_new + 10)]
            self.lights_states[room_id_new] = 1
        else:
            turnon_light = []
        if self.doors_states[room_id_old] is 1:
            close_door = ['[Walk] <door> ({})'.format(room_id_old + 10),
                          '[Find] <door> ({})'.format(room_id_old + 10),
                          '[Close] <door> ({})'.format(room_id_old + 10)]
            self.doors_states[room_id_old] = 0
        else:
            close_door = []

        if self.doors_states[room_id_new] is 0:
            open_door = ['[Walk] <door> ({})'.format(room_id_new + 10),
                         '[Find] <door> ({})'.format(room_id_new + 10),
                         '[Open] <door> ({})'.format(room_id_new + 10)]
            self.doors_states[room_id_new] = 1
        else:
            open_door = []
        # update the current room
        self.curr_room = obj_match
        temp_lst = turnoff_light + close_door + open_door + [line.strip()] + turnon_light
        self.actions.extend(temp_lst)
        return

    # def deal_with_on_off(self, dic, obj, action):
    #     """
    #     # make sure don't open something when it's already opened, or close twice
    #     """
    #     if obj in dic:
    #         if dic[obj] == action:
    #             continue
    #     else:
    #         return action

    def read_action_file(self, action_file: str):
        with open(action_file, 'r') as obj:
            for line in obj:
                # get the action string
                obj_match = line[line.find("<") + 1:line.find(">")].lower()
                action_match = line[line.find("[") + 1:line.find("]")].lower()
                # if not action_match or not obj_match:
                if obj_match == action_match:  # if they are equal, this line is a text line, not command
                    continue
                if action_match in self.available_actions:
                    # 1. deal with object
                    if obj_match in self.available_rooms:
                        self.deal_with_room(obj_match, line)
                    # Script is not executable, since <sink> (156)
                    # can not be opened when executing "[OPEN] <sink> (156) [97]"
                    if obj_match == 'sink' or obj_match == 'fridge':
                        # zhuoyue: if it's 'fridge'
                        # (1) the humanoid is gonna be stuck in the fridge
                        # (2) all bookshelves and TV Stands will have offset to the wall
                        continue
                    # <dishwasher> (166) is still on when executing "[OPEN] <dishwasher> (166) [330]"
                    # if obj_match == 'dishwasher' and \
                    #         (action_match == 'open' or action_match == 'close'):
                    #     continue

                    if obj_match not in html_list:
                        continue
                    # does not have a switch when executing "[SWITCHON] <filing_cabinet> (1008) [37]"
                    if obj_match in ['kitchen_cabinet',
                                     'cupboard',
                                     'filing_cabinet'] and action_match in ['switchon',
                                                                            'switchoff']:  # they don't have switch on
                        continue
                    if obj_match == 'lightswitch':  # make sure the lights are not switch twice
                        id_match = int(line[line.find("(") + 1:line.find(")")])
                        if action_match == 'switchon' and self.lights_states[id_match] == 1:
                            continue
                        elif action_match == 'switchoff' and self.lights_states[id_match] == 0:
                            continue
                    # 2. deal with action
                    if action_match == 'standup':
                        continue  # just remove the existed standup, so it won't duplidate with our code
                    elif action_match == 'sit':
                        self.actions.append('[Standup]')
                    elif action_match == 'switchon':
                        if obj_match in self.switch_on_off_dic:
                            if self.switch_on_off_dic[obj_match] == 1:
                                continue  # skip this line if the target appliance is already opened
                        self.switch_on_off_dic[obj_match] = 1
                    elif action_match == 'switchoff':
                        if obj_match in self.switch_on_off_dic:
                            if self.switch_on_off_dic[obj_match] == 0:
                                continue
                        self.switch_on_off_dic[obj_match] = 0
                    elif action_match == 'open':
                        if obj_match in self.open_close_dic:
                            if self.open_close_dic[obj_match] == 1:
                                continue
                        self.open_close_dic[obj_match] = 1
                    elif action_match == 'close':
                        if obj_match in self.open_close_dic:
                            if self.open_close_dic[obj_match] == 0:
                                continue
                        self.open_close_dic[obj_match] = 0
                    elif action_match == 'find':
                        self.actions.append('[Walk] <{}> (1)'.format(obj_match))
                    self.actions.append(line.strip())  # only add lines that uses available actions
        return self.actions

    def run(self, selected_num_files, total_num_files, curr_room):
        """
        Bascially we just make sure the script start with wakeup and end with sleep, we randomly pick
        `selected_num_files` of scripts for the middle, adding doors/lights along the way.

        num_of_files: number of scripts you want to combine
        """
        # re-initialize
        self.actions = []
        self.curr_room = curr_room
        self.doors_states = [1, 1, 1, 1]
        self.lights_states = [1, 1, 1, 1]
        # Bed removed....Script is not executable, since <character> (1)
        # is not close to <bed> (284) when executing "[FIND] <bed> (284) [2]"
        # '[Find] <bed> (1)',
        wakeup = [
            '[Walk] <bedroom> (1)',
        ]
        # they don't support lie down on the bed...
        sleep = [
            '[Walk] <bedroom> (1)',
        ]
        self.actions.extend(wakeup)
        # walk through the path and get files
        idx = 0
        indices = random.sample(range(0, total_num_files), selected_num_files)
        # indices = [0, 1, 2]
        # zhuoyue: I don't use random number on dirs directly because lots of dirs are empty
        for base, dirs, files in os.walk(self.path):
            if len(files) >= 1:
                # print('Looking in : ', base)
                for f in files:
                    if not f.startswith('.'):  # neglect files such as ".DS_Store"
                        path_to_file = os.path.join(base, f)
                        if idx in indices:
                            self.read_action_file(path_to_file)
                        idx += 1
        self.actions.extend(sleep)


if __name__ == '__main__':
    path = '../../augment_location/withoutconds/results_intentions_march-13-18'

    soup = BeautifulSoup(return_html(), "html.parser")
    html_list = []  # available objects
    for tag in soup.find_all():
        tag = str(tag)
        if tag.startswith('<td>') and tag != "<td> </td>" and tag != "<td>✅</td>":
            tag = tag[3:]  # remove the first "<tb>"
            item = tag[tag.find(">") + 1:tag.find("<")]
            html_list.append(item.lower())

    g = DataGenerator(path)
    for i in range(1):
        g.run(selected_num_files=10, total_num_files=1186, curr_room='bedroom')
        textfile = open("../data/gen/{}.txt".format(i), "w")
        for element in g.actions:
            textfile.write(element + "\n")
        textfile.close()
