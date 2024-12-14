# this is a linear optimisation problem
# find integers (a,b) such that a * a_x + b * b_x = prize_x; a * a_y + b * b_y = prize_y; minimising 3a + b
# I'm certain there's a nice algorithm that solves this directly but I don't think I've had to implement it before. it just reminds me of doing lagrangian multipliers at university.
# I'll read about this once I've got the general skeleton set up

# rather than considering all solutions, you simply want to find some number of presses of a and b such that 
# then all you need to do is find a single solution, then optimise 3a + b by going as close to that crossover point as we can

import re
import math

class Machine:
    def __init__(self, a, b, target):
        self.a = a
        self.b = b
        self.target = target
     
    # as I said, I'm sure there's a nice algorithm for this, but let's solve it the basic way to start off with...
    def minimum_tokens(self):
        limit = 100

        target = self.target
        a = self.a
        b = self.b
         
        # search the space for solutions
        # the number of button presses are heavily constrained so we don't need to search the whole space, we can just iterate over possible numbers of presses for one of a or b, and figure the other out
        # I'm picking to iterate over b presses basically arbitrarily 
        best_solution = (math.inf, math.inf, math.inf)

        # starting from the maximum press number, or the number of presses required for just b to saturate one of the values (min is correct as otherwise we'd overshoot)...
        max_b_presses = min(target[0] // b[0], target[1] // b[1])
        for b_presses in range(0, max_b_presses + 1):
            remaining_x = target[0] - b_presses * b[0]
            if remaining_x % a[0] != 0:
                # doesn't evenly divide the remainder - bin it.
                continue

            a_presses = remaining_x // a[0]
            remaining_y = target[1] - b_presses * b[1]
            if remaining_y != a[1] * a_presses:
                # not a real solution, bin it.
                continue

            # assert this is a real solution (bit paranoid but worth checking)
            if target[0] != (a[0] * a_presses + b[0] * b_presses) or target[1] != (a[1] * a_presses + b[1] * b_presses):
                raise Exception(f"Thought {(a_presses, b_presses)} was a solution to {self}")

            # we found a real solution
            score = 3 * a_presses + b_presses
            if score < best_solution[2]:
                best_solution = (a_presses, b_presses, score)

        best_score = best_solution[2]
        if best_score == math.inf:
            print(f"Machine {self} thinks it's inf") 
            return 0

        return best_score
    
    def __str__(self):
        return f"Button A: X+{self.a[0]}, Y+{self.a[1]}\nButton B: X+{self.b[0]}, Y+{self.b[1]}\nPrize: X={self.target[0]}, Y={self.target[1]}"

class Puzzle:
    def __init__(self, machines):
        self.machines = machines
    
    def minimum_tokens(self):
        return sum(machine.minimum_tokens() for machine in self.machines)

button_re = re.compile(r'Button (\w): X\+(\d+), Y\+(\d+)')
prize_re = re.compile(r'Prize: X=(\d+), Y=(\d+)')

def accept_input():
    machines = []
    current_machine = {}
    while True:
        try: 
            line = input()
            button_match = button_re.match(line)
            
            if button_match:
                current_machine[button_match.group(1)] = (int(button_match.group(2)), int(button_match.group(3)))
            
            prize_match = prize_re.match(line)
            if prize_match:
                target = (int(prize_match.group(1)), int(prize_match.group(2)))
                if 'A' in current_machine and 'B' in current_machine:
                    machines.append(Machine(current_machine['A'], current_machine['B'], target))
                    current_machine = {}
                else:
                    raise Exception(f"got prize {target} without buttons")
        except EOFError:
            return Puzzle(machines)

def part1(puzzle):
    return puzzle.minimum_tokens()

def part2(puzzle):
    # all the limits are actually 10000000000000 higher than thought... easiest to build a new puzzle and solve that
    offset = 10000000000000
    new_machines = []
    for machine in puzzle.machines:
        new_target = (machine.target[0] + offset, machine.target[1] + offset)
        new_machines.append(Machine(machine.a, machine.b, new_target))
    
    new_puzzle = Puzzle(new_machines)
    print([str(m) for m in new_puzzle.machines])
    return Puzzle(new_machines).minimum_tokens()

def main():
    puzzle = accept_input()
    print(f"Part 1: {part1(puzzle)}")
    print(f"Part 2: {part2(puzzle)}")

main()