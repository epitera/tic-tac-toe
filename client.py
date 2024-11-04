import sys
import socket
import json
import time
import selectors
import types

def handle_response(data):
    global game_started, player_turn, symbol, board, game_over

    response = json.loads(data)
    type = response.get("type")
    print()
    print(response["message"])

    #if the username was already taken, prompt user to try again
    if type == "join_error":
        username = input("Enter a username: ")
        send_message("join", username)
        recv_data = sock.recv(1024)
        if recv_data:
            handle_response(recv_data.decode())

    #first player who joined is 'X' and moves first
    #second player who joined is 'O' and moves second
    elif type == "player_joined":
        symbol = response["symbol"]
        if symbol == 'X':
            player_turn = True

    #if there is already 2 players connected, disconnect
    elif type == "limit_error":
        print(f"Closing connection to {(host, port)}")
        sock.close()

    elif type == "start_game":
        game_started = True

    elif type == "player_move":
        board = response["board"]
        player_turn = True

    elif type == "player_quit":
        print("You Win!")
        game_over = True


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

def print_board():
    print("Current Board:")
    print(f"{board[0]} | {board[1]} | {board[2]}")
    print("--+---+--")
    print(f"{board[3]} | {board[4]} | {board[5]}")
    print("--+---+--")
    print(f"{board[6]} | {board[7]} | {board[8]}")
    print()

def check_move(move):
    if (move < 0 or move > 8) or board[move] != ' ':
        return False
    return True

board = [' '] * 9
symbol = ' '
player_turn = False
game_started = False
game_over = False
host, port = sys.argv[1], int(sys.argv[2])
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
username = input("Enter a username: ")
start_connection(host, port, username)

print("Waiting for game to start")
while not game_started:
    try:
        recv_data = sock.recv(1024)
        if recv_data:
            handle_response(recv_data.decode())
    except BlockingIOError:
        time.sleep(0.1)

try:
    while not game_over:
        if player_turn:
            print_board()
            action = input("Your Turn: Enter Action (quit, move): ")

            if action == "move":
                move = input("Enter a tile (0-8): ")
                is_valid = check_move(int(move))
                if is_valid:
                    send_message(action, username=username, move=move, symbol=symbol)
                    player_turn = False
                else:
                    print("\nInvalid move, try again\n")
                continue
            elif action == "quit":
                send_message(action, username=username)
                print(f"Closing connection to {(host, port)}")
                break
            else:
                print("invalid input")
                continue

            #recv_data = sock.recv(1024)
            #if recv_data:
                #handle_response(recv_data.decode())
        
        else:
            print("Waiting for opponent to finish turn")
            try:
                recv_data = sock.recv(1024)
                if recv_data:
                    handle_response(recv_data.decode())
            except BlockingIOError:
                time.sleep(0.1)

except ConnectionRefusedError:
    print(f"Failed to connect to {(host, port)}")
finally:
    sock.close()
