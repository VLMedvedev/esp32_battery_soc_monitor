# highly recommended to set a lowish garbage collection threshold
# to minimise memory fragmentation as we sometimes want to
# allocate relatively large blocks of ram.
import gc
from configs.sys_config import *
from wifi_ap.wifi_portal import connect_to_wifi_ap, setup_wifi_mode, set_rtc, start_captive_portal

"""Main function. Runs after board boot, before main.py
Connects to Wi-Fi and checks for latest git version.
"""
#gc.set_threshold(50000)
gc.collect()
gc.enable()

ip_addres = None
if AUTO_CONNECT_TO_WIFI_AP:
    ip_addres = connect_to_wifi_ap()
    if ip_addres is None:
        if AUTO_START_SETUP_WIFI:
            setup_wifi_mode()
        if AUTO_START_CAPTIVE_PORTAL:
            ip_addres = start_captive_portal()
    else:
        set_rtc()
        import mp_git
        mp_git.main()
else:
    if AUTO_START_CAPTIVE_PORTAL:
        ip_addres = start_captive_portal()




