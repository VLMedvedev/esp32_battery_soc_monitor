from phew import logging, access_point, connect_to_wifi, is_connected_to_wifi, dns, server
from phew.template import render_template
#import os
import _thread
import time
import machine
from configs.constants_saver import ConstansReaderWriter
from configs.sys_config import *
from configs.wifi_config import PASSWORD

WIFI_MAX_ATTEMPTS = 3
AP_TEMPLATE_PATH = "/wifi_ap"

def machine_reset():
    time.sleep(5)
    print("Resetting...")
    machine.reset()

def setup_wifi_mode():
    print("Entering setup mode...")

    def scan_wifi_ap():
        import network
        ap_str = ""
        wlan_sta = network.WLAN(network.STA_IF)
        wlan_sta.active(True)
        id = 0
        for ssid, *_ in wlan_sta.scan():
            ssid_str = ssid.decode("utf-8").strip()
            if len(ssid_str) == 0:
                continue
            id += 1
            print(ssid_str)
            ap_str += f"""<input type="radio" name="SSID" value="{ssid_str}" id="{id}"><label for="{ssid_str}">&nbsp;{ssid_str}</label><br>"""

        return ap_str

    def ap_index(request):
        if request.headers.get("host").lower() != APP_DOMAIN.lower():
            return render_template(f"{AP_TEMPLATE_PATH}/redirect.html", domain = APP_DOMAIN.lower())
        ap_str = scan_wifi_ap()
        logging.info(f"AP: {ap_str} passwd {PASSWORD}")
        return render_template(f"{AP_TEMPLATE_PATH}/index.html",
                               ap_str = ap_str,
                               ap_name = APP_NAME,
                               passwd = PASSWORD,
                               replace_symbol=False)

    def ap_configure(request):
        print("Saving wifi credentials...")
        #os.chdir("/configs")
        crw = ConstansReaderWriter("wifi_config")
        update_config = request.form
        print(update_config)
        crw.set_constants_from_config_dict(update_config)
        # Reboot from new thread after we have responded to the user.
        _thread.start_new_thread(machine_reset, ())
        return render_template(f"{AP_TEMPLATE_PATH}/configured.html",
                                                   ap_name=APP_NAME,
                                                   ssid = request.form["SSID"])
        
    def ap_catch_all(request):
        if request.headers.get("host") != APP_DOMAIN:
            return render_template(f"{AP_TEMPLATE_PATH}/redirect.html", domain = APP_DOMAIN)

        return "Not found.", 404

    server.add_route("/", handler = ap_index, methods = ["GET"])
    server.add_route("/configure", handler = ap_configure, methods = ["POST"])
    server.set_callback(ap_catch_all)
    start_captive_portal()

def start_ap():
    print(f"Starting {AP_NAME}...ip {AP_IP}")
    ap = access_point(AP_NAME,AP_IP)
    ip = ap.ifconfig()[0]
    print(f"Started ap... ip {ip}")
    dns.run_catchall(ip)
    return ip

def start_captive_portal():
    #global
    ip = start_ap()
    print(f"Starting captive portal... ip {ip}")
    server.run()

def connect_to_wifi_ap():
    # Figure out which mode to start up in...
    wifi_current_attempt = 0
    try:
        print("Testing saved wifi credentials...")
        import sys
        mod_name = "configs.wifi_config"
        obj = __import__(mod_name)
        del sys.modules[mod_name]
        from configs.wifi_config import SSID, PASSWORD
        ssid = SSID
        password = PASSWORD
        print(f"connect to ssid {ssid} and passwd {password}")
        if len(ssid) < 2:
            return None
        while wifi_current_attempt < WIFI_MAX_ATTEMPTS:
            #print(wifi_current_attempt, WIFI_MAX_ATTEMPTS)
            ip_address = connect_to_wifi(ssid, password)
            #print(f"ip_address: {ip_address}")
            if is_connected_to_wifi():
                print(f"Connected to wifi, IP address {ip_address}")
                #break
                return ip_address
            else:
                wifi_current_attempt += 1
    except:
        pass
    return None

def set_rtc():
    # if AUTO_SETUP_TIME:
    from machine import RTC
    import ntptime
    rtc = RTC()
    try:
        ntptime.settime()
        logging.info(f"set time to: {rtc.datetime()}")
        return True
    except Exception as error:
        logging.error(f"set_rtc {error}")
    return False


if __name__ == "__main__":
    ip = connect_to_wifi_ap()
    print(ip)