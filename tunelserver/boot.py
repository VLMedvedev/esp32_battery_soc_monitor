# boot.py file for ESP32
import webrepl

yourWifiSSID = "my_ssid"
yourWifiPassword = "my_WiFi_password"

def connect():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(yourWifiSSID, yourWifiPassword)

connect()

webrepl.start()

print("--------------")
print("Ended boot")
print("--------------")