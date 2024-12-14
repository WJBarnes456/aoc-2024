# find integers (a,b) such that a * a_x + b * b_x = prize_x; a * a_y + b * b_y = prize_y; minimising 3a + b
# we can substitute one of these variables out - let's make it all in terms of a
# b = (prize_x - a * a_x) / b_x (which is an integer)
# substitute into (2) 
# a * a_y + b_y * (prize_x - a * a_x) / b_x = prize_y
# a * a_y * b_x + b_y * (prize_x - a * a_x) = prize_y * b_x
# a * a_y * b_x - a * a_x * b_y = prize_y * b_x - prize_x * b_y
# a (a_y * b_x - a_x * b_y) = prize_y * b_x - prize_x * b_y
# a = (prize_y * b_x - prize_x * b_y) / (a_y * b_x - a_x * b_y)
# ...huh!? and this gives exactly the sample solutions... it's constrained enough that you don't need to do any searching at all! I was misled!

import re
import math

class Machine:
    def __init__(self, a, b, target):
        self.a = a
        self.b = b
        self.target = target
     
    # we can solve this completely analytically...
    def minimum_tokens(self):
        (a, b, target) = (self.a, self.b, self.target)
        numerator = (target[1] * b[0] - target[0] * b[1])
        denominator = (a[1] * b[0] - a[0] * b[1])

        if numerator % denominator != 0:
            # no integer solution - i.e. not solvable
            return 0

        # assert this is now an integer number of a presses
        a_presses = numerator // denominator

        # now just turn this into a score
        b_numerator = (target[0] - a_presses * a[0])

        if b_numerator % b[0] != 0:
            print(f"Thought {a_presses} is a solution but {b_numerator / b[0]} is non-integer")

        b_presses = (target[0] - a_presses * a[0]) // b[0]
        
        return a_presses * 3 + b_presses 
    
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
    return Puzzle(new_machines).minimum_tokens()

def main():
    puzzle = accept_input()
    print(f"Part 1: {part1(puzzle)}")
    print(f"Part 2: {part2(puzzle)}")

main()