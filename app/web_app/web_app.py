# Kevin McAleer
# 28 Aug 2022
from phew import logging, server
from phew.template import render_template
from configs.sys_config import *
from configs.hw_config import HW_LED_PIN
from configs.wifi_ap_config import SSID
import machine
import utime
import os
import asyncio
import _thread
from configs.constants_saver import ConstansReaderWriter
from configs.can_bus_config import CAN_SOC_CHECK_PERIOD_SEC
from primitives import Broker, RingbufQueue
from constants import *
import asyncio

soc_level = 0

def machine_reset():
    import machine
    utime.sleep(3)
    print("Resetting...")
    machine.reset()

def application_mode(broker):
    print("Entering application mode.")
    CSS_STYLE = ""
    CONFIG_PAGE_LINKS = ""
    onboard_led = machine.Pin(HW_LED_PIN, machine.Pin.OUT)

    async def get_soc_level():
        global soc_level
        queue = RingbufQueue(20)
        broker.subscribe(EVENT_TYPE_CAN_SOC_READ, queue)
        async for topic, message in queue:
            #print(topic, message)
            soc_level = int(message)

    def app_index(request):
        #return render_template("/web_app/home.html")
        return render_template("/web_app/index2.html",
                               title=APP_NAME,
                               style_css_str=CSS_STYLE,
                               config_page_links=CONFIG_PAGE_LINKS,
                               replace_symbol=False,
                               )

    def app_toggle_led(request):
        led_on = onboard_led.value()
        if not led_on:
            onboard_led.on()
        else:
            onboard_led.off()
        return "OK"

    #async def app_get_soc(request):
    def app_get_soc(request):
        global soc_level
        # Not particularly reliable but uses built in hardware.
        # Demos how to incorporate senasor data into this application.
        # The front end polls this route and displays the output.
        # Replace code here with something else for a 'real' sensor.
        # Algorithm used here is from:
        # https://www.coderdojotc.org/micropython/advanced-labs/03-internal-temperature/
        # sensor_temp = machine.ADC(4)
        # reading = sensor_temp.read_u16() * (3.3 / (65535))
        #soc_level = que_can.get()
        ## - (reading - 0.706)/0.001721
        #print(f"can soc {soc_level}   can_que  {que_can.qsize()}")
        print(f"soc lev {soc_level}")
        out_str = f"{soc_level}"
        return out_str

        # temperature = 27  # - (reading - 0.706)/0.001721
        # return f"{round(temperature, 1)}"

    def app_reset(request):
        # Deleting the WIFI configuration file will cause the device to reboot as
        # the access point and request new configuration.
        crw = ConstansReaderWriter("wifi_ap_config")
        update_config_dict= {
            "ssid": "",
            "password": "",
        }
        crw.set_constants_from_config_dict(update_config_dict)
        # Reboot from new thread after we have responded to the user.
    #    _thread.start_new_thread(machine_reset, ())
        return render_template("/web_app/reset.html", access_point_ssid=SSID)

    def app_reboot(request):
        # Reboot from new thread after we have responded to the user.
        _thread.start_new_thread(machine_reset, ())
        return render_template("/web_app/reboot.html", access_point_ssid=SSID)

    def app_catch_all(request):
        return "Not found.", 404


    def about(request):
        return render_template("/web_app/about.html",
                               title="About this Site",
                               style_css_str=CSS_STYLE,
                               config_page_links=CONFIG_PAGE_LINKS,
                               )

    def delete_log(request):
        try:
            os.remove("/log.txt")
            log_txt = "File log.txt deleted !!"
        except:
            log_txt = "File log.txt cannot deleted"
        return render_template("/web_app/log_viewer.html",
                               title="Log Viewer",
                               log_txt=log_txt,
                               style_css_str=CSS_STYLE,
                               config_page_links=CONFIG_PAGE_LINKS,
                               )

    def log_viewer(request):
        log_txt = ""
        try:
            with open("/log.txt", "r") as log:
                lines = log.readlines()
                for line in lines:
                   # line = line.strip()
                    log_txt += f"<p>{line}</p>"
                    #log_txt += f"<p>{line}</p><br>"
                    #log_txt += "\n"
        except:
            log_txt = "Cannot read log.txt"
        return render_template("/web_app/log_viewer.html",
                               title="Log Viewer",
                               log_txt=log_txt,
                               style_css_str=CSS_STYLE,
                               config_page_links=CONFIG_PAGE_LINKS,
                               replace_symbol=False,
                               )


    def login_form(request):
        print(request.method)
        crw = ConstansReaderWriter("users_config")
        user_config_dict = crw.get_dict()
        username="username"
        if request.method == 'GET':
            return render_template("/web_app/login.html",
                                        title = "Login",
                                        username = username,
                                        style_css_str = CSS_STYLE,
                                        config_page_links = CONFIG_PAGE_LINKS,
                                        )
        if request.method == 'POST':
            username = request.form.get("username", None)
            username = username.upper()
            password = request.form.get("password", None)
            config_pass = user_config_dict.get(username, None)
            print(user_config_dict)
            logging.info(f"{username}, {password}, {config_pass}")
            if not config_pass is None:
                if password == config_pass:
                    return render_template("/web_app/default.html",
                                       content=f"<h1>Welcome back, {username}</h1>",
                                       style_css_str=CSS_STYLE,
                                       config_page_links=CONFIG_PAGE_LINKS,
                                        replace_symbol=False,
                                       )
            return render_template("/web_app/default.html",
                                       content="Invalid username or password",
                                       title="About this Site",
                                       style_css_str=CSS_STYLE,
                                       config_page_links=CONFIG_PAGE_LINKS,
                                       )

    def get_config_page(module_config, update_config=None):
        print(update_config)
        crw = ConstansReaderWriter(module_config)
        app_config_dict = crw.get_dict()
        if update_config is not None:
            for var_name, val in app_config_dict.items():
                type_attr = type(val)
                if type_attr == bool:
                    page_val = update_config.get(var_name, False)
                    if page_val:
                        update_config[var_name] = 'True'
                    else:
                        update_config[var_name] = 'False'
            crw.set_constants_from_config_dict(update_config)
            app_config_dict = crw.get_dict()
            utime.sleep(2)

        config_page = ""
        max_var_len = 0
        for var_name in app_config_dict.keys():
            if len(var_name) > max_var_len:
                max_var_len = len(var_name)
        for var_name, val in sorted(app_config_dict.items()):
          #  print(f"{var_name}: {val}")
            type_attr = type(val)
            checked = ""

            if type_attr == str:
                type_input = "text"
                if len(val) > 20:
                    type_input = "textarea"
                    val = str(val).split()
                    val = str(val).replace("[", "").replace("]", "")
                    val = str(val).replace("'", "").replace('"', "")
                    row=2
                    for z in val:
                        if z == ",":
                            row += 1
                    val = str(val).replace(",",",\n")

            elif type_attr == int:
                type_input = "number"
            elif type_attr == list:
                type_input = "text"
            elif type_attr == dict:
                type_input = "text"
            elif type_attr == float:
                type_input = "number"
            elif type_attr == bool:
                type_input = "checkbox"
                if val:
                    checked = 'checked'

           # var_name = str(var_name)
            var_len = len(var_name)
            label_name = var_name
            for i in range(max_var_len - var_len):
                label_name += "."
            label_name += ":"

          #  print(var_name, type_input, val, var_len, max_var_len, label_name)

            if type_input == "textarea":
                str_http = f'''<label for="{var_name}">&nbsp;{label_name}</label>            
                                <textarea id="{var_name}" name="{var_name}" value="{val}" rows="{row}" cols="30" >{val}</textarea><br>
                        '''
            else:
                str_http = f'''<label for="{var_name}">&nbsp;{label_name}</label>            
                          <input type="{type_input}" id="{var_name}" name="{var_name}" value="{val}"  {checked} "><br>
                         '''
            config_page += str_http
            config_page += "\n"

        return config_page

    def config_page(request):
        #print(request.method)
        path = request.path
        path = path.replace("/", "")
        #print(path)
        module_config = path
        title = str(module_config).upper()
        if request.method == 'GET':
            config_page = get_config_page(module_config)
            return render_template("/web_app/config_page.html",
                                   config_page=config_page,
                                   page_info="Please save params",
                                   title=f"{title} Config page",
                                   style_css_str=CSS_STYLE,
                                   replace_symbol=False,
                                    config_page_links = CONFIG_PAGE_LINKS,
                                    )

        if request.method == 'POST':
            config_page = get_config_page(module_config,
                                          update_config=request.form)
            restart_app = AUTO_RESTART_AFTER_UPDATE
            if restart_app:
                return app_reboot(request)
            else:
                return render_template("/web_app/config_page.html",
                                   config_page=config_page,
                                   page_info="Params saved !!!",
                                   title=f"{title} Config page",
                                   style_css_str=CSS_STYLE,
                                   replace_symbol=False,
                                    config_page_links = CONFIG_PAGE_LINKS,
                                    )

    def get_app_configs():
        import sys
        mod_name = "configs.app_config"
        obj = __import__(mod_name)
        del sys.modules[mod_name]
        from configs.app_config import ON_LEVEL, OFF_LEVEL, MODE
        mode = MODE
        val_on = ON_LEVEL
        val_off = OFF_LEVEL

        check_AUTO = ""
        check_ALLWAYS_ON = ""
        check_ALLWAYS_OFF = ""
        if mode == "ALLWAYS_ON":
            check_ALLWAYS_ON = "checked"
        elif mode == "ALLWAYS_OFF":
            check_ALLWAYS_OFF = "checked"
        elif mode == "AUTO":
            check_AUTO = "checked"

        mode_str = f"""
               <input type="radio" name="MODE" value="AUTO" id="AUTO" {check_AUTO}><label for="AUTO">&nbsp;AUTO</label><br>
               <input type="radio" name="MODE" value="ALLWAYS_ON" id="ALLWAYS_ON" {check_ALLWAYS_ON}><label for="ALLWAYS_ON">&nbsp;ALLWAYS_ON</label><br>
               <input type="radio" name="MODE" value="ALLWAYS_OFF" id="ALLWAYS_OFF" {check_ALLWAYS_OFF}><label for="ALLWAYS_OFF">&nbsp;ALLWAYS_OFF</label><br>    
           """

        return mode_str, val_on, val_off


    def app_config_page(request):

        if request.method == 'GET':
            mode_str, val_on, val_off = get_app_configs()
            return render_template("/web_app/app_config_page.html",
                                   page_info="Please save params",
                                   title="APP Config page",
                                   val_on=val_on,
                                   val_off=val_off,
                                   mode_str=mode_str,
                                   style_css_str=CSS_STYLE,
                                   replace_symbol=False,
                                   config_page_links=CONFIG_PAGE_LINKS,
                                   )

        if request.method == 'POST':
            crw = ConstansReaderWriter("app_config")
            app_config_dict = crw.get_dict()
            update_config = request.form
            print(update_config)
            for var_name, val in app_config_dict.items():
                type_attr = type(val)
                if type_attr == bool:
                    page_val = update_config.get(var_name, False)
                    if page_val:
                        update_config[var_name] = 'True'
                    else:
                        update_config[var_name] = 'False'
            crw.set_constants_from_config_dict(update_config)
            utime.sleep(2)
            mode_str, val_on, val_off = get_app_configs()
            restart_app = AUTO_RESTART_AFTER_UPDATE
            if restart_app:
                return app_reboot(request)
            else:
                return render_template("/web_app/app_config_page.html",
                                       page_info="Params saved !!!",
                                       val_on=val_on,
                                       val_off=val_off,
                                       mode_str=mode_str,
                                       title="APP Config page",
                                       style_css_str=CSS_STYLE,
                                       replace_symbol=False,
                                       config_page_links=CONFIG_PAGE_LINKS,
                                       )
    def get_css():
        with open("/web_app/style.css", "r") as f:
            style_str = f.read()
            return style_str

    CSS_STYLE = get_css()
    CONFIG_PAGE_LINKS = ""
    for file_name in os.listdir("/configs"):
        if file_name.endswith("_config.py"):
            module_name = file_name.replace(".py", "")
            logging.debug(f"add config to list {module_name}")
            if module_name == "app_config":
                continue
            label_link = module_name.upper()
            CONFIG_PAGE_LINKS += f'<a href="/{module_name}">{label_link} > </a> \n'
            server.add_route(f"/{module_name}", handler=config_page, methods=["POST",'GET'])
    os.chdir("/")

    server.add_route("/", handler=app_index, methods=["GET"])
    server.add_route("/toggle", handler=app_toggle_led, methods=["GET"])
    server.add_route("/about", handler=about, methods=["GET"])
    server.add_route("/log_viewer", handler=log_viewer, methods=["GET"])
    server.add_route("/delete_log", handler=delete_log, methods=["GET"])
    server.add_route("/login", handler=login_form, methods=["POST",'GET'])
    server.add_route("/soc", handler=app_get_soc, methods=["GET"])
    server.add_route("/reset", handler=app_reset, methods=["GET"])
    server.add_route("/reboot", handler=app_reboot, methods=["GET"])
    server.add_route("/app_config_page", handler=app_config_page, methods=["POST",'GET'])
    #os.chdir("/configs")

    # Add other routes for your application...
    server.set_callback(app_catch_all)
    asyncio.create_task(get_soc_level())
    server.run()



