import network
import socket
#import ure
import struct
#import time
import constants_and_configs as cons

AP_IP = cons.AP_IP
s = None
conn = None
ap = None
dns_sock = None


def get_html_page(body=""):
    portal_html = f"""\
    HTTP/1.1 200 OK
    Content-Type: text/html

    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ESP32 Captive Portal</title>
    </head>
    <body>
        <h1>Добро пожаловать!</h1>
        <p>Вы подключились к Captive Portal на ESP32.</p>
        {body}
    </body>
    </html>
    """

    return portal_html

# Start AP
def start_esp32_ap():
    global s, conn, ap, dns_sock
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.ifconfig((AP_IP, '255.255.255.0', AP_IP, AP_IP))
    ap.config(essid=cons.AP_SSID, password=cons.AP_PASSWORD, authmode=cons.AUTHMODE)
    print(f"AP started: SSID='{cons.AP_SSID}', IP='{AP_IP}'")

# Start HTTP server
def start_http_server():
    global s, conn, ap, dns_sock
    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    print("HTTP-server start on port 80")

    while True:
        conn, addr = s.accept()
        print(f"Connecting from {addr}")
        request = conn.recv(1024).decode("utf-8")
        print(request)
        body = f"<p>Connecting from {addr}.</p>"
        portal_html = get_html_page(body=body)
        conn.send(portal_html)
        conn.close()

# Start DNS-server
def start_dns_server():
    global s, conn, ap, dns_sock
    dns_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dns_sock.bind(("0.0.0.0", 53))
    print("DNS-server starting on 53")

    while True:
        try:
            data, addr = dns_sock.recvfrom(512)
            if data:
                dns_sock.sendto(build_dns_response(data), addr)
        except Exception as e:
            print(f"Ошибка DNS: {e}")

def build_dns_response(request):
    # Simple DNS-request function, return IP ESP32
    response = request[:2] + b'\x81\x80'
    response += request[4:6] + request[4:6] + b'\x00\x00\x00\x00'
    response += request[12:]
    response += b'\xc0\x0c'
    response += b'\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04'
    response += struct.pack(">BBBB", *[int(octet) for octet in AP_IP.split('.')])
    return response

def stop_ap():
    global s, conn, ap, dns_sock
    print("Stopping HTTP server...")
    s.close()
    conn.close()
    print("Stopping DNS server...")
    dns_sock.close()
    print("Stopping AP...")
    ap.active(False)



def start_ap():
# start all
    start_esp32_ap()
    import _thread
    _thread.start_new_thread(start_dns_server, ())
    start_http_server()

if __name__ == '__main__':
    start_ap()