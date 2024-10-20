import sys
import socket
import json
import selectors
import types

def handle_response(data):
    response = json.loads(data)
    type = response.get("type")
    print(response["message"])

    #if the username was already taken, prompt user to try again
    if type == "join_error":
        username = input("Enter a username: ")
        send_message("join", username)
        recv_data = sock.recv(1024)
        if recv_data:
            handle_response(recv_data.decode())

def send_message(action, **kwargs):
    message = {"action": action}
    message.update(kwargs)
    try:
        sock.sendall(json.dumps(message).encode())
    except BrokenPipeError:
        print("message failed to send")

def start_connection(host, port, username):
    sock.connect((host, port))
    print(f"Starting connection to {(host, port)}")
    send_message("join", username=username)
    recv_data = sock.recv(1024)
    if recv_data:
        handle_response(recv_data.decode())

host, port = sys.argv[1], int(sys.argv[2])
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
username = input("Enter a username: ")
start_connection(host, port, username)

try:
    while True:
        action = input("Enter Action (quit, move): ")
        #if action == "chat":
            #user_message = input("Enter your message: ")
            #send_message(action, username=username, message=user_message)
        if action == "move":
            move = input("Enter a tile (0-8): ")
            send_message(action, username=username, move=move)
        elif action == "quit":
            send_message(action, username=username)
            print(f"Closing connection to {(host, port)}")
            break
        else:
            print("invalid input")
            continue

        recv_data = sock.recv(1024)
        if recv_data:
            handle_response(recv_data.decode())
        #if message.lower() == "quit":
            #print(f"Closing connection to {(host, port)}")
            #break
        #sock.sendall(message.encode())
        #data = sock.recv(1024)
        #print(f"Received {repr(data)} from {(host, port)}")
except ConnectionRefusedError:
    print(f"Failed to connect to {(host, port)}")
finally:
    sock.close()
