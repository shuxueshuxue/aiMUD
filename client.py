import socket
import threading

def send_long_data(sock, data):
    """ Send long data reliably over a socket connection. """
    data = data.encode('utf-8')  # Ensure the data is in bytes
    length = len(data)
    sock.send(length.to_bytes(4, byteorder='big'))  # Send the length of data first
    sock.send(data)  # Send the data

def recv_long_data(sock):
    """ Receive long data reliably from a socket connection. """
    length_bytes = sock.recv(4)  # First receive 4 bytes for the length
    if not length_bytes:
        return None
    length = int.from_bytes(length_bytes, byteorder='big')  # Convert bytes to int
    data = b''
    while len(data) < length:
        packet = sock.recv(length - len(data))  # Receive the remaining bytes
        if not packet:
            break  # Connection closed
        data += packet
    return data.decode('utf-8')

def listen_for_messages(sock):
    """ Continuously listen for messages from the server and print them. """
    try:
        while True:
            message = recv_long_data(sock)
            if message:
                print(message)
            else:
                break  # Stop listening if no data is received (connection closed)
    finally:
        sock.close()

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = '127.0.0.1'
    port = 12345

    client_socket.connect((host, port))
    response = recv_long_data(client_socket)
    print(response)

    # Start a thread to continuously listen for messages
    threading.Thread(target=listen_for_messages, args=(client_socket,), daemon=True).start()

    try:
        while True:
            message = input("")  # Prompt for user input
            if message.lower() == 'quit':  # Allow command to break the loop and close connection
                send_long_data(client_socket, message)
                break
            send_long_data(client_socket, message)
    except KeyboardInterrupt:
        pass  # Handle Ctrl+C gracefully

    client_socket.close()

if __name__ == '__main__':
    main()
