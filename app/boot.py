# highly recommended to set a lowish garbage collection threshold
# to minimise memory fragmentation as we sometimes want to
# allocate relatively large blocks of ram.
# import gc
# gc.threshold(50000)
# gc.collect()
# gc.enable()

from configs.sys_config import AUTO_START_WEBREPL, AUTO_CONNECT_TO_WIFI_AP
from wifi_ap.wifi_portal import connect_to_wifi_ap
"""Main function. Runs after board boot, before main.py
Connects to Wi-Fi and checks for latest git version.
"""
if AUTO_CONNECT_TO_WIFI_AP:
    ip_address = connect_to_wifi_ap()
    if ip_address is not None:
        if AUTO_START_WEBREPL:
            #logging.info("[AUTO_START_WEBREPL]")
            import webrepl
            # #asyncio.create_task(webrepl.start())
            f_start_loop = False
            webrepl.start()







