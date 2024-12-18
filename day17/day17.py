import re
from enum import IntEnum

class Opcode(IntEnum):
    ADV = 0
    BXL = 1
    BST = 2
    JNZ = 3
    BXC = 4
    OUT = 5
    BDV = 6
    CDV = 7

class EndOfProgramError(Exception):
    pass


class Computer:
    def __init__(self, a, b, c, program):
        # careful! you can't pre-parse instructions and their operands because jnz with an odd operand allows you to change "worlds" and switch which values are the instructions and which are the operands
        self.instruction_pointer = 0
        self.a = a
        self.b = b
        self.c = c
        self.program = program

    def combo(self, value):
        match value:
            case 0 | 1 | 2 | 3:
                return value
            case 4:
                return self.a
            case 5:
                return self.b
            case 6:
                return self.c
            case _:
                raise Exception(f"Invalid combo operand {value}")
    
    def __str__(self):
        return f"PC: {self.instruction_pointer}, A: {self.a}, B: {self.b}, C: {self.c}, Program: {self.program}"
    
    def step(self):
        # "If the computer tries to read an opcode past the end of the program, it instead halts."
        if self.instruction_pointer >= len(self.program):
            raise EndOfProgramError(f"Halted, instruction pointer is {self.instruction_pointer}")
        
        # instruction pointer is valid, so just implement the instructions
        pc = self.instruction_pointer
        opcode, operand = self.program[pc], self.program[pc+1]
        match opcode:
            case Opcode.ADV:
                # if a register can ever be a negative value, this might turn into a multiplication instead
                denominator = 2 ** self.combo(operand)
                self.a = self.a // denominator
            case Opcode.BXL:
                self.b = self.b ^ operand
            case Opcode.BST:
                self.b = self.combo(operand) % 8
            case Opcode.JNZ:
                if self.a != 0:
                    self.instruction_pointer = operand
                    # early return here stops program counter iterating
                    return
            case Opcode.BXC:
                self.b = self.b ^ self.c
            case Opcode.OUT:
                # step the instruction pointer manually, we're returning
                self.instruction_pointer += 2
                return self.combo(operand) % 8
            case Opcode.BDV:
                denominator = 2 ** self.combo(operand)
                self.b = self.a // denominator
            case Opcode.CDV:
                denominator = 2 ** self.combo(operand)
                self.c = self.a // denominator
            case _:
                raise Exception(f"Unknown instruction {opcode}")
        
        self.instruction_pointer += 2

register_re = re.compile(r'Register ([ABC]): (\d+)')

def parse_register_value(line, register):
    match = register_re.match(line)
    if not match:
        raise Exception(f"Invalid register line {line}")
    
    if register != match.group(1):
        raise Exception(f"Expected register {register}, got register {match.group(1)}")
    
    return int(match.group(2))

program_re = re.compile(r'Program: ([0-7,]+)')
def parse_program(line):
    match = program_re.match(line)
    if not match:
        raise Exception(f"Invalid program line {line}")
    
    return [int(v) for v in match.group(1).split(',')]

def part1(computer):
    # back up the values of a b c, we'll want to reset them after
    original_values = (computer.a, computer.b, computer.c)

    output = []
    try:
        for _ in range(100000):
            value = computer.step()
            if value is not None:
                output.append(value)

        # I suspect we might end up trying to solve the halting problem in Part 2, which we can actually do 
        raise Exception("Program did not terminate in 100k steps, you sure that's right?")
    except EndOfProgramError:
        # reset the state
        computer.a, computer.b, computer.c = original_values
        computer.instruction_pointer = 0
        return ','.join(str(v) for v in output)

# we have a couple of options to solve this...
# 1) brute force. we don't need to run the whole program every time, it's just until we get some output inconsistent with the output register
# we might need to solve the halting problem here by checking if we ever end up in a loop
def part2_bruteforce(computer):    
    for a in range(100000000):
        required_output = list(reversed(computer.program))
        try:
            new_computer = Computer(a, computer.b, computer.c, computer.program)
            states_reached = set()

            # again only simulate the machine for 100k steps
            for _ in range(1000000):
                output = new_computer.step()
                
                # if we got the correct output, we can pop it off the list
                if output is not None and output == required_output[-1]:
                    required_output.pop()
                elif output is not None:
                    raise EndOfProgramError(f"Bad machine state, needed output {required_output[-1]} but got {output}")
                
                state = (new_computer.instruction_pointer, new_computer.a, new_computer.b, new_computer.c)
                if state in states_reached:
                    raise EndOfProgramError("Program is looping, bail out")
                
                states_reached.add(state)

            state = (computer.instruction_pointer, a, computer.b, computer.c, tuple(required_output))
        except EndOfProgramError as err:
            if a % 1000 == 440:
                print(f"Discarding a={a}, {err}")
            if len(required_output) == 0:
                return a
    
    return None

# 2) not general, but reverse engineer my input...
# my input can be interpreted as:
# BST 4 (i.e. store A % 8 to B)
# ADV 1 (i.e. halve A)
# CDV 5 (i.e. divide A by 2^(A%8), store to C)
# BXL 5 (i.e. B = B ^ 5)
# BXC 1 (i.e. B = B ^ C)
# OUT 5 (i.e. output register B)
# ADV 3 (i.e. A = A/8)
# JNZ 0 (i.e. jump to start if A is not 0)
# i.e. each iteration outputs (A%8 ^ 5 ^ (A//2^(1+A%8)), A = A/16, ends when A=0
# so just go backwards - on the final iteration, A is some value less than 16 which outputs 0
def part2_clever(computer):
    # SIMPLIFYING ASSUMPTIONS:
    # - every input has just one jump, returning to the start, and it's the last instruction
    # - every iteration sets the value of B and C based just on the value of A, i.e. no value is persisted between loops besides A
    # - every iteration only mutates the value of A by a fixed amount

    # this is true for every example, and my input, and makes the rest of the analysis possible (I might be forgetting something from computation theory but I don't think this analysis is possible for general programs)
    # it's a shame as I implemented the logic to potentially have the jump shift us into a different universe as well...

    divisions_per_cycle = 0
    for potential_pc in range(0, len(computer.program), 2):
        opcode, operand = computer.program[potential_pc], computer.program[potential_pc+1]
        if opcode == Opcode.JNZ and (potential_pc != len(computer.program) -2 or operand != 0):
            raise Exception("This program has a non-looping jump at position {potential_pc}, cannot be analysed")
        elif opcode == Opcode.ADV and operand > 3:
            raise Exception("This program has a division of A by a non-literal, cannot be analysed")
        elif opcode == Opcode.ADV:
            divisions_per_cycle += operand
    
    # assert that the last two instructions are the end of the loop... so unroll it!

    # start condition: find A such that we output the required final value, and A=0 at the end to terminate
    target_as = [0]
    required_values = list(computer.program)
    one_iteration_program = computer.program[:-2]

    # iterate back from the final loop - find possible values of A which emit the required output, and leave us on a value of A which emits everything left
    while len(required_values) > 0:
        target_value = required_values.pop()
        target_as = part2_iteration(one_iteration_program, target_value, target_as, divisions_per_cycle)
        print(target_as)

    return target_as[0]

def part2_iteration(program, target_value, target_as, divisions_per_cycle):
    # since each iteration just twiddles bits from a somehow, we can shift across and stack it up
    # run the program forwards - search a from 0 to 15 (on my input) to find the value which, after running, gets us our target value
    all_values = 2 ** divisions_per_cycle
    valid_outputs = []
    for target_a in target_as:
        for a in range(all_values):
            this_a = target_a*all_values + a
            this_computer = Computer(this_a, 0, 0, program)

            emitted = None
            # if we stop short one instruction we should not halt
            # as there are no jumps this is no surprise
            for _ in range(len(program)//2):
                v = this_computer.step()
                if v is not None:
                    emitted = v
            
            if emitted == target_value and this_computer.a in target_as:
                valid_outputs.append(this_a)
    
    return valid_outputs

def accept_input():
    a = parse_register_value(input(), 'A')
    b = parse_register_value(input(), 'B')
    c = parse_register_value(input(), 'C')
    input()
    program = parse_program(input())
    return Computer(a, b, c, program)

def main():
    computer = accept_input()
    print(computer)
    print(f"Part 1: {part1(computer)}")
    print(f"Part 2: {part2_clever(computer)}")


main()