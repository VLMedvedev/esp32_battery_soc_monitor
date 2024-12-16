# Author: Igor Ferreira
# License: MIT
# Version: 2.1.0
# Description: WiFi Manager for ESP8266 and ESP32 using MicroPython.

import logging
#logging.basicConfig(level=logging.DEBUG,filename='pylontech.log')
logger = logging.getLogger("wlan","net.log")
#logger = logging.getLogger("wlan")
logger.setLevel(logging.INFO)

from machine import UART, Pin, RTC, Timer
from machine import reset
import esp32
import sys
import struct

import machine
import network
import socket
import re
import time
import ntptime

SSID = "A1-C4A220"
PASSWORD = "7KBBBLX7FQ"

LINK_DOWN = 0
LINK_JOIN = 1
LINK_NOIP = 2
LINK_UP = 3
LINK_FAIL = -1
LINK_NONET = -2
LINK_BADAUTH = -3

# set the wlan to your country, here Germany
#esp32.country("DE")

HEARTBEAT = False

rtc = RTC()

counter = 0
period = 60
router = "192.168.1.254"


def read_wifi_pref():
    if (pref.begin(key="wifi_", readMode=True)):
        wifi_mode = self.pref.getInt("wifi_mode", 0)
        wifi_ssid = self.pref.getString("wifi_ssid", "A1-C4A220")
        wifi_passwd = self.pref.getString("wifi_passwd", "7KBBBLX7FQ")
        pref.end()
    print(f"Read battery pref{self.wifi_mode},")


def write_wifi_pref():
    if (pref.begin(key="wifi_", readMode=False)):
        print( f"Writing battery pref {self.wifi_mode},")

        pref.put("wifi_mode", self.wifi_mode.value)
        pref.put("wifi_ssid", self.wifi_ssid)
        pref.put("wifi_passwd", self.wifi_passwd)
        pref.end()
    time.sleep(1)
    # self.read_battery_pref()

# use onboard LED for a active internet connection
def led_on():
    Pin(15, Pin.OUT).on()


def led_off():
    Pin(15, Pin.OUT).off()

# µPing (MicroPing) for MicroPython
# copyright (c) 2018 Shawwwn <shawwwn1@gmail.com>
# License: MIT

# Internet Checksum Algorithm
# Author: Olav Morken
# https://github.com/olavmrk/python-ping/blob/master/ping.py
# @data: bytes
def checksum(data):
    if len(data) & 0x1: # Odd number of bytes
        data += b'\0'
    cs = 0
    for pos in range(0, len(data), 2):
        b1 = data[pos]
        b2 = data[pos + 1]
        cs += (b1 << 8) + b2
    while cs >= 0x10000:
        cs = (cs & 0xffff) + (cs >> 16)
    cs = ~cs & 0xffff
    return cs

def ping(host, count=4, timeout=5000, interval=30, quiet=False, size=64):
    import utime
    import uselect
    import uctypes
    import usocket
    import ustruct
    import urandom

    # prepare packet
    assert size >= 16, "pkt size too small"
    pkt = b'Q'*size
    pkt_desc = {
        "type": uctypes.UINT8 | 0,
        "code": uctypes.UINT8 | 1,
        "checksum": uctypes.UINT16 | 2,
        "id": uctypes.UINT16 | 4,
        "seq": uctypes.INT16 | 6,
        "timestamp": uctypes.UINT64 | 8,
    } # packet header descriptor
    h = uctypes.struct(uctypes.addressof(pkt), pkt_desc, uctypes.BIG_ENDIAN)
    h.type = 8 # ICMP_ECHO_REQUEST
    h.code = 0
    h.checksum = 0
    h.id = urandom.randint(0, 65535)
    h.seq = 1

    # init socket
    sock = usocket.socket(usocket.AF_INET, usocket.SOCK_RAW, 1)
    sock.setblocking(0)
    sock.settimeout(timeout/1000)
    addr = usocket.getaddrinfo(host, 1)[0][-1][0] # ip address
    sock.connect((addr, 1))
    logger.debug("PING %s (%s): %u data bytes" % (host, addr, len(pkt)))

    seqs = list(range(1, count+1)) # [1,2,...,count]
    c = 1
    t = 0
    n_trans = 0
    n_recv = 0
    finish = False
    while t < timeout:
        if t==interval and c<=count:
            # send packet
            h.checksum = 0
            h.seq = c
            h.timestamp = utime.ticks_us()
            h.checksum = checksum(pkt)
            if sock.send(pkt) == size:
                n_trans += 1
                t = 0 # reset timeout
            else:
                seqs.remove(c)
            c += 1

        # recv packet
        while 1:
            socks, _, _ = uselect.select([sock], [], [], 0)
            if socks:
                resp = socks[0].recv(4096)
                resp_mv = memoryview(resp)
                h2 = uctypes.struct(uctypes.addressof(resp_mv[20:]), pkt_desc, uctypes.BIG_ENDIAN)
                # TODO: validate checksum (optional)
                seq = h2.seq
                if h2.type==0 and h2.id==h.id and (seq in seqs): # 0: ICMP_ECHO_REPLY
                    t_elasped = (utime.ticks_us()-h2.timestamp) / 1000
                    ttl = ustruct.unpack('!B', resp_mv[8:9])[0] # time-to-live
                    n_recv += 1
                    logger.debug("%u bytes from %s: icmp_seq=%u, ttl=%u, time=%f ms" % (len(resp), addr, seq, ttl, t_elasped))
                    seqs.remove(seq)
                    if len(seqs) == 0:
                        finish = True
                        break
            else:
                break

        if finish:
            break

        utime.sleep_ms(1)
        t += 1

    # close
    sock.close()
    ret = (n_trans, n_recv)
    logger.info("%u packets transmitted, %u packets received" % (n_trans, n_recv))
    return (n_trans, n_recv)

def set_router(ip):
    global router
    router = ip

""" fuction that test every minute if a connection with the router on the local net exist,
    if not tries to reconnect. Still buggy, do not use it unless trying to make the program more robust
    Not usefull during development of the functionality
"""
start = time.ticks_ms()
def alive(t, wlan):
    global start
    global counter
    delta = time.ticks_diff(time.ticks_ms(), start)/1000
    counter += 1
    logger.debug(counter)
    if counter % 60 == 0:
        logger.info(f"alive {delta}")
        freq = ping(router,quiet=False)
        if freq[1]>2: # 3 packets received
            return
        else:
            led_off()
            status = wlan.get_status()
            if status < 0:
                raise OSError("wifi connection lost")
            elif status < 3:
                wlan.reconnect()
            else:
                raise RuntimeError("Contact with router lost")
    return


class WifiManager:
    def __init__(self, ssid = 'WifiManager', password = 'wifimanager', reboot = True, debug = False):
        self.wlan_sta = network.WLAN(network.STA_IF)
        self.wlan_sta.active(True)
        self.wlan_ap = network.WLAN(network.AP_IF)
        #self.timer = Timer(-1)
        self.timer = Timer(1)
        # Avoids simple mistakes with wifi ssid and password lengths, but doesn't check for forbidden or unsupported characters.
        if len(ssid) > 32:
            raise Exception('The SSID cannot be longer than 32 characters.')
        else:
            self.ap_ssid = ssid
        if len(password) < 8:
            raise Exception('The password cannot be less than 8 characters long.')
        else:
            self.ap_password = password
            
        # Set the access point authentication mode to WPA2-PSK.
        self.ap_authmode = 3
        
        # The file were the credentials will be stored.
        # There is no encryption, it's just a plain text archive. Be aware of this security problem!
        self.wifi_credentials = 'wifi.dat'
        
        # Prevents the device from automatically trying to connect to the last saved network without first going through the steps defined in the code.
        self.wlan_sta.disconnect()
        
        # Change to True if you want the device to reboot after configuration.
        # Useful if you're having problems with web server applications after WiFi configuration.
        self.reboot = reboot
        
        self.debug = debug


    def connect(self):
        if self.wlan_sta.isconnected():
            return
        profiles = self.read_credentials()
        for ssid, *_ in self.wlan_sta.scan():
            ssid = ssid.decode("utf-8")
            if ssid in profiles:
                password = profiles[ssid]
                if self.wifi_connect(ssid, password):
                    return
        print('Could not connect to any WiFi network. Starting the configuration portal...')
        self.web_server()

    def disconnect(self):
        if self.wlan_sta.isconnected():
            self.wlan_sta.disconnect()

    def is_connected(self):
        return self.wlan_sta.isconnected()

    def get_address(self):
        return self.wlan_sta.ifconfig()[0]

    def reconnect(self):
        self.disconnect()
        self.connect()

    def get_ifconfig(self):
        return self.wlan_sta.ifconfig()

    def get_router(self):
        return self.get_ifconfig()[3]

    def get_status(self):
        return self.wlan_sta.status()

    def link_status(self, status):
        if status == LINK_DOWN:
            return "Link Down"
        elif status == LINK_JOIN:
            return "Joining"
        elif status == LINK_NOIP:
            return "No IP"
        elif status == LINK_UP:
            return "Connected"
        elif status == LINK_FAIL:
            return "Link Failed"
        elif status == LINK_NONET:
            return "No net available"
        elif status == LINK_BADAUTH:
            return "Authentication failed"

    """ This method creates a timer which fires every second a call to alive
        alive checks if a connection to the local net exists.
        Still buggy do not switch it on """
    """ Trying to use the pico watchdog for this in combination with a 'main_485.py' led to problems.
        I had to nuke the pico to make available/usable again """

    def create_heartbeat(self):
        # set_router(self.get_router())
        if HEARTBEAT:
            self.timer = Timer(period=1000, mode=Timer.PERIODIC, callback=lambda t: alive(t, self.wlan_sta))
            logger.debug('timer created')

    def stop_heartbeat(self):
        if HEARTBEAT:
            self.timer.deinit()


    def write_credentials(self, profiles):
        lines = []
        for ssid, password in profiles.items():
            lines.append('{0};{1}\n'.format(ssid, password))
        with open(self.wifi_credentials, 'w') as file:
            file.write(''.join(lines))


    def read_credentials(self):
        lines = []
        try:
            with open(self.wifi_credentials) as file:
                lines = file.readlines()
        except Exception as error:
            if self.debug:
                print(error)
            pass
        profiles = {}
        for line in lines:
            ssid, password = line.strip().split(';')
            profiles[ssid] = password
        return profiles


    def wifi_connect(self, ssid, password):
        print('Trying to connect to:', ssid)
        self.wlan_sta.connect(ssid, password)
        for _ in range(100):
            if self.wlan_sta.isconnected():
                print('\nConnected! Network information:', self.wlan_sta.ifconfig())
                try:
                    ntptime.settime()
                    print(rtc.datetime())
                except Exception as error:
                    print(error)
                return True
            else:
                print('.', end='')
                time.sleep_ms(100)
        print('\nConnection failed!')
        self.wlan_sta.disconnect()
        return False

    
    def web_server(self):
        self.wlan_ap.active(True)
        self.wlan_ap.config(essid = self.ap_ssid, password = self.ap_password, authmode = self.ap_authmode)
        server_socket = socket.socket()
        server_socket.close()
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('', 80))
        server_socket.listen(1)
        print('Connect to', self.ap_ssid, 'with the password', self.ap_password, 'and access the captive portal at', self.wlan_ap.ifconfig()[0])
        while True:
            if self.wlan_sta.isconnected():
                self.wlan_ap.active(False)
                if self.reboot:
                    print('The device will reboot in 5 seconds.')
                    time.sleep(5)
                    machine.reset()
            self.client, addr = server_socket.accept()
            try:
                self.client.settimeout(5.0)
                self.request = b''
                try:
                    while True:
                        if '\r\n\r\n' in self.request:
                            # Fix for Safari browser
                            self.request += self.client.recv(512)
                            break
                        self.request += self.client.recv(128)
                except Exception as error:
                    # It's normal to receive timeout errors in this stage, we can safely ignore them.
                    if self.debug:
                        print(error)
                    pass
                if self.request:
                    if self.debug:
                        print(self.url_decode(self.request))
                    url = re.search('(?:GET|POST) /(.*?)(?:\\?.*?)? HTTP', self.request).group(1).decode('utf-8').rstrip('/')
                    if url == '':
                        self.handle_root()
                    elif url == 'configure':
                        self.handle_configure()
                    else:
                        self.handle_not_found()
            except Exception as error:
                if self.debug:
                    print(error)
                return
            finally:
                self.client.close()


    def send_header(self, status_code = 200):
        self.client.send("""HTTP/1.1 {0} OK\r\n""".format(status_code))
        self.client.send("""Content-Type: text/html\r\n""")
        self.client.send("""Connection: close\r\n""")


    def send_response(self, payload, status_code = 200):
        self.send_header(status_code)
        self.client.sendall("""
            <!DOCTYPE html>
            <html lang="en">
                <head>
                    <title>WiFi Manager</title>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <link rel="icon" href="data:,">
                </head>
                <body>
                    {0}
                </body>
            </html>
        """.format(payload))
        self.client.close()


    def handle_root(self):
        self.send_header()
        self.client.sendall("""
            <!DOCTYPE html>
            <html lang="en">
                <head>
                    <title>WiFi Manager</title>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <link rel="icon" href="data:,">
                </head>
                <body>
                    <h1>WiFi Manager</h1>
                    <form action="/configure" method="post" accept-charset="utf-8">
        """.format(self.ap_ssid))
        for ssid, *_ in self.wlan_sta.scan():
            ssid = ssid.decode("utf-8")
            self.client.sendall("""
                        <p><input type="radio" name="ssid" value="{0}" id="{0}"><label for="{0}">&nbsp;{0}</label></p>
            """.format(ssid))
        self.client.sendall("""
                        <p><label for="password">Password:&nbsp;</label><input type="password" id="password" name="password"></p>
                        <p><input type="submit" value="Connect"></p>
                    </form>
                </body>
            </html>
        """)
        self.client.close()


    def handle_configure(self):
        match = re.search('ssid=([^&]*)&password=(.*)', self.url_decode(self.request))
        if match:
            ssid = match.group(1).decode('utf-8')
            password = match.group(2).decode('utf-8')
            if len(ssid) == 0:
                self.send_response("""
                    <p>SSID must be providaded!</p>
                    <p>Go back and try again!</p>
                """, 400)
            elif self.wifi_connect(ssid, password):
                self.send_response("""
                    <p>Successfully connected to</p>
                    <h1>{0}</h1>
                    <p>IP address: {1}</p>
                """.format(ssid, self.wlan_sta.ifconfig()[0]))
                profiles = self.read_credentials()
                profiles[ssid] = password
                self.write_credentials(profiles)
                time.sleep(5)
            else:
                self.send_response("""
                    <p>Could not connect to</p>
                    <h1>{0}</h1>
                    <p>Go back and try again!</p>
                """.format(ssid))
                time.sleep(5)
        else:
            self.send_response("""
                <p>Parameters not found!</p>
            """, 400)
            time.sleep(5)


    def handle_not_found(self):
        self.send_response("""
            <p>Page not found!</p>
        """, 404)


    def url_decode(self, url_string):

        # Source: https://forum.micropython.org/viewtopic.php?t=3076
        # unquote('abc%20def') -> b'abc def'
        # Note: strings are encoded as UTF-8. This is only an issue if it contains
        # unescaped non-ASCII characters, which URIs should not.

        if not url_string:
            return b''

        if isinstance(url_string, str):
            url_string = url_string.encode('utf-8')

        bits = url_string.split(b'%')

        if len(bits) == 1:
            return url_string

        res = [bits[0]]
        appnd = res.append
        hextobyte_cache = {}

        for item in bits[1:]:
            try:
                code = item[:2]
                char = hextobyte_cache.get(code)
                if char is None:
                    char = hextobyte_cache[code] = bytes([int(code, 16)])
                appnd(char)
                appnd(item[2:])
            except Exception as error:
                if self.debug:
                    print(error)
                appnd(b'%')
                appnd(item)

        return b''.join(res)

def main():
    try:
        logger.setLevel(logging.DEBUG)
        HEARTBEAT =  True
        wlan = WifiManager()
        wlan.connect()
        d = time.localtime()
        print(f"{d[3]}:{d[4]}:{d[5]} {d[2]}-{d[1]}-{d[0]} weekday {d[6]} yearday {d[7]}")
        wlan.create_heartbeat()
        #memory.memory_thread()
        while True:
            logger.info('main alive')
            time.sleep(10)
    except KeyboardInterrupt:
        logger.info('KeyboardInterrupt')
        wlan.stop_heartbeat()
        wlan.disconnect()
        sys.exit(1)
    except Exception as ex:
        logger.error('exception ' + str(ex))
    finally :
        wlan.disconnect()
        sys.exit(0)


if __name__ == "__main__":
    main()


"""
from wifi_manager import WifiManager
import utime

# Example of usage

wm = WifiManager()
wm.connect()

while True:
    if wm.is_connected():
        print('Connected!')
    else:
        print('Disconnected!')
    utime.sleep(10)

"""


