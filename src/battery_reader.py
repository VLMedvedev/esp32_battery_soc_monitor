import random
from menu import PylontechMenu, print_dict

class Battery_reader:
    def __init__(self, manualBattcountLimit=3, group=0):
        self.pylon_menu = PylontechMenu(manualBattcountLimit, group)

    def get_charge_level(self):
        data = self.pylon_menu.process_command(key="status")
        #print(data)
        print_dict(data)
        try:
            charge_level = data['Remaining_%']
            print(f"charge level is {charge_level}")
        except:
            charge_level = 0
        charge_level = random.randrange(1, 100, 2)
        return charge_level


