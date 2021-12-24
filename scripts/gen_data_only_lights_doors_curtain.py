class DataGenerator():
    def __init__(self):
        self.doors_states = [1, 1, 1]  # zhuoyue: all opened at the beginning
        self.lights_states = [1, 1, 1, 1, 1]
        self.curtain_state = 1

    def gen_light(self, id):
        idx = id - 1
        on_off_str = "[SwitchOff]" if self.lights_states[idx] else "[SwitchOn]"
        self.lights_states[idx] = 0 if self.lights_states[idx] else 1
        return ['[Walk] <lightswitch> ({})'.format(id),
                '[Find] <lightswitch> ({})'.format(id),
                '{} <lightswitch> ({})'.format(on_off_str, id)]

    def gen_door(self, id):
        idx = id - 1
        open_close_str = "[Close]" if self.doors_states[idx] else "[Open]"
        self.doors_states[idx] = 0 if self.doors_states[idx] else 1
        return ['[Walk] <door> ({})'.format(id),
                '[Find] <door> ({})'.format(id),
                '{} <door> ({})'.format(open_close_str, id)]

    def gen_curtain(self, id):
        open_close_str = "[Close]" if self.curtain_state else "[Open]"
        self.curtain_state = 0 if self.curtain_state else 1
        return ['[Walk] <Curtains> ({})'.format(id),
                '[Find] <Curtains> ({})'.format(id),
                '{} <Curtains> ({})'.format(open_close_str, id)]


if __name__ == '__main__':
    from random import randrange

    g = DataGenerator()
    actions = []
    num_actions = 30  # we can define how many random actions we want
    # switch off all lights and close all doors at the beginning, so we can register each door/lights with unique ids.
    for i_light in range(1, 6):  # 1,2,3,4,5
        actions.extend(g.gen_light(i_light))
    for i_door in range(1, 4):  # 1,2,3
        actions.extend(g.gen_door(i_door))

    for i in range(num_actions):
        random_id = randrange(1, 10)  # will generate 1,2,3,4,5,6,7,8,9 randomly
        if random_id == 9:  # curtain
            actions.extend(g.gen_curtain(1))
        elif random_id > 5:
            random_id = random_id - 5
            actions.extend(g.gen_door(random_id))
        else:
            actions.extend(g.gen_light(random_id))

    unique_id = 0
    textfile = open("../data/only_lights_doors_curtain/{}.txt".format(unique_id), "w")
    for element in actions:
        textfile.write(element + "\n")
    textfile.close()
