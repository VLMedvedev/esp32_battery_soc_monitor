# Define button press/release callback
def bt_min_up(pin, double_button_vertical_pressed,
                    double_button_horizontal_pressed):
    global f_pressed_buton, f_double_pressed_buton, f_rele_is_on, min_level, max_level, view_mode , rele_mode, wifi_ap_on
    print(f"Pin- {pin}, vertical_pressed {double_button_vertical_pressed} "
          f"horizontal_pressed {double_button_horizontal_pressed}")
    if double_button_horizontal_pressed:
        wifi_ap_on = True
        f_pressed_buton = False
        f_double_pressed_buton=True
        view_mode = cons.VIEW_MODE_VIEW_INFO
        view_data()
        return None
    if double_button_vertical_pressed:
        rele_mode = cons.RELE_ALWAYS_OFF
        check_mode_and_set_rele()
        f_pressed_buton = False
        f_double_pressed_buton=True
        view_mode =  cons.VIEW_MODE_VIEW_OFF
        view_data()
        return None

    if f_pressed_buton:
        rele_mode = cons.RELE_BATTERY_LEVEL
        min_level += 1
        if min_level > max_level - 1:
            min_level = max_level - 1
    view_mode = cons.VIEW_MODE_SETTING_UP
    oled.draw_setting_level(min_level, button_group="down")
    if not f_double_pressed_buton:
        f_pressed_buton = True
    else:
        f_double_pressed_buton = False

def bt_min_down(pin, double_button_vertical_pressed,
                            double_button_horizontal_pressed):
    global f_pressed_buton, f_double_pressed_buton, f_rele_is_on, min_level, max_level, view_mode, rele_mode, wifi_ap_on
    print(f"Pin- {pin}, vertical_pressed {double_button_vertical_pressed} "
          f"horizontal_pressed {double_button_horizontal_pressed}")
    if double_button_horizontal_pressed:
        wifi_ap_on = True
        f_pressed_buton = False
        f_double_pressed_buton=True
        view_mode = cons.VIEW_MODE_VIEW_INFO
        view_data()
        return None
    if double_button_vertical_pressed:
        rele_mode = cons.RELE_ALWAYS_OFF
        f_pressed_buton = False
        f_double_pressed_buton = True
        check_mode_and_set_rele()
        view_mode = cons.VIEW_MODE_VIEW_OFF
        view_data()
        return None

    if f_pressed_buton:
        rele_mode = cons.RELE_BATTERY_LEVEL
        f_pressed_buton = False
        min_level -= 1
        if min_level < 0:
            min_level = 0
    view_mode = cons.VIEW_MODE_SETTING_DOWN
    oled.draw_setting_level(min_level, button_group="down")
    if not f_double_pressed_buton:
        f_pressed_buton = True
    else:
        f_double_pressed_buton = False

def bt_max_up(pin, double_button_vertical_pressed,
                         double_button_horizontal_pressed):
    global f_pressed_buton, f_double_pressed_buton, f_rele_is_on, min_level, max_level, view_mode, rele_mode, wifi_ap_on
    print(f"Pin- {pin}, vertical_pressed {double_button_vertical_pressed} "
          f"horizontal_pressed {double_button_horizontal_pressed}")
    if double_button_horizontal_pressed:
        wifi_ap_on = False
        f_pressed_buton = False
        f_double_pressed_buton=True
        view_mode = cons.VIEW_MODE_VIEW_INFO
        view_data()
        return None
    if double_button_vertical_pressed:
        rele_mode = cons.RELE_ALWAYS_ON
        f_pressed_buton = False
        f_double_pressed_buton = True
        check_mode_and_set_rele()
        view_mode = cons.VIEW_MODE_VIEW_ON
        view_data()
        return None

    if f_pressed_buton:
        rele_mode = cons.RELE_BATTERY_LEVEL
        max_level += 1
        if max_level > 100:
            max_level = 100
    view_mode = cons.VIEW_MODE_SETTING_UP
    oled.draw_setting_level(max_level, button_group="up")
    if not f_double_pressed_buton:
        f_pressed_buton = True
    else:
        f_double_pressed_buton = False

def bt_max_down(pin, double_button_vertical_pressed,
                           double_button_horizontal_pressed):
    global f_pressed_buton, f_double_pressed_buton, f_rele_is_on, min_level, max_level, view_mode, rele_mode, wifi_ap_on
    print(f"Pin- {pin}, vertical_pressed {double_button_vertical_pressed} "
          f"horizontal_pressed {double_button_horizontal_pressed}")
    if double_button_horizontal_pressed:
        wifi_ap_on = False
        f_pressed_buton = False
        f_double_pressed_buton=True
        view_mode = cons.VIEW_MODE_VIEW_INFO
        view_data()
        return None
    if double_button_vertical_pressed:
        rele_mode = cons.RELE_ALWAYS_ON
        f_pressed_buton = False
        f_double_pressed_buton = True
        check_mode_and_set_rele()
        view_mode = cons.VIEW_MODE_VIEW_ON
        view_data()
        return None

    if f_pressed_buton:
        rele_mode = cons.RELE_BATTERY_LEVEL
        max_level -= 1
        if max_level < min_level + 1:
            max_level = min_level + 1
    view_mode = cons.VIEW_MODE_SETTING_DOWN
    oled.draw_setting_level(max_level, button_group="up")
    if not f_double_pressed_buton:
        f_pressed_buton = True
    else:
        f_double_pressed_buton = False