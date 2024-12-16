import socket
import sys
import _thread

external_host = "0.0.0.0"
external_port = 6690

tunnel_host = "0.0.0.0"
tunnel_port = 12014

def main():
    _thread.start_new_thread(server, () )
    lock = _thread.allocate_lock()
    lock.acquire()
    lock.acquire()

def server(*settings):
    try:
        external_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        external_socket.bind((external_host, external_port)) # listen
        external_socket.listen(2)
        print(f"*** listening on { external_host }:{ external_port }")
        
        tunnel_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tunnel_socket.bind((tunnel_host, tunnel_port)) # listen
        tunnel_socket.listen(2)
        print(f"*** listening on { tunnel_host }:{ tunnel_port }")

        tunnelclient_socket, esp_address = tunnel_socket.accept()
        print(f"*** from { esp_address }:{ tunnel_port } to { external_host }:{ external_port }")
        
        print(f"Waiting for external:6690")
        externalclient_socket, client_address = external_socket.accept()
        print(f"*** from { client_address }:{ external_port } to { tunnel_host }:{ tunnel_port }")

        _thread.start_new_thread(forward, (tunnelclient_socket, externalclient_socket, "tunnel:12014 -> external:6690" ))
        _thread.start_new_thread(forward, (externalclient_socket, tunnelclient_socket, "external:6690 -> client:12014" ))
    except Exception as error:
        print(f"Error { error }")

def forward(source, destination, description):
    print(f"Started forwarding loop: { description }")
    data = ' '
    while data and (source is not None) and (destination is not None):
        data = source.recv(1024)
        #print(f"*** { description }: { data }")
        if data:
            destination.sendall(data)
        else:
            print(f"Closing connection { description }")
            source.close()
            source = None
            destination.close()
            destination = None

if __name__ == '__main__':
    main()