# A genetic algorithm to create 8 queens solutions.
from math import comb
import random
import copy
import matplotlib
from graphics import *

def display_solution(s):
    gap = 50
    square_size = 50
    win = GraphWin("Solution", square_size * queens + gap + gap, square_size * queens + gap + gap)
    for i in range(queens + 1):
        r = Line(Point(gap, i * square_size + gap), Point(gap + queens * square_size, i * square_size + gap))
        r.draw(win)
        r = Line(Point(i * square_size + gap, gap), Point(i * square_size + gap, gap + queens * square_size))
        r.draw(win)
        if i < queens:
            c = Circle(Point((s[i] + 0.5) * square_size + gap, gap + (i + 0.5) * square_size), gap / 3)
            c.setFill("green")
            c.draw(win)

    win.getKey()

def conflict(s, i, j):
    # Check if string s has a conflict between position i and position j.
    # There are 3 ways two queens can conflict (they can't conflict on column because our syntax prevents it).
    # 1. They can be on the same row.
    if s[i] == s[j]:
        return True

    # 2. Diagonally, going down, or diagonally, going up. It's easy to check with absolute value.
    elif abs(s[i] - s[j]) == abs(i - j):
        return True
    return False

def improve(s):
    # Make a small improvement to string s if possible.
    for i in range(1, len(s)):
        for j in range(i):
            if conflict(s, i, j):
                # There's a conflict here between i and j. Check all possible values of s[i] to find another value
                # of i that doesn't conflict. Note that as soon we get into this condition, we're not continuing
                # the outer loops. We've chosen i as the column to try to improve.
                t = copy.copy(s)
                # Check each possible value of i.
                for k in range(len(s)):
                    better = True
                    t[i] = k
                    # Check all other columns for a conflict.
                    for m in range(len(s)):
                        if m != i and conflict(t, i, m):
                            better = False
                            break
                    if better:
                        # We've found a better value for s[i]
                        break
                if better:
                    # Success.
                    t[i] = k
                    return t
                else:
                    # Never mind. There are no better options.
                    return s

    # s is a solution.
    return s


def fitness(s):
    # Calculate the fitness of s as the number of non-attacking queen pairs.
    conflicts = 0
    tc = []
    for i in range(len(s)):
        for j in range(i):
            # There are 3 ways two queens can conflict (they can't conflict on column because our syntax prevents it).
            # 1. They can be on the same row.
            if conflict(s, i, j):
                conflicts += 1
                tc.append([i, j])

    # Try reducing the total score by a flat amount to make the more fit individuals pop up.
    return max(max_conflicts - conflicts, 0)


def select_string(strings, total_fitness):
    # Select a string from the strings list. The likelihood of each string being selected is in proportion to
    # its fitness.
    pos = random.randint(1, int(total_fitness))
    for i in range(len(strings)):
        if strings[i]['start'] + strings[i]['fit'] >= pos:
            return strings[i]
    raise 'Error: select_string failed'


def offspring(old_pair):
    # Combine the two parts of the pair and return the offspring.
    # We'll divide the strings at the crossover point.
    crossover = random.randint(1, queens - 1)
    new_pair = copy.deepcopy(old_pair)
    new_pair[0]['s'] = old_pair[0]['s'][:crossover] + old_pair[1]['s'][crossover:]
    new_pair[1]['s'] = old_pair[1]['s'][:crossover] + old_pair[0]['s'][crossover:]
    return new_pair

def one_trial():
    # Create random strings to start with.
    strings = []
    for i in range(population):
        strings.append({'s': [], 'fit': 0, 'start': 0})
        for j in range(queens):
            c = random.randint(0, queens - 1)
            strings[i]['s'].append(c)    # Run some generations and see if they can solve the problem.

    for generation in range(generations):
        # Calculate the fitness of each string.
        total_fitness = 0
        most_fit = 0
        for i in range(population):
            strings[i]['fit'] = fitness(strings[i]['s'])
            total_fitness += strings[i]['fit']
            if strings[i]['fit'] > most_fit:
                most_fit = strings[i]['fit']
                if most_fit >= max_conflicts:
                    display_solution(strings[i]['s'])
                    return {'generations': generation, 'success': True, 'solution': strings[i]['s']}
        #print('Average: ' + str(total_fitness / population), 'Most fit: ' + str(most_fit), 'Generation: ', generation)

        # Generate string_count pairs of strings. The likelihood of each string appearing in any given pair is in
        # proportion to its fitness.
        selected = 0
        # Fill in the starting positions in the string table.
        start = 0
        for i in range(population):
            # Set the start position of this string in the table.
            strings[i]['start'] = start
            # Move the start position forward for the next string.
            start = start + strings[i]['fit']

        # Generate the pairs.
        successors = []
        for i in range(int(population / 2)):
            pair = [select_string(strings, total_fitness), select_string(strings, total_fitness)]
            successors = successors + offspring(pair)
        strings = successors

        # Now make each string a little more fit if possible.
        if use_improve:
            for i in range(population):
                strings[i]['s'] = improve(strings[i]['s'])

        # Check the strings for random mutation.
        for i in range(population):
            r = random.random()
            if r < mutation_rate:
                for j in range(mutants):
                    pos = random.randint(0, len(strings[i]) - 1)
                    strings[i]['s'][pos] = random.randint(0, queens - 1)

    # Failed to solve the problem in the requisite number of generations.
    return {'generations': generations, 'success': False, 'solution': False}


# A string will be a list of queens, integers indicating the vertical position of a queen in a given column.
population = 2000
queens = 10
mutation_rate = 0.03
mutants = 1
generations = 200
use_improve = False
trials = 500

# Calculate the number of possible conflicts between queens as n choose 2.
# But we don't have to use that number. We can use a smaller one. The logic below will make the program use
# this smaller number to calculate the fitness of individuals, and this will make it favor more fit individuals more.
default_max = comb(queens, 2)
print('Max possible conflicts: ', default_max)
max_conflicts = int(default_max / 2)
print('Using max conflicts: ', max_conflicts)
results = []

failures = 0
total_generations = 0
for i in range(trials):
    t = (one_trial())
    results.append(t)
    if t['success']:
        print(i, 'Solution: ', t['solution'], ' Generation: ', t['generations'])
        total_generations += t['generations']
    else:
        print(i, 'Failed. ', 'Generation: ', t['generations'])
        failures += 1
    # display_solution(t['solution'])
print('Successes: ', trials - failures, '/', trials, 'Average generations to complete when successful: ',
      total_generations / (trials - failures))

# Population: 100
# max_conflicts 28: Successes:  144 / 1000 Average generations to complete when successful:  48.4
# max_conflicts 14: Successes:  305 / 1000 Average generations to complete when successful:  29.2
