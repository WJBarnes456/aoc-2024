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
        self.output = []
    
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
                self.output.append(self.combo(operand) % 8)
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

    try:
        for _ in range(100000):
            computer.step()
            print(computer)
        # I suspect we might end up trying to solve the halting problem in Part 2, which we can actually do 
        raise Exception("Program did not terminate in 100k steps, you sure that's right?")
    except EndOfProgramError:
        # reset the state
        computer.a, computer.b, computer.c = original_values
        computer.instruction_pointer = 0
        output = computer.output
        computer.output = []
        return ','.join(str(v) for v in output)

def part2(computer):
    # we have a couple of options to solve this...
    
    # 1) brute force. we don't need to run the whole program every time, it's just until we get some output inconsistent with the output register
    # we might need to solve the halting problem here by checking if we ever end up in a loop

    for a in range(100000):
        new_computer = Computer(computer.a, computer.b, computer.c, computer.program)


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


main()