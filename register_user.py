#!/usr/bin/env python3
"""Register a user for aiMUD"""
import socket

def send_long_data(sock, data):
    data = data.encode('utf-8')
    length = len(data)
    sock.send(length.to_bytes(4, byteorder='big'))
    sock.send(data)

def recv_long_data(sock, timeout=5):
    sock.settimeout(timeout)
    length_bytes = sock.recv(4)
    if not length_bytes:
        return None
    length = int.from_bytes(length_bytes, byteorder='big')
    data = b''
    while len(data) < length:
        packet = sock.recv(length - len(data))
        if not packet:
            break
        data += packet
    return data.decode('utf-8')

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 12345))

# Get welcome
print(recv_long_data(client))

# Register
send_long_data(client, "R")
print(recv_long_data(client))  # username prompt

send_long_data(client, "test_player")
print(recv_long_data(client))  # password prompt

send_long_data(client, "test123")
print(recv_long_data(client))  # result

client.close()
