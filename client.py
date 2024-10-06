import sys
import socket
import selectors
import types

host, port = sys.argv[1], int(sys.argv[2])
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, port))
print(f"Starting connection to {(host, port)}")

try:
    while True:
        message = input("Enter message to send (or 'exit' to quit): ")
        if message.lower() == "exit":
            print(f"Closing connection to {(host, port)}")
            break
        sock.sendall(message.encode())
        data = sock.recv(1024)
        print(f"Received {repr(data)} from {(host, port)}")
except ConnectionRefusedError:
    print(f"Failed to connect to {(host, port)}")
finally:
    sock.close()