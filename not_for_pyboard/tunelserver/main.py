# main_webrepl.py file for ESP32
import uasyncio
import socket

#serverName = 'IP.ADDRESS.OF.SERVER'
serverName = '167.172.179.78'
serverPort = 12014

localName = 'localhost'
localPort = 8266

async def async_recvfrom(sock, count):
    print(f"Entered async_recvfrom(sock, count)")
    yield uasyncio.core._io_queue.queue_read(sock)
    print(f"async_recvfrom(sock, count) queued read")
    return sock.recv(count)

async def _transfer(src, dest, description):
    print(f"Started forwarding loop: {description}")
    while True:
        data = await async_recvfrom(src, 1024)
        print(f"Readed {len(data)} bytes from {description}")
        if data == b'':
            break
        dest.write(data)

        await uasyncio.sleep_ms(10)


async def tunnelToServer():
    tunnelSocket = None
    redirectSocket = None

    taskRemoteToLocal = None
    taskLocalToRemote = None

    while True:
        try:
            needToStartThreads = False

            print(f"Checkpoint 1: {needToStartThreads}; {tunnelSocket}; {redirectSocket}")

            if tunnelSocket is None:
                needToStartThreads = True
                tunnelSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                tunnelServerTuple = (serverName, serverPort)
                print(f"Connecting to {tunnelServerTuple}...")
                tunnelSocket.connect(tunnelServerTuple)
                print(f"Connected to {tunnelServerTuple}")
                print(f"Checkpoint 2: {needToStartThreads}; {tunnelSocket}; {redirectSocket}")

            if redirectSocket is None:
                needToStartThreads = True
                redirectSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                localTuple = ('localhost', 8266)
                print(f"Connecting to {localTuple}...")
                redirectSocket.connect(localTuple)
                print(f"Connected to {localTuple}")
                print(f"Checkpoint 3: {needToStartThreads}; {tunnelSocket}; {redirectSocket}")

            if needToStartThreads:
                print("Starting tasks...")
                taskRemoteToLocal = uasyncio.create_task(
                    _transfer(tunnelSocket, redirectSocket, "remote -> localhost:8266"))

                taskLocalToRemote = uasyncio.create_task(
                    _transfer(redirectSocket, tunnelSocket, "localhost:8266 -> remote"))
                print("Tasks started...")
        except Exception as exc:
            print(f"Error with TCP tunnel: {exc}")
            if tunnelSocket is not None:
                tunnelSocket.close()
                tunnelSocket = None
            if redirectSocket is not None:
                redirectSocket.close()
                redirectSocket = None

            if taskRemoteToLocal is not None:
                taskRemoteToLocal.cancel()
                taskRemoteToLocal = None

            if taskLocalToRemote is not None:
                taskLocalToRemote.cancel()
                taskLocalToRemote = None

        print("Tunnel daeomon sleeping")
        print(f"Checkpoint 4: {needToStartThreads}; {tunnelSocket}; {redirectSocket}")
        await uasyncio.sleep(5)
        print(f"Checkpoint 5: {needToStartThreads}; {tunnelSocket}; {redirectSocket}")

# ----------------
# MAIN

task = None
try:
    task = uasyncio.create_task(tunnelToServer())
    uasyncio.run(tunnelToServer())
except KeyboardInterrupt:
    print("Stopped with keyboard")
    if task is not None:
        print(f"Stopping task { task }")
        task.cancel()