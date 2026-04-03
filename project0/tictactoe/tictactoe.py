"""
Tic Tac Toe Player
"""

import math

X = "X"
O = "O"
EMPTY = None

def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]
    
def is_cell_empty(cell):
    return cell == EMPTY
    
def player(board):
    number_of_actions = 0
    
    for row in board:
        number_of_actions += len([cell for cell in row if not is_cell_empty(cell)])
    
    return X if number_of_actions % 2 == 0 else O

def actions(board):
    result = set()
    
    for row_index in range(len(board)):
        row = board[row_index]
        
        for cell_index in range(len(row)):
            cell = row[cell_index]
            
            if is_cell_empty(cell):
                result.add((row_index, cell_index))
        
    return result

def result(board, action):
    new_board = [[cell for cell in row] for row in board]
    
    row_index, cell_index = action
    
    if row_index not in range(3) or cell_index not in range(3) or not is_cell_empty(new_board[row_index][cell_index]):
        raise Exception
    
    new_board[row_index][cell_index] = player(board)
    
    return new_board

def winner(board):
    if any(all(cell == X for cell in row) for row in board):
        return X
    
    if any(all(cell == O for cell in row) for row in board):
        return O
    
    if any(all(cell == X for cell in column) for column in get_columns(board)):
        return X
    
    if any(all(cell == O for cell in column) for column in get_columns(board)):
        return O
    
    if board[0][0] == board[1][1] == board[2][2]:
        return board[0][0]
    
    if board[0][2] == board[1][1] == board[2][0]:
        return board[0][2]
    
def terminal(board):
    if winner(board):
        return True
    
    for row in board:
        if any(is_cell_empty(cell) for cell in row):
            return False
        
    return True

def utility(board):
    who_won = winner(board) 
    
    return 1 if who_won == X else -1 if who_won == O else 0

def minimax(board):
    if terminal(board):
        return None

    current_player = player(board)

    if current_player == X:
        best_score = -math.inf
        best_action = None
        for action in actions(board):
            score = min_value(result(board, action))
            if score > best_score:
                best_score = score
                best_action = action
        return best_action

    best_score = math.inf
    best_action = None
    for action in actions(board):
        score = max_value(result(board, action))
        if score < best_score:
            best_score = score
            best_action = action
    return best_action


def max_value(board):
    if terminal(board):
        return utility(board)

    v = -math.inf
    for action in actions(board):
        v = max(v, min_value(result(board, action)))
    return v


def min_value(board):
    if terminal(board):
        return utility(board)

    v = math.inf
    for action in actions(board):
        v = min(v, max_value(result(board, action)))
    return v

def get_columns(board):
    result = []
    
    for i in range(3):
        result.append([board[0][i], board[1][i], board[2][i]])
        
    return result