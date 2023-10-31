import socket

HOST = "127.0.0.1"
PORT = 65432

delimiter = '\n\n\n'

def main():
    # Cria um socket TCP/IP.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((HOST, PORT))
        while True:
            # Recebe a mensagem do servidor.
            msg = client.recv(1024).decode()
            # Caso a mensagem não esteja completa, recebe o restante.
            while delimiter not in msg:
                msg += client.recv(1024).decode()

            msg = msg.replace(delimiter, '')
            print(msg)

            # Caso a mensagem recebida seja 'Desconectando...', encerra a conexão.
            if 'Desconectando...' in msg:
                break

            # Envia a opção escolhida pelo usuário.
            option = str(input('Aguardando input...\n'))
            while not option:
                print('Input inválido, tente novamente.')
                option = str(input('Aguardando input...\n'))
            client.send(option.encode())

        # Encerra a conexão.
        client.close()

if __name__ == "__main__":
    main()
