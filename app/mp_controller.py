


def bt_pressed(btn_number, double=False, long=False):
    global f_pressed_buton, f_rele_is_on, min_level, max_level, view_mode, rele_mode, wifi_ap_on, wifi_mode, press_button_counter
    press_button_counter = 0
    print(f"bt_num = {btn_number} double={double} long={long}")
    if not double and not long and f_pressed_buton:
        if btn_number == HW_BT_LEFT_UP:
            rele_mode = RELE_BATTERY_LEVEL
            min_level += 1
            if min_level > max_level - 1:
                min_level = max_level - 1
            view_mode = VIEW_MODE_SETTING_UP
            oled.draw_setting_level(min_level, button_group="down")
        elif btn_number == HW_BT_LEFT_DOWN:
            rele_mode = RELE_BATTERY_LEVEL
            min_level -= 1
            if min_level < 0:
                min_level = 0
            view_mode = VIEW_MODE_SETTING_DOWN
            oled.draw_setting_level(min_level, button_group="down")
        elif btn_number == HW_BT_RIGTH_UP:
            rele_mode = RELE_BATTERY_LEVEL
            max_level += 1
            if max_level > 100:
                max_level = 100
            view_mode = VIEW_MODE_SETTING_UP
            oled.draw_setting_level(max_level, button_group="up")
        elif btn_number == HW_BT_RIGTH_DOWN:
            rele_mode = RELE_BATTERY_LEVEL
            max_level -= 1
            if max_level < min_level + 1:
                max_level = min_level + 1
            view_mode = VIEW_MODE_SETTING_DOWN
            oled.draw_setting_level(max_level, button_group="up")
    elif double:
        if btn_number == HW_BT_RIGTH_DOWN:
            wifi_ap_on = False
            wifi_mode = WiFi_OFF
          #  stop_ap()
        elif btn_number == HW_BT_LEFT_DOWN:
            wifi_ap_on = True
            wifi_mode = WiFi_client
        elif btn_number == HW_BT_RIGTH_UP:
            wifi_ap_on = False
            wifi_mode = WiFi_AP
          #  start_ap()
        view_mode = VIEW_MODE_VIEW_INFO
    elif long:
        if btn_number == HW_BT_LEFT_DOWN:
            rele_mode = RELE_ALWAYS_OFF
            view_mode = VIEW_MODE_VIEW_OFF
        elif btn_number == HW_BT_RIGTH_DOWN:
            rele_mode = RELE_ALWAYS_ON
            view_mode = VIEW_MODE_VIEW_ON
        check_mode_and_set_rele()
    else:
        view_mode = VIEW_MODE_SETTINGS
    f_pressed_buton = True
    view_data()