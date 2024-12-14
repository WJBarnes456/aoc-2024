import re
import math

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
    
    # the problem definition is not very precise, but I think this "christmas tree" shape is when one particular row is fully occupied by robots
    # the downside is that I'm not sure which row it's going to be 
    # i.e. this is going to be the lowest time when that row is fully occupied
    # the very first AoC in 2015 was also in the shape of a Christmas tree https://adventofcode.com/2015/
    # the input has 500 robots in it, filling a 103 x 101 space with the shape of that Christmas tree..
    # the example has 12 robots in a 7 x 11 space, which is just about enough to form a Christmas tree
    # my thought is that it could look something like
    #    x
    #   xox
    #  xooox
    # xxxxxxx
    #   | |
    # i.e. width of a layer is 2*(steps from top) - 1
    # this implies that for a 103 wide space, the tree is 52 layers tall
    # and the number of robots required is 1 + (50 * 2) + 103 = 204 robots
    # this can't be the case for this design, there are far too many robots
    # perhaps it's instead stepped at twice that height..? but in any case I'm expecting there to be some number of lined up robots
    # I implemented a dumb solution just to see what it'd look like and unexpectedly just found the solution, I'm glad I didn't make too many assumptions as the clever way would've not worked at all.
    def print_positions_at_time(self, seconds):
        robot_positions = sorted(r.position_after(seconds, self.size) for r in self.robots)

        print(f"Positions at second {seconds}")
        
        robot_positions.reverse() 
        next_robot = robot_positions.pop()
        for x in range(0, self.size[0]):
            line = ""
            for y in range(0, self.size[1]):
                count = 0
                while next_robot == (x,y):
                    count += 1
                    try:
                        next_robot = robot_positions.pop()
                    except IndexError:
                        next_robot = None
                
                if count == 0:
                    line += '.'
                else:
                    line += str(count)
            print(line)
    
    def deduce_christmas_tree_time(self):
        for seconds in range(100000):
            robot_positions = [r.position_after(seconds, self.size) for r in self.robots]

            # we are specifically looking for a horizontal line as part of the christmas tree, so order by y first, then look for consecutive x
            inverted_positions = sorted((r[1], r[0]) for r in robot_positions)

            prev_pos = (math.inf, math.inf)
            consecutive = 0
            for pos in inverted_positions:
                if pos[0] == prev_pos[0] and pos[1] == prev_pos[1] + 1:
                    consecutive += 1
                else:
                    consecutive = 0
                
                if consecutive > 10:
                    print("Found 10 consecutive, printing image")
                    self.print_positions_at_time(seconds)
                    return seconds
                
                prev_pos = pos
        
        return None


robot_re = re.compile('p=(\d+),(\d+) v=(-?\d+),(-?\d+)')

def accept_input():
    robots = []
    while True:
        try:
            line = input()
        except EOFError:
            return Puzzle(robots, (101, 103))

        match = robot_re.match(line)

        if not match:
            raise Exception(f"invalid robot: {line}")
        
        position = (int(match.group(1)), int(match.group(2)))
        velocity = (int(match.group(3)), int(match.group(4)))
        robots.append((position, velocity))

def part1(puzzle):
    return puzzle.safety_factor_after_time(100)

def part2(puzzle):
    return puzzle.deduce_christmas_tree_time()


def main():
    puzzle = accept_input()
    print(f"Part 1: {part1(puzzle)}")
    print(f"Part 2: {part2(puzzle)}")

main()