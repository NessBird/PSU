# Tic-tac-toe RL, deterministic version.

import random
from tkinter import *
from tkinter import font as tkfont
import numpy as np

def game_pause(event):
    # Pause until mouse click. Terminate the main loop, we'll pick it up in a minute.
    master.quit()

def key_pressed(event):
    if event.keysym == 'Escape':
        # Allow user to stop playing.
        master.destroy()
        exit()

def get_mouse(event):
    master.quit()

def progress(grid):
    # Iterate. Play every possible move and record all the resulting state values.

    # First, make a copy of all the current values.
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            #grid[i][j]['temp_value'] = grid[i][j]['value']
            grid[i][j]['temp_value'] = 0
            grid[i][j]['temp_n'] = 0

    # Find a position.
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if grid[i][j]['terminal']:
                continue

            # Select a direction.
            for d in dirs:
                # Play out this move.
                p = grid[i][j]
                # Find the new position selected by this move.
                # Does it take us outside the grid?
                if i + d[0] < 0 or i + d[0] >= len(grid) or j + d[1] < 0 or j + d[1] >= len(grid[0]):
                    # Yes. So we don't move, just take the hit.
                    new_p = p
                else:
                    new_p = grid[i + d[0]][j + d[1]]

                # Use the value found in the new position to "back up" and (later) adjust the
                # value of the current position.
                p['temp_value'] += new_p['value'] + reward
                # Increment the counter.
                p['temp_n'] += 1

    # Finalize the progress, calculating new values and storing them back in the value properties.
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pos = grid[i][j]
            if pos['temp_n']:
                # Calculate the average adjustment for this run.
                avg = pos['temp_value'] / pos['temp_n']
                # Now build it into the value.
                pos['value'] = avg

def draw_board(grid):
    w.delete('all')
    font = tkfont.Font(size=font_size)
    for i in range(grid_size):
        for j in range(grid_size):
            if grid[i][j]['terminal']:
                fill = 'gray'
            else:
                fill = 'white'
            x = edge + j * (square + gap)
            y = edge + i * (square + gap)
            w.create_rectangle(x, y, x + square, y + square, fill=fill)
            if not grid[i][j]['terminal']:
                w.create_text(x + square / 2, y + square / 2, font=font, text=str(round(grid[i][j]['value'], 2)))
            w.update()

    font = tkfont.Font(size=font_size)
    w.create_text(250, 450, text='Iteration: ' + str(iteration), fill='green', font=font)

    w.update()


# Visual proportions.
grid_size = 4
square = 100
edge = 25
gap = 10
canvas_w = canvas_h = 500
font_size = 20
reward = -1

# Directions, in x-y.
dirs = np.zeros((8, 2), dtype=int)
dirs[0] = [0, 1]
dirs[1] = [1, 0]
dirs[2] = [0, -1]
dirs[3] = [-1, 0]
dirs[4] = [-1, -1]
dirs[5] = [1, -1]
dirs[6] = [1, 1]
dirs[7] = [-1, 1]

# Start the UI. It won't show a window until we run draw_board.
master = Tk()
master.title("Homework 4")
grid = [[0 for x in range(grid_size)] for y in range(grid_size)]

w = Canvas(master, width=canvas_w, height=canvas_h)
w.pack(expand=YES, fill=BOTH)

# Set up a grid of 16 states. Each maintains a current value plus a counter so we can keep recalculating.
# There's also the "old" value and count, which are needed because while we're recalculating we don't
# want current calculations to be affected by current changes.
for i in range(grid_size):
    for j in range(grid_size):
        grid[i][j] = {
            'value': 0,
            'terminal': (i == 0 and j == 0) or (i == grid_size-1 and j == grid_size-1),
            'temp_value': 0,
            'temp_n': 0
        }

iteration = 1
for i in range(100):
    # Show the board.
    draw_board(grid)
    w.bind("<Button-1>", get_mouse)
    w.mainloop()

    # Now run one iteration.
    progress(grid)
    iteration += 1

