# tic-tac-toe

This is a simple Tic-Tac-Toe game implemented using Python and sockets.

**How to play:**
1. **Start the server:** Run the `server.py` script with the port to listen on as an argument like this: server.py -p PORT. (IP address is set to 0.0.0.0)
2. **Connect clients:** Run the `client.py` script on two different machines or terminals with address and port to connect to as arguments. usage: client.py -i IP -p PORT
3. **Play the game:** Players take turns entering their moves on a 3x3 grid. One player enters circles while the other player enters X's. The first player to get three in a row wins!

**Technologies used:**
* Python
* Sockets

**Additional resources:**
* [https://docs.python.org/3/library/socket.html]

# Multi-Player Functionality

## Game State Synchronization
* Server keeps track of the board, initially each tile is an empty space
* When a player enters a move (0-8), the server updates the board and sends it to the other player
* This creates a back and forth of the board being continuosly updated until a player wins (win conditions still need to be implemented)

## Client-Side Game Rendering
* The updated board recieved from the server is displayed before the player makes their move

## Turn-Based Gameplay
* The first player who connected makes the first move
* When player 1 makes their move and player 2 receives the updated game board from the server, it is automatically set to player 2's turn
* While it is not a player's turn, they cannot enter a move on the command line

## Player Identification
* When a client makes a connection to the server, they are asked to enter a username
* If the username is already taken by the other player, they are informed and prompted to enter a different username
* On the server side, a hash map is used to link a player's username to their socket

# Game play, Game State, UI
* Command Line Interface based gameplay
* Server checks for win conditions every time a move if received from the client
* Prompts both users if they want to play again once match has ended

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

**Server Response (username already taken error)**
```json
{
    "type": "join_error",
    "message": "string"
}
```

**Server Response (too many players error)**
```json
{
    "type": "limit_error",
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
    "move": "int",
    "symbol": "char"
}
```

**Server response (success)**
```json
{
    "type": "player_move",
    "message": "string",
    "board": []
}
```

**Server response (error)**
```json
{
    "type": "move_error",
    "message": "string"
}
```

# Start game
**Server**
```json
{
   "type": "start_game",
   "message": "string"
}
```

#Game over
**Server**
```json
{
    "type": "game_over",
    "message": "string",
    "board": []
}
```

#Play Again
**Client**
```json
{
    "type": "play_again",
    "username": "string",
    "response": "string"
}
```
