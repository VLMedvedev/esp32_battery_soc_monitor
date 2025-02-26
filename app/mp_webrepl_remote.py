# main_webrepl.py file for ESP32
import asyncio
import socket
from configs.webperl_remote import *

#serverName = 'IP.ADDRESS.OF.SERVER'
serverName = SERVER_NAME
serverPort = SERVER_PORT

localName = 'localhost'
localPort = 8266

async def async_recvfrom(sock, count):
    print(f"Entered async_recvfrom(sock, count)")
    yield asyncio.core._io_queue.queue_read(sock)
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

        await asyncio.sleep_ms(10)


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
                taskRemoteToLocal = asyncio.create_task(
                    _transfer(tunnelSocket, redirectSocket, "remote -> localhost:8266"))

                taskLocalToRemote = asyncio.create_task(
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
        await asyncio.sleep(5)
        print(f"Checkpoint 5: {needToStartThreads}; {tunnelSocket}; {redirectSocket}")

# ----------------
# MAIN
def main():
    task = None
    try:
        task = asyncio.create_task(tunnelToServer())
        asyncio.run(tunnelToServer())
    except KeyboardInterrupt:
        print("Stopped with keyboard")
        if task is not None:
            print(f"Stopping task { task }")
            task.cancel()

if __name__ == "__main__":
    main()