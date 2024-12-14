import re

# Python's built-in mod can return negative values (e.g. -1 mod 2 is -1), which we don't want. so define our own instead
def mod(a, b):
    return (a+b) % b

class Robot:
    def __init__(self, position, velocity) -> None:
        self.position = position
        self.velocity = velocity
        pass

    def position_after(self, seconds, map_size):
        p = self.position
        v = self.velocity
        return mod(p[0] + seconds * v[0], map_size[0]), mod(p[1] + seconds * v[1], map_size[1])


class Puzzle:
    def __init__(self, robots, size) -> None:
        self.robots = [Robot(r[0], r[1]) for r in robots]
        self.size = size
    
    def safety_factor_after_time(self, seconds):
        # work out where the robots will be, and put them in the right quadrant
        # we can do this in a fairly neat way by having an array of length 4 and indexing into it based on quadrant values...
        quadrants = [0, 0, 0, 0]
        halfway = ((self.size[0] - 1) // 2, (self.size[1] - 1) // 2)
        for r in self.robots:
            final_pos = r.position_after(seconds, self.size)

            # "Robots that are exactly in the middle (horizontally or vertically) don't count as being in any quadrant"
            if final_pos[0] == halfway[0] or final_pos[1] == halfway[1]:
                continue

            # index into them by summing indicator functions
            # i.e. the quadrants are upper left, upper right, lower left, lower right in that order
            index = (final_pos[0] > halfway[0]) + 2 * (final_pos[1] > halfway[1])
            quadrants[index] += 1
        
        score = 1
        for q in quadrants:
            score *= q
        return score

robot_re = re.compile('p=(\d+),(\d+) v=(-?\d+),(-?\d+)')

def accept_input():
    robots = []
    while True:
        try:
            line = input()
        except EOFError:
            return Puzzle(robots, (101,103))

        match = robot_re.match(line)

        if not match:
            raise Exception(f"invalid robot: {line}")
        
        position = (int(match.group(1)), int(match.group(2)))
        velocity = (int(match.group(3)), int(match.group(4)))
        robots.append((position, velocity))

def part1(puzzle):
    return puzzle.safety_factor_after_time(100)

def main():
    puzzle = accept_input()
    print(f"Part 1: {part1(puzzle)}")

main()