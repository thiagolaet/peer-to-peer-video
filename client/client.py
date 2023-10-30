import socket

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

delimiter = '0111110'

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((HOST, PORT))
        while True:
            msg = client.recv(1024).decode()
            
            msgs = msg.split(delimiter)

            if msg == 'Desconectando...':
                break


            option = str(input('Aguardando input: \n'))
            # while option == '':
            #     print('Input inválido, por favor digite um input válido\n')
            #     option = str(input())
            client.send(option.encode())
        client.close()

if __name__ == "__main__":
    main()
