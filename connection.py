import sys
import socketio as socket
import math
import copy

# agoritm taked and dated from http://dhconnelly.com/paip-python/docs/paip/othello.html#section-14
mainsocket = socket.Client()
ip = 'http://192.168.1.6'
#samip
# ip = 'http://192.168.1.127'
port = '4000'
host = ip + ':' + port
# user_name = input('Insert username ')
user_name = 'Desktop'
# tournament_id = input('Insert tournament id ')
tournament_id = '12'
N: int = 8

def validatePosition(x, y):
    '''
    validates if postion is valid
    '''
    if 0 <= x <= 7 and 0 <= y <= 7:
        return True
    return False


#function adapted from https://inventwithpython.com/chapter15.html
def is_valid_move(board, player_turn_id, x, y):
    global N
    index = x * N + y
    tilesToFlip = []
    index_of_tiles = []
    position_around = [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]

    if board[index] != 0 or not validatePosition(x, y):
        return False, tilesToFlip, None
    testboard = copy.deepcopy(board)
    testboard[index] = player_turn_id

    oponent_turn_id = 1
    if player_turn_id == 1:
        oponent_turn_id = 2


    for xd, yd in position_around:
        i, j = x, y

        i += xd
        j += yd

        if validatePosition(i, j) and testboard[i*N+j] == oponent_turn_id:
            i += xd
            j += yd
            if not validatePosition(i, j):
                continue
            while testboard[i*N + j] == oponent_turn_id:
                i += xd
                j += yd

                if not validatePosition(i, j):
                    break
            if not validatePosition(i, j):
                continue
            if testboard[i*N + j] == player_turn_id:
                while True:
                    i -= xd
                    j -= yd

                    if i == x and j == y:
                        break
                    tilesToFlip.append([i, j])
    if len(tilesToFlip) > 0:
        for i in tilesToFlip:
            index = i[0] * N + i[1]
            testboard[index] = player_turn_id
            index_of_tiles.append(index)
        return True, index_of_tiles, testboard
    else:
        return False, index_of_tiles,testboard


def generate_valid_moves(board, playerTurnID):
    possible_moves = []
    result_boards = []
    for x in range(8):
        for y in range(8):
            is_valid, tilesToFlip, new_board = is_valid_move(board, playerTurnID, x, y)
            if is_valid:
                possible_moves.append(ix(x,y))
                result_boards.append(new_board)
    return possible_moves, result_boards


def human_board(board):
    global N
    tileRep = ['_', 'X', 'O']
    result = '    A  B  C  D  E  F  G  H'
    for i in range(len(board)):
        if i % N == 0:
            result += '\n\n ' + str(int(math.floor(i / N)) + 1) + ' '
        result += ' ' + tileRep[board[i]] + ' '
    return result


def ix(row, col):
    return row * 8 + col


def processMove(base_board, tilesToFlip, player_turn_id):
    '''
    this function creates the new board with the flipped coins
    :param base_board: the pre-existing  board
    :param tilesToFlip: list of index to change
    :param player_turn_id: 1 or 2
    :return: the new board
    '''
    print('proces_move', base_board, tilesToFlip, player_turn_id)
    new_board = copy.deepcopy(base_board)
    for position in tilesToFlip:
        new_board[position] = player_turn_id
    return new_board


def evaluateBoard(gameBoard):
    player = 0
    oponent = 0
    for space in gameBoard:
        if space == 1:
            player += 1
        elif space == 2:
            oponent += 1
    # coner give a bonus
    cornerBonus = 10
    corner_position = [0,7,56,63]
    for corner in corner_position:
        if gameBoard[corner] == 1:
            player += cornerBonus
        elif gameBoard[corner] == 2:
            oponent += cornerBonus
    return abs(player-oponent)



def minimax(gameBoard, depth, maximizingPlayer, player_turn_id):
    a = -sys.maxsize - 1
    b = sys.maxsize
    oponent_turn_id = 1
    if player_turn_id == 1:
        oponent_turn_id = 2
    # if gets to the depth
    if depth == 0:
        return evaluateBoard(gameBoard)

    # Calcuting moves
    moves, new_boards = generate_valid_moves(gameBoard, player_turn_id)
    bestcoordinate = 0
    if maximizingPlayer:
        for board in new_boards:
            v = minimax(board, depth - 1, not maximizingPlayer, player_turn_id)
            if v > a:
                a = v
                bestcoordinate = board
            if a >= b:
                break
        if bestcoordinate == 0:
            return 0
        else:
            return moves[new_boards.index(bestcoordinate)]

    else:
        for board in new_boards:
            v = minimax(board, depth - 1, not maximizingPlayer, oponent_turn_id);
            if v < b:
                b = v
                bestcoordinate = board

            if a >= b:
                break
        if bestcoordinate == 0:
            return 0
        else:
            return moves[new_boards.index(bestcoordinate)]


def play(data):
    # move = randint(0,63)
    move = minimax(data['board'], 3, True, data['player_turn_id'])
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
    print(data)
    print("About to move. Board:\n")
    print(human_board(data['board']))
    print("\nRequesting move...")
    mainsocket.emit('play', {
        "player_turn_id":data['player_turn_id'],
        "tournament_id":tournament_id,
        "game_id":data['game_id'],
        "movement": minimax(data['board'], 4, True, data['player_turn_id'])
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