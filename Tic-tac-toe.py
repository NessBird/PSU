# Tic-tac-toe RL, deterministic version.

import random
from tkinter import *
from tkinter import font as tkfont


# Utilities.
def replace_char(s, pos, c):
    # String utility. Replace the character at position pos with character c.
    string_list = list(s)
    string_list[pos] = c
    s = "".join(string_list)
    return s

def other_ox(ox):
    # Utility. Return the other player's token.
    if not ox or ox == '-':
        raise 'other_ox: bad ox'

    if ox == 'O':
        return 'X'
    else:
        return 'O'

def check_goal_state(s, ox):
    # Check if this string constitutes a goal state for the given ox.
    for i in range(3):
        # Horizontal:
        found = True
        for j in range(3):
            if s[i * 3 + j] != ox:
                found = False
        if found:
            return True

        # Vertical:
        found = True
        for j in range(3):
            if s[j * 3 + i] != ox:
                found = False
        if found:
            return True

    # Diagonal up:
    if s[0] == s[4] == s[8] == ox:
        return True

    # Diagonal down:
    if s[2] == s[4] == s[6] == ox:
        return True

    return False

class State:
    def __new__(cls, s, parent, ox):
        # Check if this state already exists. If it does, use it instead of generating a new one.
        if s in states:
            # Return this existing state. Make sure it knows where we came from so we can correctly
            # follow the sequence of moves for this trial.
            states[s].parent = parent
            return states[s]
        else:
            # Default behavior: run __init__()
            instance = super().__new__(cls)
            return instance

    def __init__(self, s, parent, ox):
        if s:
            self.s = s
            # Make sure it gets included in the states listing.
            if s in states:
                # This state already existed.
                return
            else:
                states[s] = self
        else:
            # We use - for blank instead of a space, it's a lot easier to tell how many there are in the string.
            self.s = starting_board
        self.parent = parent
        self.ox = ox
        # No information is better than a tie.
        self.children = []
        self.is_goal_state = self.goal_state()
        self.resign = False
        if self.is_goal_state:
            self.value = 1
            self.is_tie = False
        else:
            # We don't know if this is a winning or losing branch. But we
            # start with a high value -- actually greater than a winning value.
            self.value = 2
            # Is it a tie?
            self.is_tie = '-' not in self.s
            if self.is_tie:
                self.value = 0.5
        self.expanded = False

    def expand(self):
        # Expand this node, creating its children but not its grandchildren.
        if self.expanded:
            return
        ox = other_ox(self.ox)
        for i in range(9):
            if self.s[i] == '-':
                # Build the string for this child.
                c_string = replace_char(self.s, i, ox)
                self.children.append(State(c_string, self, ox))
        self.expanded = True

    def best_child(self):
        # Return the best child of the given state.
        # Make sure its kids are populated.
        self.expand()
        child = None
        max_value = 0
        for i in range(len(self.children)):
            if self.children[i].value > max_value:
                # There are going to be lots of ties here, since we're only using a few values:
                # 0, 0.5, 1, 2. Just take the first one, I don't care about randomizing.
                max_value = self.children[i].value
                child = self.children[i]
        return child

    def generate_move(self, pos):
        # Select a move and return its state. "self" is actually the state of the opponent's last move.
        # If pos is supplied, the move was selected by user; have it override the automatic move generation.
        self.expand()

        # Select the best available move from this point. Since "unknown" gets the highest score, we'll
        # prioritize finding out all the possible configurations and scoring them.
        best = 0
        child = None
        for i in range(len(self.children)):
            if self.children[i].value > best:
                best = self.children[i].value
                child = self.children[i]

        # Process this selected move.
        if child is None:
            # The opponent was in a winning configuration. We resign after that move.
            # (This gets recorded on the opponent's move since we've not making a move.)
            # Note that resigning is only relevant in training.
            self.value = 1
            self.resign = True
            return None
        elif child.is_goal_state:
            child.value = 1
            # The opponent's move caused them to lose.
            self.value = 0
            return child
        elif child.is_tie:
            child.value = 0.5
            # The opponent's move led to this tie.
            self.value = 0.5
        elif child.value == 0.5 or child.value == 1:
            # This child's value has already been determined. Propagate it backwards toward the beginning of the game.
            self.value = 1 - child.value
        return child

    def draw_board(self):
        w.delete('all')
        padding = (square - ox_size) / 2
        for i in range(9):
            x = edge + i % 3 * (square + gap)
            y = edge + i // 3 * (square + gap)
            w.create_rectangle(x, y, x + square, y + square)

            match self.s[i]:
                case '-':
                    pass
                case 'X':
                    w.create_line(x + padding, y + padding, x + padding + ox_size, y + padding + ox_size, width = 10)
                    w.create_line(x + padding, y + padding + ox_size, x + padding + ox_size, y + padding, width = 10)
                case 'O':
                    w.create_oval(x + padding, y + padding, x + square - padding, y + square - padding, width = 10)
            w.pack()

        font = tkfont.Font(size=20)
        # The computer doesn't need to resign in play (it can't lose), and we don't want to make the
        # human resign, even when they've lost.
        resign = self.resign and mode == 'training'
        if self.is_goal_state:
            w.create_text(250, 400, text=self.ox + ' wins', font=font, fill='red')
        if self.is_tie:
            w.create_text(250, 400, text='Tie game', font=font, fill='gray')
        if resign:
            w.create_text(250, 400, text=other_ox(self.ox) + ' resigns', font=font, fill='red')

        if self.is_goal_state or self.is_tie or resign:
            w.create_text(250, 450, text='Game over, click to proceed', font=font)
        else:
            w.create_text(250, 450, text='Your move', fill='green', font=font)

        w.update()

    def goal_state(self):
        # Is the given board won and lost by the given player?
        return check_goal_state(self.s, self.ox)

def game_stop(event):
    # End.
    master.destroy()
    exit()

def game_pause(event):
    # Pause until mouse click. Terminate the main loop, we'll pick it up in a minute.
    master.quit()

def key_pressed(event):
    if event.keysym == 'Escape':
        # Allow user to stop playing.
        master.destroy()
        exit()

def get_mouse(event):
    handles['event'] = event
    master.quit()

def play():
    curr = handles['curr']
    ox = other_ox(curr.ox)
    if handles[ox] == 'player':
        # Let the user play this move. Play synchronously.
        w.bind("<Button-1>", get_mouse)
        w.mainloop()

        # The user has selected a move. Build its state.
        event = handles['event']
        x = min((event.x - edge) // (square + gap), 2)
        y = min((event.y - edge) // (square + gap), 2)
        p = y * 3 + x

        # We have the position of the user's move. Create a new state for it under the current state.
        pos = replace_char(curr.s, p, ox)
        p_state = states[pos]

        # Rebind.
        handles['curr'] = p_state
    else:
        # Generate a state for the computer's move (playing against itself or against a player).
        c_state = curr.generate_move(None)

        # Point the curr pointer at the new state.
        if c_state is not None:
            handles['curr'] = c_state
            if pause_after_game or mode == 'playing':
                # Draw the board without waiting. This only actually draws in debug mode while training.
                curr.draw_board()


# Visual proportions.
square = 100
edge = 25
gap = 10
ox_size = 80
canvas_w = canvas_h = 500

# Game settings.
# This causes the system to draw the board and wait for click between games while training.
pause_after_game = False
starting_board = '---------'

# We'll build a list of states with success / failure data.
states = {}

state = State(False, None, 'X')

states[state.s] = state
# Get children for this first state.
state.expand()

# Handy object handles.
handles = {'curr': state, 'first': state, 'X': 'program', 'O': 'program'}

# Start the UI. It won't show a window until we run draw_board.
master = Tk()
master.title("Tic-Tac-Toe")
w = Canvas(master, width=canvas_w, height=canvas_h)
w.pack(expand=YES, fill=BOTH)

game = 0
X_wins = 0
O_wins = 0
mode = 'training'
this_epoch_results = {'program': 0, 'random': 0, 'tie': 0}

# Train agent. Stop when we know who will win before we start.
while handles['first'].value == 2:
    # Play a move.
    play()

    # (If we're already pausing after moves, no need to do this separately.)
    if handles['curr'].is_goal_state or handles['curr'].is_tie or handles['curr'].resign:
        game += 1
        if handles['curr'].resign:
            if handles['curr'].ox == 'O':
                X_wins += 1
            else:
                O_wins += 1
        elif handles['curr'].is_goal_state:
            if handles['curr'].ox == 'O':
                O_wins += 1
            else:
                X_wins += 1
        print(game, handles['curr'].s, ' games played, X:', X_wins, ' O: ', O_wins)

        if pause_after_game:
            # Draw the board and wait for user click.
            handles['curr'].draw_board()
            w.bind("<Button-1>", get_mouse)
            w.mainloop()
            handles['curr'] = handles['first']
            # Start a new game.
            handles['curr'].draw_board()

        # Start again.
        handles['curr'] = handles['first']


# OK, training's complete, play against a human.
mode = 'playing'
# Player is always O, computer is X.
handles['O'] = 'player'
handles['X'] = 'program'
while True:
    # Play games with a human now.
    handles['curr'] = handles['first']
    handles['curr'].draw_board()

    # Switch players after each game.
    temp = handles['X']
    handles['X'] = handles['O']
    handles['O'] = temp

    # Play one game.
    while not (handles['curr'].is_goal_state or handles['curr'].is_tie):
        # Play a move.
        play()
        handles['curr'].draw_board()

    # Start a new game.
    handles['curr'].draw_board()
    handles['curr'] = handles['first']
    w.bind("<Button-1>", get_mouse)
    w.mainloop()
