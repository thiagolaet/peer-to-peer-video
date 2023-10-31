import socket

HOST = "127.0.0.1"
PORT = 65432

delimiter = '\n\n\n'

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((HOST, PORT))
        while True:
            msg = client.recv(1024).decode()
            while delimiter not in msg:
                msg += client.recv(1024).decode()

            msg = msg.replace(delimiter, '')
            print(msg)

            if 'Desconectando...' in msg:
                break

            option = str(input('Aguardando input...\n'))
            while not option:
                print('Input inválido, tente novamente.')
                option = str(input('Aguardando input...\n'))
            client.send(option.encode())
        client.close()

if __name__ == "__main__":
    main()
