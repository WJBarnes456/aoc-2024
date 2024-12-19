# after that horrific day17, day18 seems much easier.... but maybe there's something in it
# "a byte falls once every nanosecond" => possible we'll need to simulate the passing of time to find a valid route in part 2? the real input is 3450 lines but we're asked to only operate on the first 1024 for part 1 
# if this is the case then we need to flip the problem on its head and calculate the best next steps for the final state, and subsequently _remove_ barriers and recalculate it
# nb. we might need to change the time offset if we end up being overoptimistic and not having any possible route in that time

from enum import Enum

import re
from heapq import heapify, heappop, heappush

class Tile(Enum):
    SAFE = 0
    CORRUPTED = 1
    END = 2

class Node:
    def __init__(self, tile_type):
        self.tile_type = tile_type
        self.neighbours = set()
    
    def add_neighbour(self, other_node):
        if self.tile_type != Tile.CORRUPTED and other_node.tile_type != Tile.CORRUPTED:
            self.neighbours.add(other_node)

class Puzzle:
    def __init__(self, byte_positions, grid_size):
        self.byte_positions = byte_positions
        self.grid_size = grid_size

        self.part1_start = self.initialise_part1_grid()
    
    def get_first_1024_corrupted_positions(self):
        corrupted_positions = set()

        for (i, byte) in enumerate(self.byte_positions):
            if i > 1023:
                return corrupted_positions
            
            corrupted_positions.add(byte)
        
        return corrupted_positions

    
    def initialise_part1_grid(self):
        # part1 we can just Dijkstra no problem - we just need to build the actual grid first
        corrupted_positions = self.get_first_1024_corrupted_positions()

        # "You and The Historians are currently in the top left corner of the memory space (at 0,0)"
        start_node = None
        prev_line = None
        
        # both of these have an offset of 1 because we pass in 6, 70 and want those to be the corners
        for y in range(self.grid_size + 1):
            line = []

            for x in range(self.grid_size + 1):
                tile_type = Tile.SAFE

                #  "...and need to reach the exit in the bottom right corner (at 70,70 in your memory space, but at 6,6 in this example)"
                if (x == self.grid_size) and (y == self.grid_size):
                    tile_type = Tile.END
                
                # assumption: the end doesn't get corrupted in the input. Safe for my input, but would lead to an unsolvable puzzle in the general case
                if (x,y) in corrupted_positions:
                    tile_type = Tile.CORRUPTED

                node = Node(tile_type)

                if len(line) > 0:
                    left_node = line[-1]
                    left_node.add_neighbour(node)
                    node.add_neighbour(left_node)
                
                if prev_line is not None:
                    up_node = prev_line[x]
                    up_node.add_neighbour(node)
                    node.add_neighbour(up_node)
                
                if (x,y) == (0,0):
                    start_node = node

                line.append(node)
            
            prev_line = line
        
        return start_node
    
    # for part1: we've already initialised a graph we can run Dijkstra over, let's do that
    def part1(self):
        visited = set()

        # this is just for tiebreaks
        queue_counter = 1

        # we start at the start, which is no steps away
        queue = [(0, 0, self.part1_start)]
        heapify(queue)

        # consider all the nodes we can reach in n+1 steps
        while len(queue) > 0:
            distance, _, node = heappop(queue)
            if node in visited:
                continue

            # we found the shortest route to the end!
            if node.tile_type == Tile.END:
                return distance

            # if not, consider everywhere we can go from here
            for neighbour in node.neighbours:
                # do not go backwards
                if neighbour not in visited:
                    heappush(queue, (distance+1, queue_counter, neighbour))
                    queue_counter += 1

            visited.add(node)
        
        return None
    
    # wow this is way easier than I was expecting... we just need a nice function to corrupt a node, and to keep the grid around
    def part2(self):
        pass



coord_re = re.compile(r'(\d+),(\d+)')

def accept_input():
    byte_positions = []
    saw_coord_over_6 = False
    while True:
        try:
            line = input()
            match = coord_re.match(line)
            x,y = int(match.group(1)), int(match.group(2))
            byte_positions.append((x,y))

            if x > 6 or y > 6:
                saw_coord_over_6 = True
        except EOFError:
            grid_size = 6
            if saw_coord_over_6:
                grid_size = 70

            return Puzzle(byte_positions, grid_size)

def part1(puzzle):
    return puzzle.part1()

def part2(puzzle):
    return puzzle.part2()

def main():
    puzzle = accept_input()
    print(f"Part 1: {part1(puzzle)}")
    print(f"Part 2: {part2(puzzle)}")

main()