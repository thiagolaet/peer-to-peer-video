import socket
from vidstream import StreamingServer, CameraClient, AudioSender, AudioReceiver

HOST = "25.30.163.114"
PORT = 65432

delimiter = '\n\n\n'
request_call_delimiter = '<call-identifier>'

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
            if request_call_delimiter in msg:
                print('Realizando chamada...')
                # print('Digite o IP do usuário que deseja chamar:')
                # ip = str(input())
                # print('Digite a porta do usuário que deseja chamar:')
                # port = str(input())
                my_ip, ip_server_host = client.getsockname()[0]
                port, port_server_host = 8001
                server = StreamingServer(ip_server_host, port_server_host)
                server.start_server()

                server_audio = AudioReceiver(ip_server_host, port_server_host)
                server_audio.start_server()

                CameraClient(ip_server_to_send_video_and_audio, port_server_to_send_video_and_audio).start_stream()
                AudioSender(ip_server_to_send_video_and_audio, port_server_to_send_video_and_audio + 100).start_stream()
                continue

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
