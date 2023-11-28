import socket
import threading
from repositories.user_repository import UserRepository

HOST = "25.30.163.114"
PORT = 65432

request_call_delimiter = '<call-identifier>'
delimiter = '\n\n\n'

user_repository = UserRepository()

# Registra um novo usuário no banco de dados.
def register_new_user(conn, ip):
    conn.send(('O seu IP não foi encontrado na lista de IPs cadastrados, prossiga com o cadastro.\nDigite o nome de usuário: ' + delimiter).encode())

    username = conn.recv(1024).decode()
    is_username_unavailable = user_repository.get_by_username(username) or username == ''
    # Valida o nome de usuário.
    while is_username_unavailable:
        conn.send(('Nome de usuário inválido ou já cadastrado, por favor digite outro nome de usuário: ' + delimiter).encode())
        username = conn.recv(1024).decode()
        is_username_unavailable = user_repository.get_by_username(username)

    conn.send(('Digite a porta para o recebimento de chamadas: ' + delimiter).encode())
    port = conn.recv(1024).decode()
    # Valida a porta.
    while not port:
        conn.send(('Porta inválida, por favor digite outra porta: ' + delimiter).encode())
        port = conn.recv(1024).decode()

    return save_user(conn, username, ip, port)

# Salva um novo usuário no banco de dados.
def save_user(conn, username, ip, port):
    user = user_repository.create(username, ip, port)
    print(f'Usuário cadastrado com sucesso:\nIP: {ip} | Porta: {port} | Username: {username}')
    conn.send('Cadastro realizado com sucesso!\n'.encode())
    return user

# Busca um usuário no banco de dados pelo nome de usuário.
def get_user_by_username(conn):
    conn.send(('Digite o nome de usuário: ' + delimiter).encode())
    username = conn.recv(1024).decode()
    user = user_repository.get_by_username(username)
    if user is None:
        msg = 'Usuário não encontrado.\n'
    else:
        msg = f'-----------------------------------\nIP | porta | username\n-----------------------------------\n{user.ip} | {user.port} | {user.username}\n'
    conn.send(msg.encode())

# Lista os usuários ativos no momento.
def list_active_users(conn, active_users):
    msg = '-----------------------------------\n' \
            'IP | porta | username\n' \
            '-----------------------------------\n'
    for user in active_users:
        msg += f'{user.ip} | {user.port} | {user.username}\n'
    conn.send(msg.encode())

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
    conn.send(msg.encode())

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
    conn.send(msg.encode())

# Menu principal.
def menu(conn, active_users):
    while True:
        conn.send(('-----------------------------------\n1 - Listar usuários ativos no momento\n2 - Listar usuários cadastrados\n3 - Buscar usuário\n4 - Descadastrar\n5 - Sair\n6 - Realizar chamada\n-----------------------------------' + delimiter).encode())
        user_option = conn.recv(1024).decode()
        if user_option == '1':
            list_active_users(conn, active_users)
        elif user_option == '2':
            list_registered_users(conn)
        elif user_option == '3':
            get_user_by_username(conn)
        elif user_option == '4':
            delete_user(conn)
            conn.send(('Desconectando...' + delimiter).encode())
            break
        elif user_option == '5':
            conn.send(('Desconectando...' + delimiter).encode())
            break
        elif user_option == '6':
            conn.send((request_call_delimiter + delimiter).encode())
        elif user_option == '10':
            conn.send(''.encode())
        else:
            conn.send(('Opção inválida, tente novamente.\n').encode())

# Verifica se o usuário já está cadastrado no banco de dados e o registra, caso não esteja.
def log_user(conn, ip):
    user = user_repository.get_by_ip(ip)
    if not user:
        user = register_new_user(conn, ip)
    else:
        conn.send(f"Bem-vindo, {user.username}!\n".encode())
    return user

def handle_new_client(conn, addr, active_users):
    ip, port = addr
    try:
        with conn:
            print(f"Novo usuário conectado: IP {ip}")
            user = log_user(conn, ip)
            active_users.append(user)
            menu(conn, active_users)
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
