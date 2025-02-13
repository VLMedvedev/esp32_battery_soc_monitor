from constants import TOPIC_COMMAND_LEVEL_UP, TOPIC_COMMAND_LEVEL_DOWN
from configs.constants_saver import ConstansReaderWriter

def set_level(topic_command, level_type):
    file_config_name = "app_config"
    cr = ConstansReaderWriter(file_config_name)
    c_dict = cr.get_dict()
    print(c_dict)
    min_level = c_dict.get("OFF_LEVEL", 10)
    max_level = c_dict.get("ON_LEVEL", 98)
    const_dict = {'OFF_LEVEL': min_level,
                  'ON_LEVEL': max_level,
                  'MODE': 'AUTO',
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