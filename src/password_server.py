import socket
from src.core.state import app_state   # usa o objeto global

def run_server(host="127.0.0.1", port=5001):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(1)
    print(f"Server running on {host}:{port}")

    while True:
        conn, addr = server.accept()
        request = conn.recv(1024).decode().strip()

        if request == "GET_MASTER_PASSWORD":
            if app_state.crypto.decrypted_pass:
                conn.sendall(app_state.crypto.decrypted_pass.encode())
            else:
                conn.sendall(b"ERROR: User not authenticated")
        else:
            conn.sendall(b"ERROR: Invalid request")

        conn.close()