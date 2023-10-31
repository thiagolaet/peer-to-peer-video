import socket
import threading
from repositories.user_repository import UserRepository

HOST = "127.0.0.1"
PORT = 65432

delimiter = '0111110'

user_repository = UserRepository()

def get_user(ip):
    user = user_repository.get_by_ip(ip)
    return user

def register(conn, ip):
    conn.send(('O seu IP não foi encontrado na lista de IPs cadastrados, prossiga com o cadastro.\nDigite o nome de usuário: ' + delimiter).encode())
    username = conn.recv(1024).decode()
    is_username_unavailable = user_repository.get_by_username(username) or username == ''
    while is_username_unavailable:
        conn.send(('Nome de usuário inválido ou já cadastrado, por favor digite outro nome de usuário: ' + delimiter).encode())
        username = conn.recv(1024).decode()
        is_username_unavailable = user_repository.get_by_username(username)
    conn.send(('Digite a porta para o recebimento de chamadas: ' + delimiter).encode())
    port = conn.recv(1024).decode()
    while not port:
        conn.send(('Porta inválida, por favor digite outra porta: ' + delimiter).encode())
        port = conn.recv(1024).decode()
    save_user(conn, username, ip, port)

def save_user(conn, username, ip, port):
    user_repository.create(username, ip, port)
    print(f'Usuário salvo com sucesso!\nIP: {ip} | Porta: {port} | Username: {username}')
    conn.send('Cadastro realizado com sucesso!\n'.encode())

def get_user_by_username(conn):
    conn.send(('Digite o nome de usuário: ' + delimiter).encode())
    username = conn.recv(1024).decode()
    user = user_repository.get_by_username(username)
    if user is None:
        msg = 'Usuário não encontrado.\n'
    else:
        msg = f'-----------------------------------\nIP | porta | username\n-----------------------------------\n{user.ip} | {user.port} | {user.username}\n'
    conn.send(msg.encode())

def list_all(conn):
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

def remove_user(conn):
    user_ip = conn.getpeername()[0]
    user = user_repository.get_by_ip(user_ip)
    if user is None:
        msg = 'Usuário não encontrado.\n'
    else:
        user_repository.delete_by_ip(user_ip)
        msg = 'Usuário removido com sucesso.\n'
    conn.send(msg.encode())

def menu(conn):
    while True:
        conn.send(('-----------------------------------\n1 - Listar usuários\n2 - Buscar usuário\n3 - Descadastrar\n4 - Sair\n-----------------------------------' + delimiter).encode())
        user_option = conn.recv(1024).decode()
        if user_option == '1':
            list_all(conn)
        elif user_option == '2':
            get_user_by_username(conn)
        elif user_option == '3':
            remove_user(conn)
            conn.send(('Desconectando...' + delimiter).encode())
            break
        elif user_option == '4':
            conn.send(('Desconectando...' + delimiter).encode())
            break

def handle_client(conn, addr):
    ip, port = addr
    try:
        with conn:
            print(f"Novo usuário conectado: IP {ip}")
            user = get_user(ip)
            if not user:
                register(conn, ip)
            else:
                conn.send(f"Bem-vindo, {user.username}!\n".encode())
            menu(conn)
    except BrokenPipeError as e:
        print(f'O usuário de IP {ip} perdeu conexão.')
    finally:
        conn.close()

def main():
    user_repository.create_tables()
    while True:
        server.listen()
        conn, addr = server.accept()
        client_thread = threading.Thread(target=handle_client, args=(conn, addr))
        client_thread.start()

if __name__ == "__main__":
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    main()
