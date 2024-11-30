from wifi_manager import WifiManager
import micropython_OTA
import os
_SYSNAME = os.uname()
print(_SYSNAME)
# connect to network
#wm = WifiManager()
#wm.connect()
##wm.create_heartbeat()
#if wm.is_connected():
#    micropython_OTA.main()