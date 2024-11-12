# Homework 1 for CS 541, Ness Blackbird
# Initialize the board.

# And also set up an array of text objects. We'll need to have them around to keep
# redrawing the numbers.
texts = []

import numpy as np
from numpy._core.defchararray import lower
from copy import deepcopy
from manual import manual_play, move, get_blank_pos

def stringify(board):
    # Turn the board 2-d array into a string.
    s = ''
    for i in range(len(board)):
        for j in range(len(board[i])):
            s += board[i][j]
    return s

def count_inversions(s):
    # Check if the given string represents a soluble puzzle. If the number of inversions is even, it
    # can be solved.
    inv_count = 0
    for i in range(0, 8):
        for j in range(i + 1, 9):
            # Ignore the blank.
            if s[j] != ' ' and s[i] != ' ' and s[i] > s[j]:
                inv_count = inv_count + 1
    return inv_count

def h_tiles_incorrect(nd):
    board = nd.board
    # Count the number of incorrect tiles, and use that as the heuristic of how good this board is.
    s = stringify(board)
    if use_a_star:
        n = nd.depth
    else:
        n = 0
    for i in range(len(s)):
        if s[i] != should[i]:
            n = n + 1
    return n

def is_solution(nd):
    board = nd.board
    # Count the number of incorrect tiles.
    s = stringify(board)
    for i in range(len(s)):
        if s[i] != should[i]:
            return False
    return True

def h_manhattan(nd):
    # Calculate the Manhattan distance between each tile and where it should be.
    board = nd.board
    if use_a_star:
        total = nd.depth
    else:
        total = 0
    for i in range(len(board)):
        for j in range(len(board[i])):
            # Subtract one because should_reverse is 0-based, but the tiles are 1-based.
            if board[i][j] != ' ':
                t = int(board[i][j]) - 1
                total += abs(should_reverse[t][0] - i) + abs(should_reverse[t][1] - j)
    return total

def top_line(nd):
    # Check if the top line is done yet.
    board = nd.board
    lined_up = True
    for i in range(len(board[0])):
        # This is one of the top line tiles. Is it in place? We have to add one because tiles are 1-based.
        if board[0][i] == ' ' or int(board[0][i]) != i + 1:
            lined_up = False
    return lined_up

def h_custom(nd):
    # Calculate the Manhattan distance between each tile and where it should be, but if we haven't yet
    # completed the top line, treat all numbers > 3 as if they didn't need to be positioned, so the
    # algorithm focuses on the top line.
    if use_a_star:
        total = nd.depth
    else:
        total = 0

    board = nd.board
    for i in range(len(board)):
        for j in range(len(board[i])):
            # Subtract one because should_reverse is 0-based, but the tiles are 1-based.
            if board[i][j] == ' ':
                # Try to keep the space out of the top line, but don't try too hard.
                if i == 0:
                    total += 1
            else:
                t = int(board[i][j]) - 1
                if nd.top_line:
                    total += abs(should_reverse[t][0] - i) + abs(should_reverse[t][1] - j)
                else:
                    # The top line isn't complete, so ignore numbers 4 and above.
                    if t < 4:
                        total += abs(should_reverse[t][0] - i) + abs(should_reverse[t][1] - j)
    return total


def get_actions(board):
    # Generate a list of possible actions from the board.
    b = get_blank_pos(board)
    acts = []
    if b['x'] > 0:
        acts.append('right')
    if b['x'] < 2:
        acts.append('left')
    if b['y'] > 0:
        acts.append('down')
    if b['y'] < 2:
        acts.append('up')
    return acts

def select_node():
    # Select the node with the cheapest cost to proceed with.
    current = False
    best = 1000
    for ix in fringe:
        nd = fringe[ix]
        # Find the lowest cost -- but don't lose a top line, if we have one and this is the heuristic
        # that uses it (nd.top_line will not be set unless we're on the right one).
        # True is 1 in Python, so make sure we don't take a non-top-line node over a top-line node.
        if not current or nd.top_line > current.top_line:
            current = nd
            best = current.cost
        else:
            if nd.cost < best:
                current = nd
                best = current.cost

    # Return the whole node.
    return current

class Node:
    def __init__(self, nd, board, act):
        if nd:
            self.depth = nd.depth + 1
        else:
            self.depth = 0
        self.parent = nd
        self.source_action = act
        self.board = board
        self.s = stringify(self.board)
        boards_seen[self.s] = self
        self.children = []
        # Don't record top_line unless we're on the right heuristic.
        if heuristic == h_custom:
            # It's on the fringe when it's created. But don't add it if it violates the top-line principle.
            tl = top_line(self)
            # Add it to the fringe unless it doesn't have its top line and the parent does.
            if not nd or not (nd.top_line and not tl):
                fringe[self.s] = self
            self.top_line = tl
        else:
            fringe[self.s] = self
            self.top_line = False
        self.cost = heuristic(self)

    def add_child(self, board, act):
        t = Node(self, board, act)
        self.children.append(t)
        boards_seen[stringify(board)] = t
        return t

# Set up a template of where each tile oughta be.
# should = [[1, 2, 3], [4, 5, 6], [7, 8, 0], []]
should = '12345678 '
# These are y, x
should_reverse = [[0, 0], [0, 1], [0, 2], [1, 0], [1, 1], [1, 2], [2, 0], [2, 1], [2, 2]]

starts = ['45 618732', '54 618732', '182 43765', '87654321 ', ' 12345678']

# Select algorithm and heuristic.
# Unfortunately, the debug function in PyCharm isn't consistent with using Python input.
ask = True
if ask:
    config = input('Enter 1-5 to select a configuration: ')
    config = int(config)
    if config < 1 or config > 5:
        raise ValueError('Config must be between 1 and 5')
    start = starts[int(config) - 1]

    if input('Enter m for manual play: ') == 'm':
        manual_play(start)
        exit()

    algorithm = lower(input('Algorithm: Enter a for a*, or b for best-first: '))
    use_a_star = (algorithm == 'a')

    heur = lower(input('Heuristic: enter c for "count correct tiles," m for "manhattan distance," or t for "top line": '))
    heuristic = False
    if heur == 'c':
        heuristic = h_tiles_incorrect

    if heur == 'm':
        heuristic = h_manhattan

    if heur == 't':
        heuristic = h_custom

    if not heuristic:
        raise Exception('Invalid heuristic.')
else:
    heuristic = h_tiles_incorrect
    config = 2
    start = starts[int(config) - 1]
    use_a_star = True


# Keep track of if we've ever seen a "top line" one.
was_top_line = False

if (count_inversions(start) % 2):
    print(f'Puzzle has {count_inversions(start)} inversions, and is not soluble.')

root_board = [[], [], []]
root_board[0] = [start[0], start[1], start[2]]
root_board[1] = [start[3], start[4], start[5]]
root_board[2] = [start[6], start[7], start[8]]

fringe = {}
# We'll need to remember all the nodes we've seen. Do them by string, it'll be faster, I guess.
boards_seen = {}
root = Node(False, root_board, False)

done = False
success = True
node = root
count = 0
while not done:
    count += 1

    # Select a node to investigate next.
    node = select_node()
    print(f'node: {node.s}, depth: {node.depth} count: {count} fringe: {len(fringe)}, top line: {top_line(node)}')

    # This node is no longer on the fringe.
    del fringe[node.s]

    # Get a list of possible actions from this state.
    actions = get_actions(node.board)

    # Make a node for each of those, if it hasn't already been checked.
    for action in actions:
        leaf_board = move(node.board, action)
        s = stringify(leaf_board)
        if not (s in boards_seen):
            child = node.add_child(leaf_board, action)
            if top_line(child) and not was_top_line:
                # Now that we've seen a top_line node, we don't want to consider any non-top-line ones.
                # Remove them from the fringe.
                fringe = {s: child}
                # Only do this once.
                was_top_line = True

            if is_solution(child):
                success = True
                done = True
                break

    # If the fringe is empty, we're done.
    if not len(fringe):
        success = False
        done = True

if success:
    # Read out the actions that got us here.
    # First we make a list by finding them in backwards order.
    actions = []
    node = child
    while node != root:
        actions.append(node.source_action)
        node = node.parent

    # Now we turn it around.
    actions.reverse()

    # And output it.
    print('Success.')
    nm = 0
    for action in actions:
        nm += 1
        print(f'{nm}: {action}')
else:
    print('Failure.')