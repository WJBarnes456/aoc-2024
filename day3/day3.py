# this should be my final day doing it in Python given I have a free evening tonight

import re

# these regexes mean that both parts can be solved with just plain old findall
# the basic mul regex just grabs instances of the mul instruction (part1)
# the do/don't regex just grabs the do/don't as a capture group, which we can use to iterate through
# then we compose both of those together as a non-capturing alternation
mul_re_str = r'mul\((\d{1,3}),(\d{1,3})\)'
mul_re = re.compile(mul_re_str)
mul_do_dont_re = re.compile(r"(?:(do(?:n\'t)?\(\))|" + mul_re_str + ')')

def accept_input():
    blob = ""
    while True:
        try:
            blob += input()
        except EOFError:
            return blob

def part1(memory):
    matches = mul_re.findall(memory)
    total = 0
    for match in matches:
        total += int(match[0]) * int(match[1])
    return total

def part2(memory):
    matches = mul_do_dont_re.findall(memory)
    total = 0
    enabled = True
    for match in matches:
        print(match)
        if match[0] == "don't()":
            enabled = False
        elif match[0] == "do()":
            enabled = True
        elif enabled:
            total += int(match[1]) * int(match[2])
    return total
        
    
def main():
    memory = accept_input()
    part1_result = part1(memory)
    print(f"Part 1: {part1_result}")
    
    part2_result = part2(memory)
    print(f"Part 2: {part2_result}")
    
main()