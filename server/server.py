import socket
from repositories.user_repository import UserRepository

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports  are > 1023)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

user_repository = UserRepository()

def is_ip_registered(ip):
    user = user_repository.get_by_ip(ip)
    return user

def register(conn, ip):
    conn.send('O seu IP não foi encontrado na lista de IPs cadastrados, prossiga com o cadastro.\nDigite o nome de usuário: '.encode())
    username = conn.recv(1024).decode()
    conn.send('Digite a porta para o recebimento de chamadas: '.encode())
    port = conn.recv(1024).decode()
    save_user(conn, username, ip, port)

def save_user(conn, username, ip, port):
    user_repository.create(username, ip, port)
    print(f'Usuário salvo com sucesso!\nIP: {ip} | Porta: {port} | Username: {username}')
    conn.send('Cadastro realizado com sucesso!\n'.encode())

def menu(conn):
    while True:
        conn.send('-----------------------------------\n1 - Listar usuários\n2 - Buscar usuário\n3 - Descadastrar\n4 - Sair\n-----------------------------------'.encode())
        user_option = conn.recv(1024).decode()
        print(user_option)
        if user_option == '4':
            conn.send('Desconectando...'.encode())
            break

def main():
    user_repository.create_tables()
    while True:
        server.listen()
        conn, addr = server.accept()
        ip, port = conn.getpeername()
        with conn:
            print(f"Novo usuário conectado: IP {ip}")
            if not is_ip_registered(ip):
                register(conn, ip)
            menu(conn)
        conn.close()

if __name__ == "__main__":
    main()
