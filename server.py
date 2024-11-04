import sys
import socket
import selectors
import types
import json

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
                if type == "player_move":
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

            #send updated board to other player
            broadcast("player_move", f"{username} placed {symbol} on tile {move}", board, sock)

        elif action == "quit":
            #let other client know that the player has quit and delete from client list
            broadcast("player_quit", f"{username} has left the game", sock)
            del clients[username]
            print("closing connection to", addr)
            sel.unregister(sock)
            sock.close()

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

host, port = sys.argv[1], int(sys.argv[2])
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


