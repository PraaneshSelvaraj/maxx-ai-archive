import os
import socket


def send(filename):
    if not filename: return None
    
    SEPARATOR = "<SEPARATOR>"
    BUFFER_SIZE = 4096 
    host = '0.0.0.0'
    port = 5001
    s=socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(5)
    print(f"[*] Listening as {host}:{port}")
    client_socket, address = s.accept() 
    filesize = os.path.getsize(filename)
    print(filesize)
    client_socket.send(f"{filename}{SEPARATOR}{filesize}".encode('ascii'))
    msg = client_socket.recv(BUFFER_SIZE).decode('ascii')
    if msg =="RECIEVED":
        with open(filename, "rb") as f:
            while True:
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    break
                client_socket.sendall(bytes_read)

    s.close()
    client_socket.close()
    print("file client closed")

def recieve():

    host = "0.0.0.0"
    port = 5001
    BUFFER_SIZE = 4096
    SEPARATOR = "<SEPARATOR>"
    s = socket.socket()
    print(f"[+] Connecting to {host}:{port}")
    s.connect((host, port))
    print("[+] Connected.")
    received = s.recv(BUFFER_SIZE).decode()
    filename, filesize = received.split(SEPARATOR)
    filename = os.path.basename(filename)
    filesize = int(filesize)
    with open(filename, "wb") as f:
        while True:
            bytes_read = s.recv(BUFFER_SIZE)
            if not bytes_read:    
                break

            f.write(bytes_read)
    s.close()