import os.path
import sys
from tkmacosx import Button
from tkinter import *

from games import random_player, Game, GameState, alpha_beta_cutoff_search

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

EMPTY = 0
PLAYER_WHITE = 1
PLAYER_WHITE_KING = 2
PLAYER_BLACK = 3
PLAYER_BLACK_KING = 4


# "gen_state" can be used to generate a game state to apply the algorithm
def gen_state(to_move='X', board=[]):
    """Given whose turn it is to move, the positions of X's on the board, the
    positions of O's on the board, and, (optionally) number of rows, columns
    and how many consecutive X's or O's required to win, return the corresponding
    game state"""

    moves = get_all_moves(board, 'X')
    return GameState(to_move=to_move, utility=0, board=board, moves=moves)


def find_middle(from_index, index_to):
    from_row, from_column = to_point(from_index)
    to_row, to_column = to_point(index_to)
    delta_row = 1 if from_row < to_row else -1
    delta_column = 1 if from_column < to_column else -1
    return to_index(int(from_row + delta_row), int(from_column + delta_column))


def make_move(board, from_index, to_index):
    from_value = board[from_index]
    board[from_index] = EMPTY
    board[to_index] = from_value
    from_row, from_column = to_point(from_index)
    to_row, to_column = to_point(to_index)
    if abs(from_row - to_row) > 1:
        middle = find_middle(from_index, to_index)
        board[middle] = EMPTY
    if to_index < 4 or to_index > 28:
        if board[to_index] == PLAYER_WHITE:
            board[to_index] = PLAYER_WHITE_KING
        if board[to_index] == PLAYER_BLACK:
            board[to_index] = PLAYER_BLACK_KING


class Checkers(Game):
    """Play Checkers on an h x v board, with Max (first player) playing 'X'.
    A state has the player to move, a cached utility, a list of moves in
    the form of a list of (x, y) positions, and a board, in the form of
    a dict of {(x, y): Player} entries, where Player is 'X' or 'O'."""

    def __init__(self):
        moves = []
        self.initial = GameState(to_move='X', utility=0, board={}, moves=moves)

    def actions(self, state):
        """Legal moves are any square not yet taken."""
        return state.moves

    def result(self, state, move):
        if move not in state.moves:
            return state  # Illegal move has no effect
        board = state.board.copy()
        from_index, to_index = move
        make_move(board, from_index, to_index)
        # moves = state.moves
        # moves.remove(move)
        moves = get_all_moves(board, state.to_move)
        new_state = GameState(to_move=('O' if state.to_move == 'X' else 'X'),
                         utility=self.compute_utility(board, move, state.to_move),
                         board=board, moves=moves)
        return new_state

    def utility(self, state, player):
        """Return the value to player; 1 for win, -1 for loss, 0 otherwise."""
        return state.utility if player == 'X' else -state.utility

    def terminal_test(self, state):
        """A state is terminal if it is won or there are no empty squares."""
        return state.utility != 0 or len(state.moves) == 0

    def display(self, state):
        board = state.board
        for i in range(0, len(board)):
            if i % 4 == 0 and i != 0:
                print()
            if i % 8 == 0:
                print('  ', end='')
            text = 'o'
            if board[i] == PLAYER_WHITE or board[i] == PLAYER_WHITE_KING:
                text = 'W'
            elif board[i] == PLAYER_BLACK or board[i] == PLAYER_BLACK_KING:
                text = 'B'
            print(text, ' ', end='')
        print()

    def compute_utility(self, board, move, player):
        """If 'X' wins with this move, return 1; if 'O' wins return -1; else return 0."""
        board_copy = board.copy()
        a, b = move
        make_move(board_copy, a, b)
        has_white = 0
        has_black = 0
        for i in range(0, len(board_copy)):
            if board_copy[i] == PLAYER_WHITE or board_copy[i] == PLAYER_WHITE_KING:
                has_white += 1
            if board_copy[i] == PLAYER_BLACK or board_copy[i] == PLAYER_BLACK_KING:
                has_black += 1
        sign = 1 if player == 'X' else -1
        if has_white > 0 and has_black == 0:
            return has_white*sign
        if has_black > 0 and has_white == 0:
            return has_black*-1*sign
        return 0


def display_winner():
    global result, new_board
    has_white = 0
    has_black = 0
    for i in range(0, len(new_board)):
        if new_board[i] == PLAYER_WHITE or new_board[i] == PLAYER_WHITE_KING:
            has_white += 1
        if new_board[i] == PLAYER_BLACK or new_board[i] == PLAYER_BLACK_KING:
            has_black += 1
    if has_black > 0 and has_white > 0:
        result.set("It's a tie")
    elif has_black > 0 and has_white == 0:
        result.set("You lose :(")
    else:
        result.set("You win!")
    disable_game()


def reset_board():
    board = []
    for i in range(0, 12):
        board.append(PLAYER_BLACK)

    for i in range(0, 8):
        board.append(EMPTY)

    for i in range(0, 12):
        board.append(PLAYER_WHITE)
    return board


def to_index(row, column):
    if row < 0 or column < 0 or row > 7 or column > 7:
        return -1
    return int(row * 4 + column / 2)


def to_point(index):
    row = index / 4
    column = 2 * (index % 4) + (row + 1) % 2
    return int(row), int(column)


def add_points(board, points, row, column, value, delta):
    is_king = (value == PLAYER_BLACK_KING or value == PLAYER_WHITE_KING)
    opposite_player = PLAYER_BLACK
    opposite_king = PLAYER_BLACK_KING
    if value == PLAYER_BLACK or value == PLAYER_BLACK_KING:
        opposite_player = PLAYER_WHITE
        opposite_king = PLAYER_WHITE_KING

    if is_king or value == PLAYER_BLACK:
        new_index = to_index(row + delta, column + delta)
        if 0 <= new_index < 32 and board[new_index] == EMPTY:
            if delta == 1:
                points.append(new_index)
            else:
                middle_value = board[to_index(row + 1, column + 1)]
                if middle_value == opposite_player or middle_value == opposite_king:
                    points.append(new_index)
        new_index = to_index(row + delta, column - delta)
        if 0 <= new_index < 32 and board[new_index] == EMPTY:
            if delta == 1:
                points.append(new_index)
            else:
                middle_value = board[to_index(row + 1, column - 1)]
                if middle_value == opposite_player or middle_value == opposite_king:
                    points.append(new_index)

    if is_king or value == PLAYER_WHITE:
        new_index = to_index(row - delta, column + delta)
        if 0 <= new_index < 32 and board[new_index] == EMPTY:
            if delta == 1:
                points.append(new_index)
            else:
                middle_value = board[to_index(row - 1, column + 1)]
                if middle_value == opposite_player or middle_value == opposite_king:
                    points.append(new_index)
        new_index = to_index(row - delta, column - delta)
        if 0 <= new_index < 32 and board[new_index] == EMPTY:
            if delta == 1:
                points.append(new_index)
            else:
                middle_value = board[to_index(row - 1, column - 1)]
                if middle_value == opposite_player or middle_value == opposite_king:
                    points.append(new_index)


def get_moves(board, row, column, value):
    points = []
    add_points(board, points, row, column, value, 1)
    return points


def get_all_moves(board, color):
    moves = []
    for i in range(0, len(board)):
        if (color == 'X' and (board[i] == PLAYER_BLACK or board[i] == PLAYER_BLACK_KING)) or \
                (color == 'O' and (board[i] == PLAYER_WHITE or board[i] == PLAYER_WHITE_KING)):
            row, column = to_point(i)
            current_jumps = get_jumps(board, row, column, board[i])
            for j in range(0, len(current_jumps)):
                if current_jumps:
                    moves.append((i, current_jumps[j]))
            current_moves = get_moves(board, row, column, board[i])
            for j in range(0, len(current_moves)):
                moves.append((i, current_moves[j]))
    return moves


def get_jumps(board, row, column, value):
    points = []
    add_points(board, points, row, column, value, 2)
    return points


ttt = Checkers()
root = None
buttons = []
frames = []
new_board = reset_board()
move_from = -1
count = 0
sym = ""
result = None
choices = None
depth_choices = None
eval_choices = None



def repaint_buttons():
    global buttons, new_board

    for index in range(0, len(new_board)):
        row, column = to_point(index)

        value = new_board[to_index(row, column)]
        # index_string = '-{}'.format(index)
        index_string = ''
        text = '{}'.format(index_string)
        if value == PLAYER_WHITE_KING or value == PLAYER_BLACK_KING:
            text = 'K{}'.format(index_string)
        elif value == PLAYER_BLACK or value == PLAYER_WHITE:
            text = 'O{}'.format(index_string)

        color = 'green'
        if value == PLAYER_BLACK or value == PLAYER_BLACK_KING:
            color = 'black'
        elif value == PLAYER_WHITE or value == PLAYER_WHITE_KING:
            color = 'red'
        buttons[row][column].config(text=text)
        buttons[row][column].config(fg=color)


# eval 1 finds the difference between the values of black and white pieces.
def eval_1(state, player):
    has_white = 0
    has_black = 0
    board_copy = state.board
    for i in range(0, len(board_copy)):
        if board_copy[i] == PLAYER_WHITE or board_copy[i] == PLAYER_WHITE_KING:
            has_white += 1
        if board_copy[i] == PLAYER_BLACK or board_copy[i] == PLAYER_BLACK_KING:
            has_black += 1
    sign = 1 if player == 'X' else -1
    result = (has_black - has_white) * sign
    return result


# 7. finds how many pieces a player has. player is trying not to lose more pieces.
def eval_2(state, player):
    has_white = 0
    has_black = 0
    board_copy = state.board
    for i in range(0, len(board_copy)):
        if board_copy[i] == PLAYER_WHITE or board_copy[i] == PLAYER_WHITE_KING:
            has_white += 1
        if board_copy[i] == PLAYER_BLACK or board_copy[i] == PLAYER_BLACK_KING:
            has_black += 1
    sign = 1 if player == 'X' else -1
    result = has_black * sign
    if player == 'O':
        result = has_white * sign
    return result


def create_frames(root):
    """
    This function creates the necessary structure of the game.
    """
    frame1 = Frame(root)
    frame2 = Frame(root)
    frame3 = Frame(root)
    frame4 = Frame(root)
    frame5 = Frame(root)
    frame6 = Frame(root)
    frame7 = Frame(root)
    frame8 = Frame(root)
    frame9 = Frame(root)
    create_buttons(frame1, 0)
    create_buttons(frame2, 1)
    create_buttons(frame3, 2)
    create_buttons(frame4, 3)
    create_buttons(frame5, 4)
    create_buttons(frame6, 5)
    create_buttons(frame7, 6)
    create_buttons(frame8, 7)
    buttonExit = Button(
        frame9, height=1, width=2,
        text="Exit",
        command=lambda: exit_game(root))
    buttonExit.pack(side=LEFT)
    frame9.pack(side=BOTTOM)
    frame8.pack(side=BOTTOM)
    frame7.pack(side=BOTTOM)
    frame6.pack(side=BOTTOM)
    frame5.pack(side=BOTTOM)
    frame4.pack(side=BOTTOM)
    frame3.pack(side=BOTTOM)
    frame2.pack(side=BOTTOM)
    frame1.pack(side=BOTTOM)
    frames.append(frame1)
    frames.append(frame2)
    frames.append(frame3)
    frames.append(frame4)
    frames.append(frame5)
    frames.append(frame6)
    frames.append(frame7)
    frames.append(frame8)
    for x in frames:
        buttons_in_frame = []
        for y in x.winfo_children():
            buttons_in_frame.append(y)
        buttons.append(buttons_in_frame)
    repaint_buttons()


def get_button_color(index):
    return 'white' if index % 2 == 0 else 'black'


def create_buttons(frame, index):
    """
    This function creates the buttons to be pressed/clicked during the game.
    """
    button0 = Button(frame, height=2, width=2, text=" ", highlightbackground=get_button_color(index + 0),
                     command=lambda: on_click(button0))
    button0.pack(side=LEFT)
    button1 = Button(frame, height=2, width=2, text=" ", highlightbackground=get_button_color(index + 1),
                     command=lambda: on_click(button1))
    button1.pack(side=LEFT)
    button2 = Button(frame, height=2, width=2, text=" ", highlightbackground=get_button_color(index + 2),
                     command=lambda: on_click(button2))
    button2.pack(side=LEFT)
    button3 = Button(frame, height=2, width=2, text=" ", highlightbackground=get_button_color(index + 3),
                     command=lambda: on_click(button3))
    button3.pack(side=LEFT)
    button4 = Button(frame, height=2, width=2, text=" ", highlightbackground=get_button_color(index + 4),
                     command=lambda: on_click(button4))
    button4.pack(side=LEFT)
    button5 = Button(frame, height=2, width=2, text=" ", highlightbackground=get_button_color(index + 5),
                     command=lambda: on_click(button5))
    button5.pack(side=LEFT)
    button6 = Button(frame, height=2, width=2, text=" ", highlightbackground=get_button_color(index + 6),
                     command=lambda: on_click(button6))
    button6.pack(side=LEFT)
    button7 = Button(frame, height=2, width=2, text=" ", highlightbackground=get_button_color(index + 7),
                     command=lambda: on_click(button7))
    button7.pack(side=LEFT)


def on_click(button):
    """
    This function determines the action of any button.
    """
    global ttt, choices, depth_choices, eval_choices, count, sym, result, new_board, move_from

    if count % 2 == 0:
        sym = "X"
    else:
        sym = "O"
    count += 1

    x, y = get_coordinates(button)
    row = x
    column = y
    board_index = to_index(row, column)
    print("Clicked on row {}, column {}".format(row, column))
    board_value = new_board[board_index]
    # print("Board index = {}, value = {}".format(board_index, board_value))
    if board_value == PLAYER_WHITE or board_value == PLAYER_WHITE_KING:
        move_from = board_index
        print("Moving from = {}".format(move_from))
        moves = get_moves(new_board, row, column, board_value)
        print("Legal moves = {}".format(moves))
        jumps = get_jumps(new_board, row, column, board_value)
        print("Legal jumps = {}".format(jumps))
        return
    if board_value == PLAYER_BLACK or board_value == PLAYER_BLACK_KING:
        return

    print("Moving from {} to {}".format(move_from, board_index))
    row_from, column_from = to_point(move_from)
    from_board_value = new_board[move_from]
    moves = get_all_moves(new_board, 'O')
    if len(moves) == 0:
        display_winner()
        return
    print("Legal moves = {}".format(moves))
    jumps = get_jumps(new_board, row_from, column_from, from_board_value)
    print("Legal jumps = {}".format(jumps))
    if (move_from, board_index) not in moves:
        return
    make_move(new_board, move_from, board_index)

    y += 1
    state = gen_state(to_move='O', board=new_board)
    ttt.display(state)
    repaint_buttons()
    choice = choices.get()
    depth = depth_choices.get()
    evaluate = eval_choices.get()
    if "Random" in choice:
        opponent_move = random_player(ttt, state)
    else:
        opponent_move = alpha_beta_cutoff_search(state, ttt, int(depth), None, lambda state: globals()[evaluate](state, 'X'))
    if opponent_move is None:
        display_winner()
        return
    a, b = opponent_move
    print("search {}".format(a, b))
    make_move(new_board, a, b)
    repaint_buttons()
    move_from = -1


def get_coordinates(button):
    """
    This function returns the coordinates of the button clicked.
    """
    global buttons
    for x in range(len(buttons)):
        for y in range(len(buttons[x])):
            if buttons[x][y] == button:
                return x, y


def get_button(x, y):
    """
    This function returns the button memory location corresponding to a coordinate.
    """
    global buttons
    return buttons[x][y]


def disable_game():
    """
    This function deactivates the game after a win, loss or draw.
    """
    global frames
    for x in frames:
        for y in x.winfo_children():
            y.config(state='disabled')


def exit_game(root):
    """
    This function will exit the game by killing the root.
    """
    root.destroy()


if __name__ == "__main__":
    #global result, choices

    root = Tk()
    root.title("Checkers")
    root.geometry("600x500")  # Improved the window geometry
    root.resizable(0, 0)  # To remove the maximize window option
    result = StringVar()
    result.set("Your Turn!")
    w = Label(root, textvariable=result)
    w.pack(side=BOTTOM)
    create_frames(root)
    choices = StringVar(root)
    choices.set("Vs Legend")
    menu = OptionMenu(root, choices, "Vs Random",  "Vs Legend")
    menu.pack()
    depth_choices = StringVar(root)
    depth_choices.set(4)
    depth_choices_menu = OptionMenu(root, depth_choices, 4, 8, 12)
    depth_choices_menu.pack()
    eval_choices = StringVar(root)
    eval_choices.set('eval_1')
    eval_choices_menu = OptionMenu(root, eval_choices, "eval_1", "eval_2")
    eval_choices_menu.pack()
    root.mainloop()
