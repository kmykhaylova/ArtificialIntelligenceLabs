import pandas as pd
import sys
from utils import *

from search import astar_search, breadth_first_graph_search, iterative_deepening_search, EightPuzzle

state = [1, 2, 3, 4, 5, 6, 7, 8, 0]
puzzle = EightPuzzle(tuple(state))
solution = None

b = [None] * 9


def solve():
    """Solves the puzzle using astar_search"""
    return astar_search(puzzle, display=True).solution()


def solve_steps():
    """Solves the puzzle step by step"""
    global puzzle
    global solution
    global state
    solution = solve()
    print(solution)


def read_state(filename):
    """Import a file and convert it to an array of integers"""
    file = pd.read_csv(filename, delim_whitespace=True, header=None)
    flat_list = [item for sublist in file.values for item in sublist]
    for idx, item in enumerate(flat_list):
        if item == '_':
            flat_list[idx] = 0
        flat_list[idx] = int(flat_list[idx])
    return flat_list


def main():
    global state
    global solution
    global puzzle

    if len(sys.argv) != 3:
        print_solution("Must provide two parameters: file name and type of algorithm")
        return
    filename = sys.argv[1]
    algorithm = sys.argv[2]

    state = read_state(filename)
    puzzle = EightPuzzle(tuple(state))

    if not puzzle.check_solvability(state):
        print('The inputted puzzle is not solvable:')
        with open(filename, 'r') as file:
            print(file.read())
        return

    """Cases of each input algorithm with their printed solution"""
    match algorithm:
        case 'BFS':
            result = breadth_first_graph_search(puzzle)
            if result:
                solution = result.solution()
                print_solution(solution)
        case 'IDS':
            result = iterative_deepening_search(puzzle)
            if result:
                solution = result.solution()
                print_solution(solution)
        case 'h1':
            h = memoize(puzzle.h, 'h')
            result = astar_search(puzzle, lambda n: misplaced(n) + h(n), display=True)
            if result:
                solution = result.solution()
                print_solution(solution)
        case 'h2':
            h = memoize(puzzle.h, 'h')
            result = astar_search(puzzle, lambda n: n.path_cost + h(n), display=True)
            if result:
                solution = result.solution()
                print_solution(solution)
        case 'h3':
            h = memoize(puzzle.h, 'h')
            result = astar_search(puzzle, lambda n: custom_sums(n) + h(n), display=True)
            if result:
                solution = result.solution()
                print_solution(solution)
        case _:
            print('Error: unsupported algorithm ' + algorithm)


def misplaced(n):
    """count misplaced tiles"""
    result = 0
    for i in range(1, 9):
        if n.state[i - 1] != i:
            result += 1

    return result


def custom_sums(n):
    """check whether the sum of current states' rows or columns is the same or different from the sum of the
    goal states """
    result = 0
    result = result + abs(n.state[0] + n.state[1] + n.state[2] - 6)
    result = result + abs(n.state[3] + n.state[4] + n.state[5] - 15)
    result = result + abs(n.state[6] + n.state[7] + n.state[8] - 15)

    result = result + abs(n.state[0] + n.state[3] + n.state[6] - 12)
    result = result + abs(n.state[1] + n.state[4] + n.state[7] - 15)
    result = result + abs(n.state[2] + n.state[5] + n.state[8] - 9)
    return result


def print_solution(solution):
    result = ''
    for i in range(0, len(solution)):
        result = result + solution[i][0]
    print('Path length:', len(solution))
    print('Path:', result)


if __name__ == '__main__':
    main()
