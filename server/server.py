import socket
import threading
import json
from repositories.user_repository import UserRepository

HOST = "25.34.138.157"
PORT = 65432

request_call_delimiter = '<call-identifier>'
delimiter = '\n\n\n'

user_repository = UserRepository()

def send_msg(conn, msg, allow_input=False, make_request_call=False, disconnect=False):
    conn.send((json.dumps({
        'msg': msg,
        'allow_input': allow_input,
        'make_request_call': make_request_call,
        'disconnect': disconnect,
    }) + delimiter).encode('utf-8'))

# Registra um novo usuário no banco de dados.
def register_new_user(conn, ip):
    send_msg(conn, 'O seu IP não foi encontrado na lista de IPs cadastrados, prossiga com o cadastro.\nDigite o nome de usuário: ', allow_input=True)

    username = conn.recv(1024).decode('utf-8')
    is_username_unavailable = user_repository.get_by_username(username) or username == ''
    # Valida o nome de usuário.
    while is_username_unavailable:
        send_msg(conn, 'Nome de usuário inválido ou já cadastrado, por favor digite outro nome de usuário: ', allow_input=True)
        username = conn.recv(1024).decode('utf-8')
        is_username_unavailable = user_repository.get_by_username(username)

    send_msg(conn, 'Digite a porta para o recebimento de chamadas: ', allow_input=True)
    port = conn.recv(1024).decode('utf-8')
    # Valida a porta.
    while not port:
        send_msg(conn, 'Porta inválida, por favor digite outra porta: ', allow_input=True)
        port = conn.recv(1024).decode('utf-8')

    return save_user(conn, username, ip, port)

def start_call(conn, active_users, user):
    send_msg(conn, 'Digite o nome do usuário: ', allow_input=True)
    receiver_name = conn.recv(1024).decode('utf-8')
    # Valida o username.
    while not receiver_name:
        send_msg('Nome inválido, por favor digite outro nome: ', allow_input=True)
        receiver_name = conn.recv(1024).decode('utf-8')
    # Busca o nome entre os usuários ativos e retorna o ip e a porta do mesmo.
    if receiver_name == user.username:
        send_msg(conn, 'Não é permitido ligar para si mesmo.')
        return
    for active_user in active_users:
        if active_user.username == receiver_name:
            send_msg(conn, {
                "sender_ip": user.ip,
                "sender_port": user.port,
                "destination_ip": active_user.ip,
                "destination_port": active_user.port,
            }, make_request_call=True)
            return
    send_msg(conn, 'Usuário não encontrado entre os usuários ativos no momento.')

# Salva um novo usuário no banco de dados.
def save_user(conn, username, ip, port):
    user = user_repository.create(username, ip, port)
    print(f'Usuário cadastrado com sucesso:\nIP: {ip} | Porta: {port} | Username: {username}')
    send_msg(conn, 'Cadastro realizado com sucesso!\n')
    return user

# Busca um usuário no banco de dados pelo nome de usuário.
def get_user_by_username(conn):
    send_msg(conn, 'Digite o nome de usuário: ', allow_input=True)
    username = conn.recv(1024).decode('utf-8')
    user = user_repository.get_by_username(username)
    if user is None:
        msg = 'Usuário não encontrado.\n'
    else:
        msg = f'-----------------------------------\nIP | porta | username\n-----------------------------------\n{user.ip} | {user.port} | {user.username}\n'
    send_msg(conn, msg)

# Lista os usuários ativos no momento.
def list_active_users(conn, active_users):
    msg = '-----------------------------------\n' \
            'IP | porta | username\n' \
            '-----------------------------------\n'
    for user in active_users:
        msg += f'{user.ip} | {user.port} | {user.username}\n'
    send_msg(conn, msg)

# Lista todos os usuários cadastrados.
def list_registered_users(conn):
    users = user_repository.all()
    if len(users) == 0:
        msg = 'Não há usuários cadastrados.'
    else:
        msg = '-----------------------------------\n' \
                'IP | porta | username\n' \
                '-----------------------------------\n'
        for user in users:
            msg += f'{user.ip} | {user.port} | {user.username}\n'
    send_msg(conn, msg)

# Remove um usuário do banco de dados.
def delete_user(conn):
    user_ip = conn.getpeername()[0]
    user = user_repository.get_by_ip(user_ip)
    if user is None:
        msg = 'Usuário não encontrado.\n'
    else:
        user_repository.delete_by_ip(user_ip)
        msg = 'Usuário descadastrado com sucesso.\n'
        print(f'Usuário descadastrado com sucesso:\nIP: {user.ip} | Porta: {user.port} | Username: {user.username}')
    send_msg(conn, msg)

# Menu principal.
def menu(conn, active_users, user):
    while True:
        send_msg(conn, '-----------------------------------\n1 - Listar usuários ativos no momento\n2 - Listar usuários cadastrados\n3 - Buscar usuário\n4 - Realizar chamada\n5 - Descadastrar\n6 - Sair\n-----------------------------------', allow_input=True)
        user_option = conn.recv(1024).decode('utf-8')
        if user_option == '1':
            list_active_users(conn, active_users)
        elif user_option == '2':
            list_registered_users(conn)
        elif user_option == '3':
            get_user_by_username(conn)
        elif user_option == '4':
            start_call(conn, active_users, user)
        elif user_option == '5':
            delete_user(conn)
            send_msg(conn, 'Desconectando...', disconnect=True)
            break
        elif user_option == '6':
            send_msg(conn, 'Desconectando...', disconnect=True)
            break
        elif user_option == '10':
            send_msg(conn, '')
        else:
            send_msg(conn, 'Opção inválida, tente novamente.\n')

# Verifica se o usuário já está cadastrado no banco de dados e o registra, caso não esteja.
def log_user(conn, ip):
    user = user_repository.get_by_ip(ip)
    if not user:
        user = register_new_user(conn, ip)
    else:
        send_msg(conn, f"Bem-vindo, {user.username}!\n")
    return user

def handle_new_client(conn, addr, active_users):
    ip, port = addr
    try:
        with conn:
            print(f"Novo usuário conectado: IP {ip}")
            user = log_user(conn, ip)
            active_users.append(user)
            menu(conn, active_users, user)
    # Trata o erro de conexão perdida com o cliente.
    except BrokenPipeError as e:
        print(f'O usuário de IP {ip} perdeu conexão.')
    finally:
        if user:
            active_users.remove(user)
        conn.close()

def main():
    # Cria as tabelas do banco de dados, caso não existam.
    user_repository.create_tables()
    active_users = []
    while True:
        # Aguarda por novas conexões.
        server.listen()
        conn, addr = server.accept()
        # Cria uma thread para lidar com o novo cliente.
        client_thread = threading.Thread(target=handle_new_client, args=(conn, addr, active_users))
        client_thread.start()

if __name__ == "__main__":
    # Cria um objeto de socket TCP e o vincula ao endereço e porta especificados.
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    main()
