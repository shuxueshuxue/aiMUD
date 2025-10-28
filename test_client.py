#!/usr/bin/env python3
"""Test client for aiMUD server"""
import socket
import time

def send_long_data(sock, data):
    """Send long data reliably over a socket connection."""
    data = data.encode('utf-8')
    length = len(data)
    sock.send(length.to_bytes(4, byteorder='big'))
    sock.send(data)

def recv_long_data(sock, timeout=10):
    """Receive long data reliably from a socket connection."""
    sock.settimeout(timeout)
    try:
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
    except socket.timeout:
        return None

def test_game():
    """Test the game server"""
    print("=" * 60)
    print("Testing aiMUD Game Server")
    print("=" * 60)

    # Connect to server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = '127.0.0.1'
    port = 12345

    try:
        print(f"\n[1] Connecting to {host}:{port}...")
        client_socket.connect((host, port))
        print("✓ Connected successfully!")

        # Receive welcome message
        print("\n[2] Receiving welcome message...")
        response = recv_long_data(client_socket)
        if response:
            print("Server says:")
            print("-" * 60)
            print(response)
            print("-" * 60)

        # Try Login first (user might already exist)
        print("\n[3] Attempting login...")
        username = "test_player"
        password = "test123"

        # Send 'L' for login
        send_long_data(client_socket, "L")
        time.sleep(0.3)

        # Receive username prompt
        response = recv_long_data(client_socket, timeout=5)
        if response:
            print(f"Server: {response.strip()}")

        # Send username
        send_long_data(client_socket, username)
        time.sleep(0.3)

        # Receive password prompt
        response = recv_long_data(client_socket, timeout=5)
        if response:
            print(f"Server: {response.strip()}")

        # Send password
        send_long_data(client_socket, password)
        time.sleep(0.3)

        # Receive login response
        response = recv_long_data(client_socket, timeout=5)
        if response:
            print("\n[4] Server response:")
            print("-" * 60)
            print(response)
            print("-" * 60)

        # Send a game command
        print("\n[5] Sending game command: 'look around'...")
        send_long_data(client_socket, "look around")

        # Wait for response (this might trigger an API call)
        print("\n[6] Waiting for game response (may take 10-20s for API call)...")
        response = recv_long_data(client_socket, timeout=30)
        if response:
            print("\nGame Response:")
            print("=" * 60)
            print(response)
            print("=" * 60)
        else:
            print("⚠ No response received (timeout)")

        print("\n[7] Test complete! Disconnecting...")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client_socket.close()
        print("✓ Disconnected")

    print("\n" + "=" * 60)

if __name__ == '__main__':
    test_game()
