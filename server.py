import socket
import hashlib
import sqlite3
import threading

# Database setup
db_conn = sqlite3.connect('user.db', check_same_thread=False)
c = db_conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT UNIQUE, password_hash TEXT)''')
db_conn.commit()

# Server setup
shutdown_event = threading.Event()
connections = []  # List to keep track of all active connections
lock = threading.Lock()  # Lock for managing access to the connections list

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def send_long_data(conn, data):
    """ Send long data reliably over a socket connection. """
    data = data.encode('utf-8')  # Ensure the data is in bytes
    length = len(data)
    conn.send(length.to_bytes(4, byteorder='big'))  # Send the length of data first
    conn.send(data)  # Send the data

def broadcast(message):
    """ Send a message to all connected clients, ensuring full transmission """
    with lock:
        for conn in connections:
            try:
                send_long_data(conn, message)
            except Exception as e:
                print(f"Error sending message: {e}")
                connections.remove(conn)

def recv_long_data(conn):
    """ Receive long data reliably from a socket connection. """
    length_bytes = conn.recv(4)  # First receive 4 bytes for the length
    if not length_bytes:
        return None
    length = int.from_bytes(length_bytes, byteorder='big')  # Convert bytes to int
    data = b''
    while len(data) < length:
        packet = conn.recv(length - len(data))  # Receive the remaining bytes
        if not packet:
            break  # Connection closed
        data += packet
    return data.decode('utf-8')

action_in_progress = False
action_lock = threading.Lock()






import os
import json
from keywords import create_graph, spot_keywords, extract_keywords
from llm import continueStory

# File Path
GAME_STATE_FILE = "game.txt"

def load_game_state():
    """ Load the current game state from a file. """
    if os.path.exists(GAME_STATE_FILE):
        with open(GAME_STATE_FILE, "r") as file:
            return json.load(file)
    return {"overall_context": "", "keywords": {}, "progress": ""}

def save_game_state(state):
    """ Save the current game state to a file. """
    with open(GAME_STATE_FILE, "w") as file:
        json.dump(state, file, indent=4)





def continue_story(user_input, user_name) -> str:
    """ Process user input and update the game state with dynamic context windows based on specified coefficients. """
    state = load_game_state()
    keywords = state["keywords"]
    overall_context = state["overall_context"]
    full_progress = state["progress"]
    base_window_size = state.get("text_window_size", 1000)  # Base context window size
    word_search_depth = state.get("word_search_depth", 2)

    # Load model configuration
    with open('config.json', 'r') as f:
        config = json.load(f)
    story_model = config['models']['story_continuation']

    # Coefficients for various uses of the window
    coeff_continuation = 1.0
    coeff_keyword_spotting_continuation = 0.5
    coeff_keyword_extraction = 1.0  # Since we use the new segment

    # Calculate window sizes based on coefficients
    window_for_continuation = int(base_window_size * coeff_continuation)
    window_for_keyword_spotting = int(base_window_size * coeff_keyword_spotting_continuation)

    # Truncate the progress for GPT model processing and keyword spotting
    progress_for_continuation = full_progress[-window_for_continuation:]
    progress_for_keyword_spotting = full_progress[-window_for_keyword_spotting:]

    # Create a graph from current keywords
    keyword_graph = create_graph(keywords, directed=False)

    # Spot keywords in the context window specifically for keyword spotting
    relevant_keywords = spot_keywords(progress_for_keyword_spotting + " " + user_input, keywords, depth=word_search_depth, graph=keyword_graph)

    # Update progress and context using GPT model with filtered keywords
    new_progress_segment = continueStory(progress_for_continuation, overall_context, user_name, user_input, {k: keywords[k] for k in relevant_keywords if k in keywords}, model=story_model)
    full_progress += " " + new_progress_segment  # Append new segment to full progress

    # Save the full progress back to state
    state["progress"] = full_progress

    save_game_state(state)

    # Generate and return response to the server
    return new_progress_segment

def extract_key_words(new_progress_segment):
    state = load_game_state()
    keywords = state["keywords"]
    overall_context = state["overall_context"]
    full_progress = state["progress"]
    base_window_size = state.get("text_window_size", 1000)  # Base context window size
    
    keyword_graph = create_graph(keywords, directed=False)

    # Re-run keyword spotting on the new progress segment
    new_relevant_keywords = spot_keywords(new_progress_segment, keywords, depth=2, graph=keyword_graph)

    # Extract and update keywords from the new story segment using the latest spotted keywords
    new_keywords = extract_keywords({k: keywords[k] for k in new_relevant_keywords if k in keywords}, new_progress_segment)
    if new_keywords: 
        state["keywords"].update(new_keywords)

    # Save the updated game state
    save_game_state(state)

    return None


def handle_client(conn):
    global action_in_progress
    with lock:
        connections.append(conn)
    try:
        send_long_data(conn, 'Welcome to the Game! Do you want to [R]egister or [L]ogin?')
        mode = recv_long_data(conn).strip().upper()

        if mode == 'R':
            send_long_data(conn, 'Enter username: ')
            username = recv_long_data(conn).strip()
            send_long_data(conn, 'Enter password: ')
            password = recv_long_data(conn).strip()
            password_hash = hash_password(password)
            try:
                c.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password_hash))
                db_conn.commit()
                send_long_data(conn, 'Registration successful! You can now login.\n')
            except sqlite3.IntegrityError:
                send_long_data(conn, 'Username already exists. Please try again.\n')
            return  # Exit after registration to prompt for login
        elif mode == 'L':
            send_long_data(conn, 'Enter username: ')
            username = recv_long_data(conn).strip()
            send_long_data(conn, 'Enter password: ')
            password = recv_long_data(conn).strip()
            password_hash = hash_password(password)
            c.execute('SELECT * FROM users WHERE username=? AND password_hash=?', (username, password_hash))
            if c.fetchone():
                game_state = load_game_state()
                send_long_data(conn, f"Login successful! Current Progress:\n\n{game_state['progress']}\n")
                broadcast(f"[{username} logs in.]")

                while True:
                    user_input = recv_long_data(conn)
                    if not user_input or user_input.strip() == "quit":
                        break  # Disconnect if input is empty

                    with action_lock:
                        if action_in_progress:
                            send_long_data(conn, "[Another action is currently being processed. Please wait.]")
                            continue

                        action_in_progress = True

                    # Process action
                    try:
                        broadcast(f"[Action taken by {username}: {user_input}]")
                        feedback = continue_story(user_input, username)
                        broadcast(feedback)  # Broadcast the feedback from main to all users
                        broadcast("[Keywords generating...]")
                        extract_key_words(feedback)
                        broadcast("[Keywords generation completed.]")

                    finally:
                        with action_lock:
                            action_in_progress = False
            else:
                send_long_data(conn, 'Login failed. Check your username and password.\n')
    finally:
        with lock:
            if conn in connections:
                connections.remove(conn)
        conn.close()

def start_server():
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = '127.0.0.1'
    port = 12345
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print('Server started. Listening for connections...')

    while not shutdown_event.is_set():
        try:
            client, addr = server_socket.accept()
            print(f'Connected to: {addr[0]}:{addr[1]}')
            threading.Thread(target=handle_client, args=(client,)).start()
        except OSError as e:
            print("Server socket has been closed.", e)
            break

def stop_server():
    shutdown_event.set()
    server_socket.close()
    db_conn.close()
    print('Server has been shut down.')

# Optional: Implement a simple CLI to control the server
def server_control():
    while True:
        cmd = input('Enter "stop" to stop the server: ')
        if cmd == "stop":
            stop_server()
            break
        else:
            try:
                exec(cmd)
            except Exception as e:
                print(e)

if __name__ == "__main__":
    threading.Thread(target=start_server).start()
    server_control()
