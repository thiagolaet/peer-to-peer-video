import socket

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

def is_ip_registered(ip):
    return False

def register(conn, ip):
    conn.send('O seu IP não foi encontrado na lista de IPs cadastrados, prossiga com o cadastro.\nDigite o nome de usuário: '.encode())
    username = conn.recv(1024).decode()
    conn.send('Digite a porta para recebimento de chamadas: '.encode())
    port = conn.recv(1024).decode()
    save_user(conn, username, ip, port)

def save_user(conn, username, ip, port):
    conn.send('Usuário cadastrado com sucesso!'.encode())
    print(f'Usuário salvo com sucesso!\nIP: {ip} Porta: {port} Username: {username}')

def menu(conn):
    while True:
        conn.send('1 - Listar usuários\n\n3 - Descadastrar\n4 - Sair\n'.encode())
        user_option = conn.recv(1024)
        if user_option == '4':
            break

def main():
    while True:
        server.listen()
        conn, addr = server.accept()
        ip, port = conn.getpeername()
        with conn:
            print(f"Novo usuário conectado: IP {ip}")
            if not is_ip_registered(conn, ip):
                register(conn)
            menu()

if __name__ == "__main__":
    main()
