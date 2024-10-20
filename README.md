# tic-tac-toe

This is a simple Tic-Tac-Toe game implemented using Python and sockets.

**How to play:**
1. **Start the server:** Run the `server.py` script with the address and port to listen on as arguments.
2. **Connect clients:** Run the `client.py` script on two different machines or terminals with address and port to connect to as arguments.
3. **Play the game:** Players take turns entering their moves on a 3x3 grid. One player enters circles while the other player enters X's. The first player to get three in a row wins!

**Technologies used:**
* Python
* Sockets

**Additional resources:**
* [https://docs.python.org/3/library/socket.html]

# Message Protocol

## Join
**Client**
 ```json
{
    "action": "join",
    "username": "string" 
}
```

**Server Response (success)**
```json
{
     "type": "player_joined",
     "message": "string"
}
```

**Server Response (error)**
```json
{
    "type": "join_error",
    "message": "string"
}
```

# Quit
**Client**
```json
{
    "action": "quit",
    "username": "string"
}
```

**Server Response**
```json
{
    "type": "player_quit",
    "message": "string"
}
```

# Move
**Client**
```json
{
    "action": "move",
    "username": "string",
    "move": "int"
}
```

**Server response (success)**
```json
{
    "type": "player_move",
    "board": [
        [],
        [],
        []
        ]
}
```

**Server response (error)**
```json
{
    "type": "move_error",
    "message": "string"
}
```
