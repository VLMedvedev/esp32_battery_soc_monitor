from constants import (TOPIC_COMMAND_LEVEL_UP, TOPIC_COMMAND_LEVEL_DOWN,
                       RELE_BATTERY_LEVEL, RELE_ALWAYS_ON, RELE_ALWAYS_OFF)
from configs.constants_saver import ConstansReaderWriter

def set_rele_on_off(pin_rele, f_rele_is_on):
    print(f"change state rele {f_rele_is_on}")
    if f_rele_is_on:
        pin_rele.on()
    else:
        pin_rele.off()

def check_mode_and_calk_rele_state(rele_mode, off_level, on_level, f_rele_is_on, soc_level):
    f_change_rele_state = False
    old_f_is_on = f_rele_is_on
    if rele_mode == RELE_BATTERY_LEVEL:
        if soc_level <= off_level:
            f_rele_is_on = False
        if soc_level >= on_level:
            f_rele_is_on = True
    elif rele_mode == RELE_ALWAYS_OFF:
        print("mode 1 rele is off")
        f_rele_is_on = False
    elif rele_mode == RELE_ALWAYS_ON:
        print("mode 2 rele is on")
        f_rele_is_on = True
    if old_f_is_on != f_rele_is_on:
        f_change_rele_state = True
        print(f"change state rele {f_rele_is_on}")
    return f_change_rele_state, f_rele_is_on

def set_rele_mode_to_config_file(rele_mode, file_config_name):
    cr = ConstansReaderWriter(file_config_name)
    c_dict = cr.get_dict()
    print(c_dict)
    const_dict = {'MODE': rele_mode }
    cr.set_constants_from_config_dict(const_dict)
    cr.save_constants_to_file()
    return rele_mode

def set_level_to_config_file(topic_command, level_type, file_config_name):
    cr = ConstansReaderWriter(file_config_name)
    c_dict = cr.get_dict()
    print(c_dict)
    min_level = c_dict.get("OFF_LEVEL", 10)
    max_level = c_dict.get("ON_LEVEL", 98)
    const_dict = {'OFF_LEVEL': min_level,
                  'ON_LEVEL': max_level,
                  'MODE': 'RELE_BATTERY_LEVEL',
                  }
    if level_type == "ON_LEVEL":
        if topic_command == TOPIC_COMMAND_LEVEL_UP:
            max_level += 1
            if max_level > 100:
                max_level = 100
        elif topic_command == TOPIC_COMMAND_LEVEL_DOWN:
            max_level -= 1
            if max_level < min_level + 1:
                max_level = min_level + 1
        const_dict = {level_type : max_level}
    elif level_type == "OFF_LEVEL":
        if topic_command == TOPIC_COMMAND_LEVEL_UP:
            min_level += 1
            if min_level > max_level - 1:
                min_level = max_level - 1
        elif topic_command == TOPIC_COMMAND_LEVEL_DOWN:
            min_level -= 1
            if min_level < 0:
                min_level = 0
        const_dict = {level_type: min_level}
    cr.set_constants_from_config_dict(const_dict)
    cr.save_constants_to_file()

    return min_level, max_level

def set_wifi_mode(wifi_mode):

    return wifi_mode