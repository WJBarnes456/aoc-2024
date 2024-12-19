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
    def __init__(self, tile_type, x, y):
        self.tile_type = tile_type
        self.neighbours = set()
        self.x = x
        self.y = y
    
    def add_neighbour(self, other_node):
        if self.tile_type != Tile.CORRUPTED and other_node.tile_type != Tile.CORRUPTED:
            self.neighbours.add(other_node)
    
    def corrupt(self):
        # when you corrupt a node, you need to change its tile type, and disconnect it from its neighbours
        for neighbour in self.neighbours:
            neighbour.neighbours.remove(self)
        
        self.tile_type = Tile.CORRUPTED

class Puzzle:
    def __init__(self, byte_positions, grid_size):
        self.byte_positions = byte_positions
        self.grid_size = grid_size

        self.start_node, self.grid = self.initialise_grid()
    
    def get_first_1024_corrupted_positions(self):
        corrupted_positions = set()

        for (i, byte) in enumerate(self.byte_positions):
            if i > 1023:
                return corrupted_positions
            
            corrupted_positions.add(byte)
        
        return corrupted_positions

    
    def initialise_grid(self):
        # part1 we can just Dijkstra no problem - we just need to build the actual grid first
        corrupted_positions = self.get_first_1024_corrupted_positions()

        # "You and The Historians are currently in the top left corner of the memory space (at 0,0)"
        start_node = None
        
        grid = []
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

                node = Node(tile_type, x, y)

                if len(line) > 0:
                    left_node = line[-1]
                    left_node.add_neighbour(node)
                    node.add_neighbour(left_node)
                
                if len(grid) > 0:
                    up_node = grid[-1][x]
                    up_node.add_neighbour(node)
                    node.add_neighbour(up_node)
                
                if (x,y) == (0,0):
                    start_node = node

                line.append(node)

            grid.append(line)

        return start_node, grid
    
    # for part1: we've already initialised a graph we can run Dijkstra over, let's do that
    def shortest_path(self):
        prev_node_lookup = {}

        # this is just for tiebreaks
        queue_counter = 1

        # we start at the start, which is no steps away
        queue = [(0, 0, self.start_node, None)]
        heapify(queue)

        # consider all the nodes we can reach in n+1 steps
        while len(queue) > 0:
            distance, _, node, prev_node = heappop(queue)
            if node in prev_node_lookup:
                continue

            # we found the shortest route to the end!
            if node.tile_type == Tile.END:
                # follow the previous nodes all the way back
                path = [(node.x, node.y)]
                while prev_node is not None:
                    path.append((prev_node.x, prev_node.y))
                    prev_node = prev_node_lookup[prev_node]

                return path

            # if not, consider everywhere we can go from here
            for neighbour in node.neighbours:
                # do not go backwards
                if neighbour not in prev_node_lookup:
                    heappush(queue, (distance+1, queue_counter, neighbour, node))
                    queue_counter += 1

            prev_node_lookup[node] = prev_node
        
        return None
    
    # wow this is way easier than I was expecting... we just need a nice function to corrupt a node, and to keep the grid around
    # it would only be too slow if we tried rebuilding the grid every time, if we just make small adjustments then it's fine
    # could definitely be faster if we didn't rerun dijkstra for nodes that don't affect the current shortest path... I'll implement after
    def part2(self):
        current_shortest_path = self.shortest_path()

        # consider each new byte
        for byte in self.byte_positions[1023:]:
            self.grid[byte[1]][byte[0]].corrupt()

            # if the byte isn't on the current path, then no need to recompute anything
            # but if it does disrupt the path, then we might have something to worry about
            if byte in current_shortest_path:
                current_shortest_path = self.shortest_path()

            # if the puzzle is no longer solvable, this is the byte that broke the puzzle's back
            if current_shortest_path == None:
                return byte

        return None



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
    return len(puzzle.shortest_path()) - 1

def part2(puzzle):
    return puzzle.part2()

def main():
    puzzle = accept_input()
    print(f"Part 1: {part1(puzzle)}")
    print(f"Part 2: {part2(puzzle)}")

main()