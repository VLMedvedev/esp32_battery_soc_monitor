__version__ = "0.0.2"

# highly recommended to set a lowish garbage collection threshold
# to minimise memory fragmentation as we sometimes want to
# allocate relatively large blocks of ram.
import gc, os

gc.threshold(50000)

# phew! the Pico (or Python) HTTP Endpoint Wrangler
from . import logging

# determine if remotely mounted or not, changes some behaviours like
# logging truncation
remote_mount = False
try:
  os.statvfs("") # causes exception if remotely mounted (mpremote/pyboard.py)
except:
  remote_mount = True

def get_ip_address():
  import network
  try:
    return network.WLAN(network.STA_IF).ifconfig()[0]
  except:
    return None

def is_connected_to_wifi():
  import network
  wlan = network.WLAN(network.STA_IF)
  ret = wlan.isconnected()
  print(f"isconnected {ret}")
  return ret

def get_status_name(status):
  import network
  print(f"status {status}")
  try:
    statuses = {}
    statuses[network.STAT_IDLE] = "idle"
    statuses[network.STAT_CONNECTING] = "connecting"
    statuses[network.STAT_WRONG_PASSWORD] = "wrong password"
    statuses[network.STAT_NO_AP_FOUND] = "access point not found"
    #statuses[network.STAT_CONNECT_FAIL] = "connection failed"
    statuses[network.STAT_GOT_IP] = "got ip address"
    #print(statuses)
    ret = statuses.get(status,"unknown")
    return ret
  except:
    return "status errror"

# helper method to quickly get connected to wifi
def connect_to_wifi(ssid, password, timeout_seconds=30):
  import network, time
  info_str = f"Connect to ssid {ssid} with password {password}"
  logging.info(info_str)
  print(info_str)
  wlan = network.WLAN(network.STA_IF)
  wlan.active(True)
  #print("connecting to network...")
  wlan.connect(ssid, password)
  start = time.ticks_ms()
  #print(start)
  status = wlan.status()
  #print(status)
  status_name = get_status_name(status)
  logging.info(f"  - {status_name}")

  while not wlan.isconnected():
    print("wlan disconected...")
    if (time.ticks_ms() - start) > (timeout_seconds * 1000):
      break
    new_status = wlan.status()
    print(f"  - {get_status_name(new_status)}")
    if status != new_status:
      status_name = get_status_name(new_status)
      logging.info(f"  - {status_name}")
      status = new_status
    time.sleep(0.25)


  if wlan.status() == network.STAT_GOT_IP:
    print("return ip address....")
    return wlan.ifconfig()[0]
  return None


# helper method to put the pico into access point mode
def access_point(ssid, password = None):
  import network

  # start up network in access point mode  
  wlan = network.WLAN(network.AP_IF)
  wlan.config(essid=ssid)
  if password:
    wlan.config(password=password)
  else:    
    wlan.config(security=0) # disable password
  wlan.active(True)

  return wlan
