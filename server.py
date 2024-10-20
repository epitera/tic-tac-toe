import sys
import socket
import selectors
import types
import json

sel = selectors.DefaultSelector()
clients = {}

#this method sends a message to all clients unless a client socket is specified to exclude

def broadcast(message, exclude_sock=None):
    for client_sock in clients.values():
        if client_sock != exclude_sock:
            try:
                client_sock.sendall(message.encode())
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
                clients[username] = sock
                send_message("player_joined", sock, message=f"Welcome {username}!")
        
        elif action == "move":
            move = int(message["move"])
            #check if move entered was a number between 0-8
            #will also need to check if the tile number was already marked at later point
            if move < 0 or move > 8:
                send_message("move_error", sock, message="Invalid move, try again")
            else:
                send_message("player_move", sock, message="Hold your horses, game logic hasn't been implemented yet")
        
        #elif action == "chat":
            #chat_message = message["message"]
            #chat_message = username + " says: " + chat_message
            #send this message to the other client
            #broadcast(chat_message)

        elif action == "quit":
            #let other client know that the player has quit and delete from client list
            broadcast(f"{username} has left the game", sock)
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
            #data.outb += recv_data
        #else:
            #print("closing connection to", data.addr)
            #sel.unregister(sock)
            #sock.close()
    #if mask & selectors.EVENT_WRITE:
        #if data.outb:
            #print("echoing", repr(data.outb), "to", data.addr)
            #sent = sock.send(data.outb)  
            #data.outb = data.outb[sent:]

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


