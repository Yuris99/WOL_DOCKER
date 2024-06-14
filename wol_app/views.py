import os
import socket
import platform
import subprocess
import time
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json

def send_magic_packet(mac_address, ip_address, port):
    mac_address = mac_address.replace(":", "").replace("-", "")
    if len(mac_address) != 12:
        raise ValueError("Invalid MAC address format")
    magic_packet = bytes.fromhex("FF" * 6 + mac_address * 16)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(magic_packet, (ip_address, port))

def is_host_up(ip_address, mac_address):
    if platform.system().lower() == "windows":
        try:
            output = subprocess.check_output(f"arp -a {ip_address}", shell=True).decode()
            return mac_address.lower() in output.lower()
        except subprocess.CalledProcessError:
            return False
    else:
        try:
            output = subprocess.check_output(f"arp -n {ip_address}", shell=True).decode()
            return mac_address.lower() in output.lower()
        except subprocess.CalledProcessError:
            return False

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

            # Check if the host is already up
            if is_host_up(ip_address, mac_address):
                return JsonResponse({'message': 'The computer is already on.', 'success': True})
            else:
                # If ARP check fails, send WoL packet
                send_magic_packet(mac_address, ip_address, int(port))
                return JsonResponse({'message': 'Magic packet sent. Waiting for the computer to come online...', 'success': True})
        
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'message': 'Invalid data', 'success': False}, status=400)
    
    return JsonResponse({'message': 'Only POST method is allowed', 'success': False}, status=405)

@csrf_exempt
def receive_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print('Received data:', data)
            return JsonResponse({'message': 'Data received successfully.'})
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON data'}, status=400)
    
    return JsonResponse({'message': 'Only POST method is allowed'}, status=405)

@csrf_exempt
def check_host_up(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ip_address = data.get('ip_address')
            mac_address = data.get('mac_address')
            if is_host_up(ip_address, mac_address):
                return JsonResponse({'message': 'Host is up', 'success': True})
            else:
                return JsonResponse({'message': 'Host is down', 'success': False})
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON data'}, status=400)
    
    return JsonResponse({'message': 'Only POST method is allowed', 'success': False}, status=405)

@csrf_exempt
def get_cmd_files(request):
    if request.method == 'GET':
        execlist_path = os.path.join(os.path.expanduser("~"), "current_folder", "execlist")
        cmd_files = [f for f in os.listdir(execlist_path) if f.endswith('.cmd')]
        return JsonResponse({'cmd_files': cmd_files})

@csrf_exempt
def execute_cmd(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        cmd_file = data.get('cmd_file')
        execlist_path = os.path.join(os.path.expanduser("~"), "current_folder", "execlist")
        cmd_file_path = os.path.join(execlist_path, cmd_file)

        if os.path.isfile(cmd_file_path):
            try:
                subprocess.run(['cmd.exe', '/c', cmd_file_path], check=True)
                return JsonResponse({'message': 'Command executed successfully', 'success': True})
            except subprocess.CalledProcessError as e:
                return JsonResponse({'message': f'Error executing command: {str(e)}', 'success': False})
        else:
            return JsonResponse({'message': 'Command file not found', 'success': False})

    return JsonResponse({'message': 'Only POST method is allowed', 'success': False}, status=405)

def wake_on_lan_page(request):
    return render(request, 'my_app/wake_on_lan.html')
