from phew import access_point, connect_to_wifi, is_connected_to_wifi, dns, server
from phew.template import render_template
import json
import machine
import network
import os
import utime
import _thread

AP_NAME = "Battery monitor"
AP_DOMAIN = "power-storage.eu"
AP_TEMPLATE_PATH = "ap_templates"
APP_TEMPLATE_PATH = "app_templates"
WIFI_FILE = "wifi.json"
WIFI_MAX_ATTEMPTS = 3

def machine_reset():
    utime.sleep(1)
    print("Resetting...")
    machine.reset()

def setup_mode():
    print("Entering setup mode...")

    def scan_wifi_ap():
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
            ap_str += f"""<input type="radio" name="ssid" value="{ssid_str}" id="{id}"><label for="{ssid_str}">&nbsp;{ssid_str}</label><br>"""

        return ap_str

    def ap_index(request):
        if request.headers.get("host").lower() != AP_DOMAIN.lower():
            return render_template(f"{AP_TEMPLATE_PATH}/redirect.html", domain = AP_DOMAIN.lower())

        return render_template(f"{AP_TEMPLATE_PATH}/index.html", ap_str = scan_wifi_ap(), replace_symbol=False)

    def ap_configure(request):
        print("Saving wifi credentials...")

        with open(WIFI_FILE, "w") as f:
            json.dump(request.form, f)
            f.close()

        # Reboot from new thread after we have responded to the user.
        _thread.start_new_thread(machine_reset, ())
        return render_template(f"{AP_TEMPLATE_PATH}/configured.html", ssid = request.form["ssid"])
        
    def ap_catch_all(request):
        if request.headers.get("host") != AP_DOMAIN:
            return render_template(f"{AP_TEMPLATE_PATH}/redirect.html", domain = AP_DOMAIN)

        return "Not found.", 404

    #ap_str = scan_wifi_ap()
    #print(ap_str)

    server.add_route("/", handler = ap_index, methods = ["GET"])
    server.add_route("/configure", handler = ap_configure, methods = ["POST"])
    server.set_callback(ap_catch_all)

    ap = access_point(AP_NAME)
    ip = ap.ifconfig()[0]
    dns.run_catchall(ip)

def application_mode():
    print("Entering application mode.")
    #onboard_led = machine.Pin("LED", machine.Pin.OUT)

    def app_index(request):
        return render_template(f"{APP_TEMPLATE_PATH}/index.html")

    def app_toggle_led(request):
        #onboard_led.toggle()
        return "OK"
    
    def app_get_temperature(request):
        # Not particularly reliable but uses built in hardware.
        # Demos how to incorporate senasor data into this application.
        # The front end polls this route and displays the output.
        # Replace code here with something else for a 'real' sensor.
        # Algorithm used here is from:
        # https://www.coderdojotc.org/micropython/advanced-labs/03-internal-temperature/
        #sensor_temp = machine.ADC(4)
        #reading = sensor_temp.read_u16() * (3.3 / (65535))
        temperature = 27 #- (reading - 0.706)/0.001721
        return f"{round(temperature, 1)}"
    
    def app_reset(request):
        # Deleting the WIFI configuration file will cause the device to reboot as
        # the access point and request new configuration.
        os.remove(WIFI_FILE)
        # Reboot from new thread after we have responded to the user.
        _thread.start_new_thread(machine_reset, ())
        return render_template(f"{APP_TEMPLATE_PATH}/reset.html", access_point_ssid = AP_NAME)

    def app_reboot(request):
        # Reboot from new thread after we have responded to the user.
        _thread.start_new_thread(machine_reset, ())
        return render_template(f"{APP_TEMPLATE_PATH}/reboot.html", access_point_ssid = AP_NAME)

    def app_catch_all(request):
        return "Not found.", 404

    server.add_route("/", handler = app_index, methods = ["GET"])
    server.add_route("/toggle", handler = app_toggle_led, methods = ["GET"])
    server.add_route("/temperature", handler = app_get_temperature, methods = ["GET"])
    server.add_route("/reset", handler = app_reset, methods = ["GET"])
    server.add_route("/reboot", handler = app_reboot, methods = ["GET"])
    # Add other routes for your application...
    server.set_callback(app_catch_all)

def start_wifi():
    # Figure out which mode to start up in...
    try:
        print("Testing saved wifi credentials...")
        os.stat(WIFI_FILE)

        # File was found, attempt to connect to wifi...
        with open(WIFI_FILE) as f:
            wifi_current_attempt = 1
            wifi_credentials = json.load(f)
            print(wifi_credentials)

            while (wifi_current_attempt < WIFI_MAX_ATTEMPTS):
                ip_address = connect_to_wifi(wifi_credentials["ssid"], wifi_credentials["password"])
                print(ip_address)

                if is_connected_to_wifi():
                    print(f"Connected to wifi, IP address {ip_address}")
                    break
                else:
                    wifi_current_attempt += 1

            if is_connected_to_wifi():
                application_mode()
            else:

                # Bad configuration, delete the credentials file, reboot
                # into setup mode to get new credentials from the user.
                print("Bad wifi connection!")
                print(wifi_credentials)
                os.remove(WIFI_FILE)
                machine_reset()

    except Exception:
        # Either no wifi configuration file found, or something went wrong,
        # so go into setup mode.
        setup_mode()

    # Start the web server...
    server.run()


if __name__ == "__main__":
    start_wifi()