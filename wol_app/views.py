import socket
import time
import os
import platform
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json

def send_magic_packet(mac_address, ip_address, port):
    # Remove any separators from MAC address
    mac_address = mac_address.replace(":", "").replace("-", "")
    if len(mac_address) != 12:
        raise ValueError("Invalid MAC address format")
    
    # Create the magic packet
    magic_packet = bytes.fromhex("FF" * 6 + mac_address * 16)
    
    # Send the magic packet to the specified IP address and port
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(magic_packet, (ip_address, port))

def is_host_up(ip_address):
    # Ping the host to check if it is up
    param = "-n 1" if platform.system().lower() == "windows" else "-c 1"
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

            # Check if the host is already up
            if is_host_up(ip_address):
                return JsonResponse({'message': 'The computer is already on.', 'success': True})
            
            send_magic_packet(mac_address, ip_address, int(port))
            message = 'Magic packet sent. Waiting for the computer to come online...'
            
            # Wait and check if the host is up
            for i in range(1, 11):
                time.sleep(5)  # Wait for 5 seconds
                if is_host_up(ip_address):
                    message = f'Host is up after {i * 5} seconds.'
                    return JsonResponse({'message': message, 'success': True})
            
            message = 'Magic packet sent but the host is still down after 50 seconds.'
            return JsonResponse({'message': message, 'success': False})
        
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
            if is_host_up(ip_address):
                return JsonResponse({'message': 'Host is up', 'success': True})
            else:
                return JsonResponse({'message': 'Host is down', 'success': False})
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON data'}, status=400)
    
    return JsonResponse({'message': 'Only POST method is allowed'}, status=405)

def wake_on_lan_page(request):
    return render(request, 'wake_on_lan.html')
