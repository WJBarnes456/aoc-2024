# today's seems pretty easy - it's a basic dynamic programming problem that you can solve by memoising

class Puzzle:
    def __init__(self, towels, patterns):
        self.towels = towels
        self.patterns = patterns

        # initialise the memo with the base case - the empty pattern is solvable exactly one way
        self.memo = {'': 1}
    
    def ways_solvable(self, pattern):
        # if it's already had the number determined, return that
        if pattern in self.memo:
            return self.memo[pattern]
        
        ways_solvable = 0
        for towel in self.towels:
            # we're probably churning strings loads here when we could be using slices, but oh well
            if towel == pattern[:len(towel)]:
                ways_solvable += self.ways_solvable(pattern[len(towel):])

        self.memo[pattern] = ways_solvable
        return ways_solvable
        
    def solvable_patterns(self):
        solvable = []
        for pattern in self.patterns:
            if self.ways_solvable(pattern) != 0:
                solvable.append(pattern)

        return solvable
    
    def all_ways(self):
        total = 0
        for pattern in self.patterns:
            total += self.ways_solvable(pattern)
        
        return total

def accept_input():
    line = input()
    towels = line.split(', ')

    separator = input()
    if separator != '':
        raise Exception(f"Expected blank line after towel patterns, got {separator}")
    
    patterns = []
    try:
        while True:
            patterns.append(input())
    except EOFError:
        return Puzzle(towels, patterns)

def part1(puzzle):
    return len(puzzle.solvable_patterns())

def part2(puzzle):
    return puzzle.all_ways()

def main():
    puzzle = accept_input()
    print(f"Part 1: {part1(puzzle)}")
    print(f"Part 2: {part2(puzzle)}")

main()