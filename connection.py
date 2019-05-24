import socketio as socket
import math
from random import randint,choice


mainsocket = socket.Client()
ip = 'http://localhost'
# ip = 'http://192.168.1.127'
port = '4000'
host = ip + ':' + port
user_name = input('Insert username ')
# tournament_id = input('Insert tournament id ')
tournament_id = '12'


def validateHumanPosition(position):
    if len(position) == 2:
        row = int(position[0])
        col = str(position[1].lower())
        alph = 'abcdefgh'
        return (1 <= row and row <= 8) and (col in alph)
    else:
        return

def validatePosition(cell, board):
    # if len(cell) == 2:
    # row = int(cell[0])
    # col = str(cell[1].lower())
    position = int(cell)
    return board[position] == 0


def human_board(board):
    tileRep = ['_', 'X', 'O']
    N = 8
    result = '    A  B  C  D  E  F  G  H'
    for i in range(len(board)):
        if i % N == 0:
            result += '\n\n ' + str(int(math.floor(i / N)) + 1) + ' '
        result += ' ' + tileRep[board[i]] + ' '
    return result


def ix(row, col):
    return (row - 1) * 8 + 'abcdefgh'.index(col)


def play():
    # alph = ['a','b','d','f','g','h']
    move = randint(0,63)
    # move += choice(alph)
    print('play', move)
    return move


@mainsocket.on('connect')
def on_connect():
    print('I\'m connected!')
    mainsocket.emit('signin', {
        'user_name': user_name,
        'tournament_id': tournament_id,
        'user_role': 'player'
     })


@mainsocket.on('ready')
def on_ready(data):
    print("About to move. Board:\n")
    print(human_board(data['board']))
    print("\nRequesting move...")
    movement = play()
    while not validatePosition(movement, data['board']):
        movement = play()
    print('move to emit:', movement)
    mainsocket.emit('play', {
        "player_turn_id":data['player_turn_id'],
        "tournament_id":tournament_id,
        "game_id":data['game_id'],
        "movement": movement
    })


@mainsocket.on('finish')
def on_finish(data):
    print("game has finished!!")

    mainsocket.emit('player_ready', {
        "tournament_id":tournament_id,
        "game_id":data['game_id'],
        "player_turn_id":data['player_turn_id']
    })

mainsocket.connect(host)