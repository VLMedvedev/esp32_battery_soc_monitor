import network
import socket
import ure
import struct
import time

# Конфигурация точки доступа
AP_SSID = "ESP32_CaptivePortal"
AP_PASSWORD = "password123"
AP_PASSWORD = ""
AP_IP = "192.168.4.1"
PORTAL_HTML = """\
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
</body>
</html>
"""

# Запуск точки доступа
def start_ap():
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.ifconfig((AP_IP, '255.255.255.0', AP_IP, AP_IP))
    #ap.config(essid=AP_SSID, password=AP_PASSWORD, authmode=network.AUTH_WPA_WPA2_PSK)
    ap.config(essid=AP_SSID, authmode=network.AUTH_OPEN)
    print(f"Точка доступа запущена: SSID='{AP_SSID}', IP='{AP_IP}'")

# Запуск HTTP-сервера
def start_http_server():
    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    print("HTTP-сервер запущен на порту 80")

    while True:
        conn, addr = s.accept()
        print(f"Подключение от {addr}")
        request = conn.recv(1024).decode("utf-8")
        print(request)

        conn.send(PORTAL_HTML)
        conn.close()

# Запуск DNS-сервера
def start_dns_server():
    dns_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dns_sock.bind(("0.0.0.0", 53))
    print("DNS-сервер запущен на порту 53")

    while True:
        try:
            data, addr = dns_sock.recvfrom(512)
            if data:
                dns_sock.sendto(build_dns_response(data), addr)
        except Exception as e:
            print(f"Ошибка DNS: {e}")

def build_dns_response(request):
    # Простая DNS-ответная функция, которая всегда возвращает IP ESP32
    response = request[:2] + b'\x81\x80'
    response += request[4:6] + request[4:6] + b'\x00\x00\x00\x00'
    response += request[12:]
    response += b'\xc0\x0c'
    response += b'\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04'
    response += struct.pack(">BBBB", *[int(octet) for octet in AP_IP.split('.')])
    return response

# Запуск всех сервисов
start_ap()
import _thread
_thread.start_new_thread(start_dns_server, ())
start_http_server()
