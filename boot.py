import os
_SYSNAME = os.uname()
print(_SYSNAME)
#import wifi_portal
# connect to network
#wifi_portal.start_wifi()
#wm = WifiManager()
#wm.connect()
##wm.create_heartbeat()
#if wm.is_connected():
#    micropython_OTA.main()
import ugit
wifi_conf_dict = {"ssid": "A1-C4A220", "password": "7KBBBLX7FQ"}
wlan = ugit.wificonnect(wifi_conf_dict.get('ssid'),
                        wifi_conf_dict.get('password'))

ugit.update()
# backup internal files
ugit.backup() # saves to ugit.backup file
# Pull single file
#ugit.pull('file_name.ext','Raw_github_url')
# Pull all files
ugit.pull_all()