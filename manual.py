# Utilities

from unittest import case

import numpy as np
from graphics import *
from numpy._core.defchararray import lower
from copy import deepcopy

global size, win, gap, texts

def get_blank_pos(board):
    # Find the blank.
    for y in range(len(board)):
        for x in range(len(board[y])):
            if board[y][x] == ' ':
                return {'x': x, 'y': y}

def move(board, act):
    # Generate a board with the tiles shifted in the requested direction.
    if not board:
        return

    b_pos = get_blank_pos(board)

    # Make a deep copy of the board array to return.
    a = deepcopy(board)
    try:
        match act:
            case 'up':
                if b_pos['y'] == 2:
                    raise Exception('Up not possible.')

                # copy the tile being moved into the blank spot.
                a[b_pos['y']][b_pos['x']] = a[b_pos['y'] + 1][b_pos['x']]
                # Put the blank in its place.
                a[b_pos['y'] + 1][b_pos['x']] = ' '
                return a

            case 'down':
                if b_pos['y'] == 0:
                    raise Exception('Down not possible.')

                # copy the tile being moved into the blank spot.
                a[b_pos['y']][b_pos['x']] = a[b_pos['y'] - 1][b_pos['x']]
                # Put the blank in its place.
                a[b_pos['y'] - 1][b_pos['x']] = ' '
                return a

            case 'left':
                if b_pos['x'] == 2:
                    raise Exception('Left not possible.')

                # copy the tile being moved into the blank spot.
                a[b_pos['y']][b_pos['x']] = a[b_pos['y']][b_pos['x'] + 1]
                # Put the blank in its place.
                a[b_pos['y']][b_pos['x'] + 1] = ' '
                return a

            case 'right':
                if b_pos['x'] == 0:
                    raise Exception('Right not possible.')

                # copy the tile being moved into the blank spot.
                a[b_pos['y']][b_pos['x']] = a[b_pos['y']][b_pos['x'] - 1]
                # Put the blank in its place.
                a[b_pos['y']][b_pos['x'] - 1] = ' '
                return a

            case _:
                # bad key.
                return a
    except Exception as e:
        return a

def draw_board(board):
    # Draw the given board.
    if not board:
        return

    for y in range(len(board)):
        for x in range(len(board[y])):
            txt = texts[y * 3 + x]
            txt.undraw()
            txt.setText(board[y][x])
            txt.draw(win)
            del txt

def manual_play(start):
    global gap, size, texts, win
    gap = 10
    size = 100
    texts = []
    win = GraphWin("Manual play", 500, 500)

    # Globals for manual play
    # Draw the board outline.
    root_board = [[], [], []]
    root_board[0] = [start[0], start[1], start[2]]
    root_board[1] = [start[3], start[4], start[5]]
    root_board[2] = [start[6], start[7], start[8]]

    # Let user play.
    r = Rectangle(Point(0, 0), Point(size * 3 + gap * 3, size * 3 + gap * 3))
    for y in range(len(root_board)):
        for x in range(len(root_board[y])):
            # Rectangles just get drawn once and sit there.
            pos_x = gap + x * gap + x * size
            pos_y = gap + y * gap + y * size
            r = Rectangle(Point(pos_x, pos_y), Point(pos_x + size, pos_y + size))
            r.draw(win)

            txt = Text(Point(pos_x + size * 0.5, pos_y + size * 0.5), root_board[y][x])
            txt.setSize(36)
            txt.draw(win)
            texts.append(txt)
            del txt
    del pos_y, pos_x, y, x

    key = ''
    mt = deepcopy(root_board)
    while key != 'escape':
        tkey = lower(win.checkKey())
        if tkey and tkey != key and tkey != 'escape':
            mt = move(mt, tkey)
        key = tkey
        draw_board(mt)
    win.close()
    return


