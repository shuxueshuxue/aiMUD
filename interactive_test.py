#!/usr/bin/env python3
"""Interactive test for aiMUD with OpenRouter"""
import socket
import threading
import time

def send_long_data(sock, data):
    data = data.encode('utf-8')
    length = len(data)
    sock.send(length.to_bytes(4, byteorder='big'))
    sock.send(data)

def recv_long_data(sock):
    sock.settimeout(60)  # Long timeout for API calls
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

def listen_for_messages(sock, running):
    """Background thread to listen for server messages"""
    while running[0]:
        try:
            message = recv_long_data(sock)
            if message:
                print(f"\n{'='*60}")
                print("SERVER MESSAGE:")
                print(message)
                print('='*60)
                print("\nYour action: ", end='', flush=True)
        except Exception as e:
            if running[0]:  # Only print error if not intentionally closed
                print(f"\nConnection error: {e}")
            break

def main():
    print("="*70)
    print("aiMUD - Interactive Game Test with OpenRouter API")
    print("="*70)

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 12345))

    # Welcome
    print("\n" + recv_long_data(client))

    # Login
    send_long_data(client, "L")
    print(recv_long_data(client))

    send_long_data(client, "test_player")
    print(recv_long_data(client))

    send_long_data(client, "test123")

    # Get game state
    response = recv_long_data(client)
    print("\n" + "="*70)
    print(response)
    print("="*70)

    # Start listening thread
    running = [True]
    listener = threading.Thread(target=listen_for_messages, args=(client, running), daemon=True)
    listener.start()

    print("\n" + "="*70)
    print("You are now in the game! Type actions and wait for AI responses.")
    print("Type 'quit' to exit.")
    print("="*70)
    print("\nSuggested actions: 'explore the forest', 'examine my tools', 'walk to the brook'")
    print()

    while True:
        try:
            action = input("\nYour action: ").strip()
            if action.lower() == 'quit':
                send_long_data(client, 'quit')
                break
            if action:
                print(f"\n[Sending action to server... please wait 10-30s for AI response]")
                send_long_data(client, action)
                time.sleep(1)  # Give server time to process
        except KeyboardInterrupt:
            break

    running[0] = False
    client.close()
    print("\nDisconnected from game. Goodbye!")

if __name__ == '__main__':
    main()
