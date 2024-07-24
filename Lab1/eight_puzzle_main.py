import random

from search import astar_search, EightPuzzle

state = [1, 2, 3, 4, 5, 6, 7, 8, 0]
puzzle = EightPuzzle(tuple(state))
solution = None

b = [None] * 9


def scramble():
    """Scrambles the puzzle starting from the goal state"""

    global state
    global puzzle
    possible_actions = ['UP', 'DOWN', 'LEFT', 'RIGHT']
    scramble = []
    for _ in range(60):
        scramble.append(random.choice(possible_actions))

    for move in scramble:
        if move in puzzle.actions(state):
            state = list(puzzle.result(state, move))
            puzzle = EightPuzzle(tuple(state))


def solve():
    """Solves the puzzle using astar_search"""

    return astar_search(puzzle).solution()


def solve_steps():
    """Solves the puzzle step by step"""

    global puzzle
    global solution
    global state
    solution = solve()
    print(solution)


def init():
    """Calls necessary functions"""

    global state
    global solution
    state = [1, 2, 3, 4, 5, 6, 7, 8, 0]
    scramble()
    print(state)
    solve_steps()


init()
