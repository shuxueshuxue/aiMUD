#!/usr/bin/env python3
"""Full immersive game demonstration with OpenRouter AI"""
import socket
import threading
import time

def send_long_data(sock, data):
    data = data.encode('utf-8')
    length = len(data)
    sock.send(length.to_bytes(4, byteorder='big'))
    sock.send(data)

def recv_long_data(sock):
    sock.settimeout(90)
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

def listen_for_messages(sock, messages_list, running):
    """Background thread to collect server messages"""
    while running[0]:
        try:
            message = recv_long_data(sock)
            if message:
                messages_list.append(('server', message, time.time()))
        except Exception as e:
            if running[0]:
                messages_list.append(('error', str(e), time.time()))
            break

def main():
    print("\n" + "="*80)
    print(" " * 20 + "🎮 AIMUD - FULL GAME EXPERIENCE 🎮")
    print(" " * 15 + "Powered by OpenRouter AI (Gemini 2.5 Pro)")
    print("="*80)

    # Actions to perform
    actions = [
        "explore the dense forest",
        "examine the ancient trees more closely",
        "follow the babbling brook upstream",
        "climb a hill to get a better view",
        "search for interesting stones near the brook"
    ]

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 12345))

    messages = []
    running = [True]

    # Welcome
    welcome = recv_long_data(client)
    print(f"\n📨 SERVER: {welcome}\n")

    # Login
    print("🔐 Logging in as test_player...")
    send_long_data(client, "L")
    print(recv_long_data(client))
    send_long_data(client, "test_player")
    print(recv_long_data(client))
    send_long_data(client, "test123")

    # Get initial game state
    initial_state = recv_long_data(client)
    print("\n" + "="*80)
    print("📖 INITIAL GAME STATE:")
    print("="*80)
    print(initial_state)
    print("="*80)

    # Start listening thread
    listener = threading.Thread(target=listen_for_messages, args=(client, messages, running), daemon=True)
    listener.start()

    time.sleep(2)

    print("\n" + "="*80)
    print("🎬 BEGINNING ADVENTURE - Multiple Actions Demo")
    print("="*80)

    for i, action in enumerate(actions, 1):
        print(f"\n{'='*80}")
        print(f"ACTION #{i}/{len(actions)}: {action}")
        print(f"{'='*80}")
        print(f"⏳ Sending action to AI... (Please wait 15-30 seconds)")
        print(f"🤖 AI Model: Google Gemini 2.5 Pro")

        send_long_data(client, action)

        # Wait for response
        start_time = time.time()
        initial_msg_count = len(messages)

        print(f"\n⌛ Waiting for AI to generate story response...")
        timeout = 60  # 60 seconds timeout

        while time.time() - start_time < timeout:
            if len(messages) > initial_msg_count:
                break
            time.sleep(0.5)
            elapsed = int(time.time() - start_time)
            print(f"\r   ⏱️  Elapsed: {elapsed}s / {timeout}s", end='', flush=True)

        print()  # New line after progress

        # Print any new messages
        new_messages = messages[initial_msg_count:]
        if new_messages:
            for msg_type, msg_content, msg_time in new_messages:
                if msg_type == 'server':
                    print(f"\n{'─'*80}")
                    print(f"✨ AI GENERATED RESPONSE:")
                    print(f"{'─'*80}")
                    print(msg_content)
                    print(f"{'─'*80}")
        else:
            print(f"\n⚠️  No response within {timeout}s timeout")

        # Wait before next action
        if i < len(actions):
            print(f"\n💤 Pausing 3 seconds before next action...")
            time.sleep(3)

    print(f"\n{'='*80}")
    print("🏁 DEMO COMPLETE!")
    print("="*80)
    print(f"\n📊 Total Actions: {len(actions)}")
    print(f"📨 Messages Received: {len(messages)}")
    print(f"\n💡 TIP: The AI generates unique, contextual responses for each action!")
    print(f"🎮 Try your own actions by running: python3 interactive_test.py")
    print("="*80)

    running[0] = False
    send_long_data(client, 'quit')
    time.sleep(1)
    client.close()

if __name__ == '__main__':
    main()
