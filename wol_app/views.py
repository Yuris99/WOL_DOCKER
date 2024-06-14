import socket
import json
import os
import platform
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

def send_magic_packet(mac_address, ip_address, port):
    mac_address = mac_address.replace(":", "").replace("-", "")
    if len(mac_address) != 12:
        raise ValueError("Invalid MAC address format")
    magic_packet = bytes.fromhex("FF" * 6 + mac_address * 16)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(magic_packet, (ip_address, port))

def is_host_up(ip_address, timeout=5):
    param = "-n 1 -w {}".format(timeout * 1000) if platform.system().lower() == "windows" else "-c 1 -W {}".format(timeout)
    response = os.system(f"ping {param} {ip_address}")
    return response == 0

@csrf_exempt
def wake_and_check(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            mac_address = data.get('mac_address')
            ip_address = data.get('ip_address')
            port = data.get('port')

            errors = {}

            if not mac_address or len(mac_address.replace(":", "").replace("-", "")) != 12:
                errors['mac_address'] = 'Invalid MAC address format'

            if not ip_address:
                errors['ip_address'] = 'IP address is required'

            if not port:
                errors['port'] = 'Port is required'
            elif not isinstance(port, int) or port <= 0 or port > 65535:
                errors['port'] = 'Invalid port number'

            if errors:
                return JsonResponse({'message': 'Validation failed', 'success': False, 'errors': errors})

            if is_host_up(ip_address):
                return JsonResponse({'message': 'The computer is already on.', 'success': True})

            send_magic_packet(mac_address, ip_address, int(port))

            return JsonResponse({'message': 'Magic packet sent. Checking status...', 'success': True})
        
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'message': 'Invalid data', 'success': False}, status=400)
    
    return JsonResponse({'message': 'Only POST method is allowed', 'success': False}, status=405)

@csrf_exempt
def execute_cmd(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            file_name = data.get('file_name')
            if file_name:
                success = send_file_selection_to_client(file_name)
                if success:
                    return JsonResponse({'message': 'Execution completed successfully.', 'success': True})
                else:
                    return JsonResponse({'message': 'Execution failed.', 'success': False})
            else:
                return JsonResponse({'message': 'No file selected', 'success': False}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON data'}, status=400)
    
    return JsonResponse({'message': 'Only POST method is allowed', 'success': False}, status=405)

@csrf_exempt
def check_host_up(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ip_address = data.get('ip_address')
            if is_host_up(ip_address):
                return JsonResponse({'message': 'Host is up', 'success': True})
            else:
                return JsonResponse({'message': 'Host is down', 'success': False})
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON data'}, status=400)
    
    return JsonResponse({'message': 'Only POST method is allowed', 'success': False}, status=405)

@csrf_exempt
def get_cmd_files(request):
    try:
        cmd_files = os.listdir('./execlist')  # 클라이언트에서 실행 가능한 .cmd 파일 목록을 가져옴
        cmd_files = [f for f in cmd_files if f.endswith('.cmd')]
        return JsonResponse({'cmd_files': cmd_files})
    except Exception as e:
        return JsonResponse({'message': str(e), 'success': False}, status=500)

def get_cmd_files_from_client():
    server_address = ('client_ip', 5051)  # 클라이언트 IP와 포트
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(server_address)
        data = sock.recv(4096)
        cmd_files = json.loads(data.decode('utf-8')).get('cmd_files', [])
    return cmd_files

def send_file_selection_to_client(file_name):
    server_address = ('client_ip', 5051)  # 클라이언트 IP와 포트
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(server_address)
        sock.sendall(file_name.encode('utf-8'))
        result = json.loads(sock.recv(1024).decode('utf-8'))
    return result.get('execution_result', False)

def wake_on_lan_page(request):
    return render(request, 'my_app/wake_on_lan.html')
