import os
import socket
import json
import subprocess

def get_cmd_files():
    cmd_files = [f for f in os.listdir('./execlist') if f.endswith('.cmd')]
    return cmd_files

def send_cmd_file_list(sock):
    cmd_files = get_cmd_files()
    data = json.dumps({"cmd_files": cmd_files})
    sock.sendall(data.encode('utf-8'))

def receive_file_selection(sock):
    data = sock.recv(1024)
    return data.decode('utf-8')

def execute_cmd_file(file_name):
    file_path = os.path.join('./execlist', file_name)
    result = subprocess.run([file_path], capture_output=True, text=True)
    return result.returncode == 0

def send_execution_result(sock, success):
    result = {"execution_result": success}
    sock.sendall(json.dumps(result).encode('utf-8'))

def main():
    server_address = ('server_ip', 5051)  # 서버 IP와 포트

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(server_address)
        send_cmd_file_list(sock)
        selected_file = receive_file_selection(sock)
        success = execute_cmd_file(selected_file)
        send_execution_result(sock, success)

if __name__ == "__main__":
    main()
