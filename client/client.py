import socket
import threading
import json
from vidstream import StreamingServer, CameraClient, AudioSender, AudioReceiver

HOST = "127.0.0.1"
PORT = 65433

delimiter = '\n\n\n'

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind(('127.0.0.1', 8006))
is_tcp_running = True

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

def handle_tcp():
    streaming_server, audio_server, camera_stream, audio_stream = None, None, None, None
    is_streaming = False
    # Cria um socket TCP/IP.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((HOST, PORT))
        while True:
            # Recebe as mensagens do servidor.
            json_messages = []
            msg_to_print = ''
            messages = client.recv(1024).decode('utf-8').split(delimiter)
            for message in messages:
                if message:
                    json_msg = json.loads(message)
                    json_messages.append(json_msg)
                    msg_to_print += json_msg['msg']

            print(msg_to_print)
            if json_messages[-1]['disconnect']:
                break
            # Caso a mensagem não esteja completa, recebe o restante.
            if not json_messages[-1]['allow_input']:
                continue

            # if request_call_delimiter in msg:
            #     msg = msg.replace(request_call_delimiter, '')
            #     print(msg)
            #     call_data = json.loads(msg)
            #     print(call_data)

            #     print('Realizando chamada...')
            #     udp_socket.sendto('teste'.encode('utf-8'), ('127.0.0.1', 8006))

                # print('Digite o IP do usuário que deseja chamar:')
                # ip = str(input())
                # print('Digite a porta do usuário que deseja chamar:')
                # port = str(input())



                # streaming_server, audio_server, camera_stream, audio_stream = start_call(
                #     call_data['sender_ip'], call_data['sender_port'], call_data['destination_ip'], call_data['destination_port']
                # )
                # print('Chamada inciada com sucesso! Para encerrar a chamada, digite 10.')
                # msg = msg.replace(request_call_delimiter, '')
                # is_streaming = True


            # Envia a opção escolhida pelo usuário.
            option = str(input('Aguardando input...\n'))
            if option == '10':
                if not is_streaming:
                    print('Não há chamada em andamento.')
                else:
                    streaming_server.stop_server()
                    audio_server.stop_server()
                    camera_stream.stop_stream()
                    audio_stream.stop_stream()
                    is_streaming = False
                    streaming_server, audio_server, camera_stream, audio_stream = None, None, None, None
                    print('Chamada encerrada com sucesso!')
            while not option:
                print('Input inválido, tente novamente.')
                option = str(input('Aguardando input...\n'))
            client.send(option.encode('utf-8'))

        # Encerra a conexão.
        client.close()
        is_tcp_running = False

def handle_udp():
    while is_tcp_running:
        data, addr = udp_socket.recvfrom(1024)
        print(f"Recebido via UDP de {addr}: {data.decode('utf-8')}")

def main():
    tcp_thread = threading.Thread(target=handle_tcp)
    udp_thread = threading.Thread(target=handle_udp)

    tcp_thread.start()
    udp_thread.start()

    tcp_thread.join()
    udp_thread.join()

if __name__ == "__main__":
    main()
