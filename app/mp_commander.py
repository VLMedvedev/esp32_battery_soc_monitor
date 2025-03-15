from constants import (TOPIC_COMMAND_LEVEL_UP, TOPIC_COMMAND_LEVEL_DOWN,
                       RELE_BATTERY_LEVEL, RELE_ALWAYS_ON, RELE_ALWAYS_OFF,
                       WIFI_MODE_OFF, WIFI_MODE_AP,WIFI_MODE_CLIENT,
                       TOPIC_COMMAND_SCAN_CAN)
from configs.constants_saver import ConstansReaderWriter
from phew import logging

def mqtt_in_command(msg_tuple):
    import json
    try:
        command_type = msg_tuple[0]
        const_dict_str = msg_tuple[1]
        try:
            const_dict_str  = const_dict_str.replace("'", '"')
            const_dict = json.loads(const_dict_str)
        except ValueError:
            return "", {}

        logging.info(f"[mqtt_in_command] command_type {command_type}  {const_dict}")
        return command_type, const_dict
    except Exception as e:
        logging.error(f"[mqtt_in_command] err  {e}")
        return "", {}

def set_rele_on_off(pin_rele, f_rele_is_on):
    logging.info(f"change state rele {f_rele_is_on}")
    if f_rele_is_on:
        pin_rele.on()
    else:
        pin_rele.off()

def check_mode_and_calk_rele_state(rele_mode, off_level, on_level, f_rele_is_on, soc_level):
    #print(rele_mode, off_level, on_level, f_rele_is_on, soc_level)
    f_change_rele_state = False
    old_f_is_on = f_rele_is_on
    if soc_level == 123:
        f_rele_is_on = False
    if rele_mode == RELE_BATTERY_LEVEL and soc_level <= 100 and soc_level >= 0:
        if soc_level <= off_level:
            f_rele_is_on = False
        if soc_level >= on_level:
            f_rele_is_on = True
    elif rele_mode == RELE_ALWAYS_OFF:
        logging.info("mode 1 rele is off")
        #f_change_rele_state = True
        f_rele_is_on = False
    elif rele_mode == RELE_ALWAYS_ON:
        logging.info("mode 2 rele is on")
        f_rele_is_on = True
    if old_f_is_on != f_rele_is_on:
        f_change_rele_state = True
        logging.info(f"change state rele {f_rele_is_on} old {old_f_is_on}")
   # print(f_change_rele_state, f_rele_is_on)
    return f_change_rele_state, f_rele_is_on

def set_rele_mode_to_config_file(rele_mode, file_config_name):
    cr = ConstansReaderWriter(file_config_name)
    c_dict = cr.get_dict()
    print(c_dict)
    const_dict = {'MODE': rele_mode }
    cr.set_constants_from_config_dict(const_dict)
    logging.info(f"save to file rele mode to {rele_mode}")
    return const_dict

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
    #{'OFF_LEVEL': 15,'ON_LEVEL': 85, 'MODE': 'RELE_BATTERY_LEVEL'}

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
    logging.info(f"save to file app_config {const_dict}")
    return const_dict

def set_wifi_mode(wifi_mode):
    const_dict = {}
    logging.info(f"change wifi_mode {wifi_mode}")
    if wifi_mode == WIFI_MODE_AP:
        print(f"wifi_mode {wifi_mode} AP ")
        const_dict = {  'AUTO_CONNECT_TO_WIFI_AP': False,
                        'AUTO_START_WIFI_AP': True,
                        'AUTO_START_UMQTT' : False,
                        'AUTO_START_WEBAPP' : True,
                        'AUTO_START_OLED' : True,
                        'AUTO_RESTART_AFTER_UPDATE' : True,
                        'AUTO_START_SETUP_WIFI' : False,
                        'SEND_LOG_BY_UMQTT': False,
                        }
    elif wifi_mode == WIFI_MODE_OFF:
        print(f"wifi_mode {wifi_mode} off")
        const_dict = {  'AUTO_CONNECT_TO_WIFI_AP': False,
                        'AUTO_START_WIFI_AP': False,
                        'AUTO_START_UMQTT' : False,
                        'AUTO_START_WEBAPP' : False,
                        'AUTO_START_OLED' : True,
                        'AUTO_RESTART_AFTER_UPDATE' : True,
                        'AUTO_START_SETUP_WIFI' : False,
                        'SEND_LOG_BY_UMQTT': False,
                        }

        cr1 = ConstansReaderWriter("wifi_ap_config")
        c_dict1 = cr1.get_dict()
        print(c_dict1)
        const_dict = {'SSID': "0"}
        cr1.set_constants_from_config_dict(const_dict)
        logging.info(f"save to file  wifi_ap_config")

    elif wifi_mode == WIFI_MODE_CLIENT:
        print(f"wifi_mode {wifi_mode} client")
        const_dict = {  'AUTO_CONNECT_TO_WIFI_AP': True,
                        'AUTO_START_WIFI_AP': False,
                        'AUTO_START_UMQTT' : True,
                        'AUTO_START_WEBAPP' : True,
                        'AUTO_START_OLED' : True,
                        'AUTO_RESTART_AFTER_UPDATE' : True,
                        'AUTO_START_SETUP_WIFI' : True,
                        'SEND_LOG_BY_UMQTT' : False,
                        }
    else:
        return const_dict

    logging.info(f"save to file const_dict {const_dict}")
    file_config_name="sys_config"
    cr = ConstansReaderWriter(file_config_name)
    c_dict = cr.get_dict()
    print(c_dict)
    cr.set_constants_from_config_dict(const_dict)
    logging.info(f"save to file {file_config_name}")
    return const_dict

