import socket
import threading
import json
# import signal
from vidstream import StreamingServer, CameraClient, AudioSender, AudioReceiver
from time import sleep

HOST = "127.0.0.1"
PORT = 65432

delimiter = '\n\n\n'

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket_port = 65433
udp_socket.bind(('127.0.0.1', udp_socket_port))
shutdown_event = threading.Event()
pause_tcp_event = threading.Event()

# def input_timeout_handler(signum, frame):
#     raise TimeoutError("Tempo de entrada excedido!")

# signal.signal(signal.SIGALRM, input_timeout_handler)

def start_call(sender_ip, sender_port, destination_ip, destination_port):
    streaming_server = StreamingServer(sender_ip, sender_port)
    streaming_server.start_server()
    audio_server = AudioReceiver(sender_ip, sender_port+1)
    audio_server.start_server()
    camera_stream = CameraClient(destination_ip, destination_port)
    camera_stream.start_stream()
    audio_stream = AudioSender(destination_ip, destination_port+1)
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
                    if not json_msg['make_request_call']:
                        msg_to_print += json_msg['msg']

            print(msg_to_print)
            if json_messages[-1]['make_request_call']:
                print('Enviando solicitação de chamada...')
                call_data = json_messages[-1]['msg']
                print('conectando no ip: ', call_data['destination_ip'])
                udp_socket.sendto(json.dumps(call_data).encode('utf-8'), (call_data['destination_ip'], udp_socket_port))
                udp_socket.settimeout(20)
                # Aguardando resposta
                try:
                    data, addr = udp_socket.recvfrom(1024)
                except socket.timeout:
                    print('Tempo de resposta excedido.')
                    continue
                response = json.loads(data)
                if response['response']:
                    print('dados da chamada:')
                    print(call_data['sender_ip'], call_data['sender_port'], call_data['destination_ip'], call_data['destination_port'])
                    streaming_server, audio_server, camera_stream, audio_stream = start_call(
                        call_data['sender_ip'], call_data['sender_port'], call_data['destination_ip'], call_data['destination_port']
                    )
                    print('Chamada em andamento.\nPara encerrar a chamada, digite 10.')
                    is_streaming = True
                else:
                    print('Chamada recusada.')
            elif json_messages[-1]['disconnect']:
                break
            # Caso a mensagem não esteja completa, recebe o restante.
            elif not json_messages[-1]['allow_input']:
                continue

            # Envia a opção escolhida pelo usuário.
            option = str(input('Aguardando input...\n'))
            # while pause_tcp_event.is_set():
            #     pass
            if is_streaming:
                while option != '10':
                    print('Você não pode realizar outra operação enquanto estiver em uma chamada.')
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
        shutdown_event.set()

def handle_udp():
    streaming_server, audio_server, camera_stream, audio_stream = None, None, None, None
    while not shutdown_event.is_set():
        try:
            pause_tcp_event.clear()
            udp_socket.settimeout(3)
            data, addr = udp_socket.recvfrom(1024)
            pause_tcp_event.set()
            data = json.loads(data)
            print(f"-----------------------------------\nNova chamada recebida: IP: {addr[0]} Porta {addr[1]}\n1 - Aceitar\n2 - Recusar\n-----------------------------------")
            try:
                option = str(input('Aguardando input...\n'))
                # signal.alarm(20)
                while option not in ['1', '2']:
                    print('option', option)
                    print('Input inválido, tente novamente.')
                    option = str(input('Aguardando input...\n'))
                if option == '1':
                    udp_socket.sendto(json.dumps({'response': True}).encode('utf-8'), addr)
                    print('dados da chamada:')
                    print(data['destination_ip'], data['destination_port'], data['sender_ip'], data['sender_port'])
                    streaming_server, audio_server, camera_stream, audio_stream = start_call(data['destination_ip'], data['destination_port'], data['sender_ip'], data['sender_port'])
                    print('Chamada em andamento.\nPara encerrar a chamada, digite 10.')
                    option = str(input('Aguardando input...\n'))
                    while option != '10':
                        print('Você não pode realizar outra operação enquanto estiver em uma chamada.')
                        option = str(input('Aguardando input...\n'))
                    if option == '10':
                        streaming_server.stop_server()
                        audio_server.stop_server()
                        camera_stream.stop_stream()
                        audio_stream.stop_stream()
                        streaming_server, audio_server, camera_stream, audio_stream = None, None, None, None
                        print('Chamada encerrada com sucesso!')
                else:
                    udp_socket.sendto(json.dumps({'response': False}).encode('utf-8'), addr)
            except TimeoutError as e:
                print('Chamada recusada por falta de resposta.')
        except socket.timeout:
            pass
    udp_socket.close()

def main():
    tcp_thread = threading.Thread(target=handle_tcp)
    udp_thread = threading.Thread(target=handle_udp)

    tcp_thread.start()
    udp_thread.start()

    tcp_thread.join()
    udp_thread.join()

if __name__ == "__main__":
    main()
