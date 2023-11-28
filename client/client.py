import socket
from vidstream import StreamingServer, CameraClient, AudioSender, AudioReceiver
import time

HOST = "25.30.163.114"
PORT = 65432

delimiter = '\n\n\n'
request_call_delimiter = '<call-identifier>'


def start_call(sender_ip, sender_port, destination_ip, destination_port):
    streaming_server = StreamingServer(sender_ip, sender_port)
    streaming_server.start_server()
    audio_server = AudioReceiver(sender_ip, sender_port + 100)
    audio_server.start_server()
    camera_stream = CameraClient(destination_ip, destination_port)
    camera_stream.start_stream()
    audio_stream = AudioSender(destination_ip, destination_port + 100)
    audio_stream.start_stream()
    return streaming_server, audio_server, camera_stream, audio_stream

def main():
    streaming_server, audio_server, camera_stream, audio_stream = None, None, None, None
    is_streaming = False
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
            if is_streaming:
                msg += 'Chamada em andamento...\nPara encerrar, digite 10\n-----------------------------------\n'
            if request_call_delimiter in msg:
                print('Realizando chamada...')
                # print('Digite o IP do usuário que deseja chamar:')
                # ip = str(input())
                # print('Digite a porta do usuário que deseja chamar:')
                # port = str(input())

                my_ip = client.getsockname()[0]
                port = 8001
                ip_server_to_send_video_and_audio='25.30.163.114'
                port_server_to_send_video_and_audio = port
                streaming_server, audio_server, camera_stream, audio_stream = start_call(my_ip, port, ip_server_to_send_video_and_audio, port_server_to_send_video_and_audio)
                print('Chamada inciada com sucesso! Para encerrar a chamada, digite 10.')
                msg = msg.replace(request_call_delimiter, '')
                is_streaming = True

            print(msg)

            # Caso a mensagem recebida seja 'Desconectando...', encerra a conexão.
            if 'Desconectando...' in msg:
                break

            # Envia a opção escolhida pelo usuário.
            option = str(input('Aguardando input...\n'))
            if option == '10' and is_streaming:
                streaming_server.stop_server()
                audio_server.stop_server()
                camera_stream.stop_stream()
                audio_stream.stop_stream()
                is_streaming = False
                streaming_server, audio_server, camera_stream, audio_stream = None, None, None, None
            while not option:
                print('Input inválido, tente novamente.')
                option = str(input('Aguardando input...\n'))
            client.send(option.encode())

        # Encerra a conexão.
        client.close()

if __name__ == "__main__":
    main()
