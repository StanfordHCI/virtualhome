class DataGenerator():
    def __init__(self):
        self.doors_states = [1, 1, 1]  # zhuoyue: all opened at the beginning
        self.lights_states = [1, 1, 1, 1, 1]
        # the list of rooms that would be triggered by light, in the order of R1,2,3,5,4
        self.light_action_rooms = ['[Walk] <kitchen> (1)',
                                   '[Walk] <living_room> (1)',
                                   '[Walk] <bedroom> (1)',  #
                                   '[Walk] <bathroom> (1)',
                                   '[Walk] <bedroom> (2)']  # this actually doesn't work..so I manually replace i in the obtain_snapshots of gen_snapshot.py
        self.door_action_rooms = ['[Walk] <kitchen> (1)',
                                  '[Walk] <bedroom> (1)',
                                  '[Walk] <bathroom> (1)']

    def gen_light(self, id):
        idx = id - 1

        on_off_str = "[SwitchOff]" if self.lights_states[idx] else "[SwitchOn]"
        self.lights_states[idx] = 0 if self.lights_states[idx] else 1
        return [self.light_action_rooms[idx],
                '[Walk] <lightswitch> ({})'.format(id),
                '[Find] <lightswitch> ({})'.format(id),
                '{} <lightswitch> ({})'.format(on_off_str, id)]

    def gen_door(self, id):
        idx = id - 1
        open_close_str = "[Close]" if self.doors_states[idx] else "[Open]"
        self.doors_states[idx] = 0 if self.doors_states[idx] else 1
        return [self.door_action_rooms[idx],
                '[Walk] <door> ({})'.format(id),
                '[Find] <door> ({})'.format(id),
                '{} <door> ({})'.format(open_close_str, id)]


if __name__ == '__main__':
    from random import randrange

    g = DataGenerator()
    actions = []
    num_actions = 34  # we can define how many random actions we want
    # switch off all lights and close all doors at the beginning, so we can register each door/lights with unique ids.
    for i_light in range(1, 6):  # 1,2,3,4,5
        actions.extend(g.gen_light(i_light))

    door_idx = 1
    for i in range(num_actions):
        if i == num_actions // 2:
            for i_door in range(1, 4):  # 1,2,3
                actions.extend(g.gen_door(i_door))
            continue
        random_id = randrange(1, 6)
        actions.extend(g.gen_light(random_id))

    unique_id = 100
    textfile = open("../data/only_lights_doors/{}.txt".format(unique_id), "w")
    for element in actions:
        textfile.write(element + "\n")
    textfile.close()
