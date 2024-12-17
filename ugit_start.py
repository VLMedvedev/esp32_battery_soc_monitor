import ugit
import network
wifi_conf_dict = {"ssid": "A1-C4A220", "password": "7KBBBLX7FQ"}
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(wifi_conf_dict.get('ssid'),
             wifi_conf_dict.get('password'))
ugit.update()
# backup internal files
ugit.backup() # saves to ugit.backup file
# Pull single file
#ugit.pull('file_name.ext','Raw_github_url')
# Pull all files
ugit.pull_all()