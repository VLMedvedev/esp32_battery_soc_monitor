import network
import socket
import ure

# Конфигурация точки доступа
AP_SSID = "ESP32_CaptivePortal"
AP_PASSWORD = "password123"  # Можно оставить пустым для открытой сети
#AP_PASSWORD = ""  # Можно оставить пустым для открытой сети
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

def start_ap():
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=AP_SSID, password=AP_PASSWORD, authmode=network.AUTH_WPA_WPA2_PSK)
    #ap.config(essid=AP_SSID, password=AP_PASSWORD)
    print(f"Ap started: SSID='{AP_SSID}', passwd='{AP_PASSWORD}'")
    print(f"IP адрес: {ap.ifconfig()[0]}")

def start_captive_portal():
    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    print("Server Captive Portal start on port 80")

    while True:
        conn, addr = s.accept()
        print(f"Connect from {addr}")
        request = conn.recv(1024).decode("utf-8")
        print(request)

        # Перехват всех запросов и отправка HTML
        conn.send(PORTAL_HTML)
        conn.close()

# Запуск точки доступа и Captive Portal
start_ap()
start_captive_portal()
