import sys
import socket
import json
import time
import argparse
import selectors
import types

recv_buffer = ''

def read_messages():
    global recv_buffer
    try:
        recv_data = sock.recv(1024)
        if recv_data:
            recv_buffer += recv_data.decode()
            while '\n' in recv_buffer:
                message, recv_buffer = recv_buffer.split('\n', 1)
                handle_response(message)
    except BlockingIOError:
        time.sleep(0.1)

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
        read_messages()

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
        sys.exit(0)

    elif type == "start_game":
        game_started = True

    elif type == "player_move":
        board = response["board"]
        player_turn = True

    elif type == "player_quit":
        game_over = True

    elif type == "game_over":
        board = response["board"]
        print_board()
        game_over = True
        game_started = False
        prompt_play_again()

def send_message(action, **kwargs):
    message = {"action": action}
    message.update(kwargs)
    try:
        sock.sendall((json.dumps(message) + '\n').encode())
    except BrokenPipeError:
        print("message failed to send")

def start_connection(host, port, username):
    sock.connect((host, port))
    print(f"Starting connection to {(host, port)}")
    send_message("join", username=username)
    while True:
        read_messages()
        if symbol != ' ':
            break

def print_board():
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

def prompt_play_again():
    global game_over, board
    response = ''
    while response.lower() not in ['yes', 'no']:
        response = input("Do you want to play again? (yes/no): ")
    send_message("play_again", username=username, response=response.lower())

    if response == 'no':
        print("Thank you for playing!")
        sock.close()
        sys.exit(0)

    elif response == "yes":
        board = [' '] * 9
        game_over = False
        wait_for_game()

def wait_for_game():
    print("Waiting for game to start")
    while not game_started:
        read_messages()

parser = argparse.ArgumentParser(description="Tic-Tac-Toe Client")
parser.add_argument('-i', '--ip', required=True, help="Server IP / DNS")
parser.add_argument('-p', '--port', type=int, required=True, help="Server Port")
args = parser.parse_args()

board = [' '] * 9
symbol = ' '
player_turn = False
game_started = False
game_over = False
host, port = args.ip, args.port
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
username = input("Enter a username: ")
start_connection(host, port, username)

wait_for_game()

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
                sock.close()
                sys.exit(0)
            else:
                print("invalid input")
                continue
        
        else:
            print("Waiting for opponent to finish turn")
            read_messages()

except ConnectionRefusedError:
    print(f"Failed to connect to {(host, port)}")
finally:
    sock.close()
