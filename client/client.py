import socket

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((HOST, PORT))
        while True:
            msg = client.recv(1024).decode()
            print(msg)

            option = input()
            client.send(option.encode())

if __name__ == "__main__":
    main()
