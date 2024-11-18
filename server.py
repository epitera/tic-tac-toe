import sys
import socket
import selectors
import types
import json
import argparse

sel = selectors.DefaultSelector()
clients = {}
board = [' '] * 9

def register_user(sock, username):
    # first player uses X's
    if not clients:
        symbol = 'X'
    # second player uses O's
    elif len(clients) == 1:
        symbol = 'O'
    # if there is already 2 players connected, send an error response to the client
    else:
        send_message("limit_error", sock, message="There is already 2 players connected")
        sock.close()
        return
    
    clients[username] = sock
    send_message("player_joined", sock, symbol=symbol, message=f"Welcome {username}! Your symbol is '{symbol}'")

    if len(clients) == 2:
        broadcast("start_game", "The game has begun!")

#this method sends a message to all clients unless a client socket is specified to exclude
def broadcast(type, message, board=None, exclude_sock=None):
    for client_sock in clients.values():
        if client_sock != exclude_sock:
            try:
                if type == "player_move" or type == "game_over":
                    send_message(type, client_sock, message=message, board=board)
                else:
                    send_message(type, client_sock, message=message)
                #client_sock.sendall(message.encode())
            except BrokenPipeError:
                print("response failed to send")

def send_message(type, sock, **kwargs):
    response = {"type" : type}
    response.update(kwargs)
    try:
        sock.sendall(json.dumps(response).encode())
    except BrokenPipeError:
        print("response failed to send")

def check_win(board, symbol):
    win_conditions = [
        [0,1,2], [3,4,5], [6,7,8],  
        [0,3,6], [1,4,7], [2,5,8],  
        [0,4,8], [2,4,6]            
    ]

    for condition in win_conditions:
        if board[condition[0]] == symbol and board[condition[1]] == symbol and board[condition[2]] == symbol:
            return True
    return 

def check_draw(board):
    return ' ' not in board

def close_connections():
    for client_sock in clients.values():
        sel.unregister(client_sock)
        client_sock.close()
    sel.close()
    sys.exit(0)

def reset_game():
    global clients, board
    clients = {}
    board =  [' '] * 9

def handle_message(data, sock, addr):
    try:
        message = json.loads(data)
        action = message.get("action")
        username = message["username"]

        if action == "join":
            if username in clients:
                send_message("join_error", sock, message=f"The username {username} is already taken")
            else:
                register_user(sock, username)
        
        elif action == "move":
            move = int(message["move"])
            symbol = message["symbol"]
            board[move] = symbol

            if check_win(board, symbol):
                broadcast("game_over", f"{username} wins!", board)
                reset_game()

            elif check_draw(board):
                broadcast("game_over", "It's a draw!", board)
                reset_game()

            #send updated board to other player
            else:
                broadcast("player_move", f"{username} placed {symbol} on tile {move}", board, sock)

        elif action == "quit":
            #let other client know that the player has quit and delete from client list
            broadcast("player_quit", f"{username} has left the game", sock)
            del clients[username]
            print("closing connection to", addr)
            sel.unregister(sock)
            sock.close()

        elif action == "play_again":
            if message["response"] == "no":
                print("closing connection to", addr)
                sel.unregister(sock)
                sock.close()
            elif message["response"] == "yes":
                register_user(sock, username)


    except json.JSONDecodeError:
        send_message("error", sock, message="Invalid message format")


def accept_wrapper(sock):
    conn, addr = sock.accept()  
    print("accepted connection from", addr)
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  
        if recv_data:
            handle_message(recv_data.decode(), sock, data.addr)

parser = argparse.ArgumentParser(description="Tic-Tac-Toe Server")
parser.add_argument('-p', '--port', type=int, required=True, help="Server Port")
args = parser.parse_args()

host, port = '0.0.0.0', args.port
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host, port))
lsock.listen()
print("listening on", (host, port))
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

try:
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                service_connection(key, mask)
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    sel.close()


