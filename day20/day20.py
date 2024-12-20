# this is once again a dynamic programming problem
# compute the fair distance from every location to the end, then the number of cheats you can sum up by clipping through the walls
# there's only one route in the input we're given, but I want to implement this to work for more general input

from enum import Enum
from collections import defaultdict

class Tile(Enum):
    FREE = 0
    WALL = 1
    START = 2
    END = 3

    @staticmethod
    def from_char(c):
        match c:
            # start is just a special free tile
            case '.':
                return Tile.FREE
            case '#':
                return Tile.WALL
            case 'S':
                return Tile.START
            case 'E':
                return Tile.END
            case _:
                raise Exception(f"Invalid tile {c}")

class Node:
    def __init__(self, tile_type, x, y):
        self.tile_type = tile_type
        self.neighbours = set()
        self.cheat_neighbours = set()

        self.x = x
        self.y = y
 
    def add_neighbour(self, other_node):
        self.cheat_neighbours.add(other_node)
        if self.tile_type != Tile.WALL and other_node.tile_type != Tile.WALL:
            self.neighbours.add(other_node)
    
    def __str__(self):
        return f"{self.tile_type} ({self.x}, {self.y})"

class Puzzle:
    @staticmethod
    def from_lines(lines, cheat_length):
        grid = []
        start_node = None
        end_node = None
        for (y, line) in enumerate(lines):
            tile_line = []
            for (x, c) in enumerate(line):
                node = Node(Tile.from_char(c), x, y)

                if node.tile_type == Tile.START:
                    start_node = node
                elif node.tile_type == Tile.END:
                    end_node = node

                if len(tile_line) > 0:
                    left_node = tile_line[-1]
                    node.add_neighbour(left_node)
                    left_node.add_neighbour(node)
                
                if len(grid) > 0:
                    up_node = grid[-1][x]
                    node.add_neighbour(up_node)
                    up_node.add_neighbour(node)

                tile_line.append(node)

            grid.append(tile_line)
        
        if start_node is None:
            raise Exception("Grid had no start node")
        
        if end_node is None:
            raise Exception("Grid had no end node")

        return Puzzle(start_node, end_node, cheat_length)

    # strictly we only need one of these but having both as explicit entry points is nice
    def __init__(self, start_node, end_node, cheat_length):
        self.start_node = start_node
        self.end_node = end_node
        self.cheat_length = cheat_length
    
    # compute every node's distance to the exit - this will help us when we consider cheats later
    # since it's every node, just do some sort of search. I'll DFS it for ease of implementation
    def compute_distances_to_end(self):
        distances = {}
        nodes = [(0, self.end_node)]

        while len(nodes) > 0:
            distance, this_node = nodes.pop()

            # already considered a node, don't look again
            if this_node in distances:
                continue

            distances[this_node] = distance

            for neighbour in this_node.neighbours:
                if neighbour not in distances:
                    nodes.append((distance+1, neighbour))

        return distances
    
    # find cheats from a node, given the distances to the end for each
    # returns a list of all the cheats possible, sorted by time saved
    def find_cheats(self, from_node, distances):
        # figure out every node we could reach in that many steps
        reachable = set()
        reachable.add(from_node)
        for _ in range(self.cheat_length):
            new_reachable = set()
            for node in reachable:
                for neighbour in node.cheat_neighbours:
                    new_reachable.add(neighbour)

            reachable = new_reachable
        
        # now figure out the time-save
        cheats = []
        for target_node in reachable:
            # walls are never a time-save
            if target_node.tile_type == Tile.WALL:
                continue

            # otherwise, the time saved is the difference in distances minus the length of the cheat, and track which node it's to (nb. set means we're not going to end up with duplicates)
            time_save = distances[from_node] - distances[target_node] - self.cheat_length
            cheats.append((time_save, target_node))

        cheats.sort()

        return cheats

        
    # every possible cheat is just skipping two tiles, and we can easily compute the time saved as the value on this node versus the distance so far
    # and by DFSing out from the start node we can do that for every single node
    def get_num_cheats(self, debug=False):
        distances = self.compute_distances_to_end()

        # now, for every node...
        considered = set()
        nodes = [self.start_node]

        cheats = defaultdict(int)
        while len(nodes) > 0:
            this_node = nodes.pop()

            if this_node in considered:
                continue

            these_cheats = self.find_cheats(this_node, distances)
            for (time_save, target) in these_cheats:
                if debug:
                    print(f"Cheat found: {this_node} to {target} (saved {time_save} picoseconds)")

                cheats[time_save] += 1

            for neighbour in this_node.neighbours:
                if neighbour not in considered:
                    nodes.append(neighbour)

            considered.add(this_node)
        
        return cheats


def accept_input():
    lines = []
    try:
        while True:
            lines.append(input())
    except EOFError:
        return Puzzle.from_lines(lines, 2)

def part1(puzzle, debug=False):
    cheats = puzzle.get_num_cheats(debug=debug)

    over_100_count = 0

    # in the debug config only, we sort this to make it easier to read
    items = cheats.items()
    if debug:
        items = sorted(items)

    for (time_save, count) in items:
        if debug and time_save > 0:
            print(f"There are {count} cheats that save {time_save} picoseconds.")

        if time_save >= 100:
            over_100_count += count
    
    return over_100_count

def part2(puzzle):
    raise NotImplementedError("Part 2 not implemented")

def main():
    puzzle = accept_input()
    print(f"Part 1: {part1(puzzle, debug=True)}")
    print(f"Part 2: {part2(puzzle)}")

main()