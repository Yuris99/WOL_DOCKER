import socket
import time
import os
import platform
from django.http import JsonResponse
from django.shortcuts import render

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

def send_wol_packet(request):
    if request.method == 'POST':
        mac_address = request.POST.get('mac_address')
        ip_address = request.POST.get('ip_address')
        port = int(request.POST.get('port', 9))
        message = ''
        success = False
        errors = {}

        if not mac_address or len(mac_address.replace(":", "").replace("-", "")) != 12:
            errors['mac_address'] = 'Invalid MAC address format'

        if not ip_address:
            errors['ip_address'] = 'IP address is required'

        if errors:
            return JsonResponse({'message': 'Validation failed', 'success': success, 'errors': errors})

        try:
            send_magic_packet(mac_address, ip_address, port)
            for i in range(1, 6):
                time.sleep(1)  # Wait for 1 second
                if is_host_up(ip_address):
                    message = f'Host is up after {i} seconds.'
                    success = True
                    break
            else:
                message = 'Magic packet sent but the host is still down after 5 seconds.'
        except Exception as e:
            message = f'Failed to send magic packet: {e}'
        
        return JsonResponse({'message': message, 'success': success, 'errors': errors})
    return render(request, 'send_packet.html')
