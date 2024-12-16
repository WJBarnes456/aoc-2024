from enum import Enum
from collections import deque

from heapq import heappush, heappop, heapify

class Tile(Enum):
    FREE = 0
    WALL = 1
    START = 2
    END = 3

    def __str__(self):
        match self:
            case Tile.FREE:
                return '.'
            case Tile.WALL:
                return '#'
            case Tile.START:
                return 'S'
            case Tile.END:
                return 'E'


class Map:
    def __init__(self, lines) -> None:
        self.map = []
        self.start_pos = None
        self.end_pos = None
        for (y, line) in enumerate(lines):
            tile_line = []
            for (x, c) in enumerate(line):
                match c:
                    case '#':
                        tile_line.append(Tile.WALL)
                    case '.':
                        tile_line.append(Tile.FREE)
                    case 'S':
                        tile_line.append(Tile.START)
                        self.start_pos = (x,y)
                    case 'E':
                        tile_line.append(Tile.END)
                        self.end_pos = (x,y)
                    case _:
                        raise Exception(f"Unknown tile {c} at ({x},{y})")
            self.map.append(tile_line)
    
    def __str__(self) -> str:
        return "\n".join("".join(str(t) for t in line) for line in self.map)
 
    # gets the tile at a given position
    def get_tile(self, position):
        return self.map[position[1]][position[0]]
    
    # "Reindeer compete for the lowest score"
    # i.e. look for the route through the maze with the fewest rotations
    # for smaller maps we can do this exhaustively, but we will end up on shared subproblems eventually
    # we have a couple of different ways of doing it:
    # start from the start, and iterate forwards - benefit, we always know which way we start, drawback is that the "cheapest" path to the end might become even cheaper if we find an alternative route with more moves but fewer rotations
    # e.g. consider
    # ##############
    # #...........##
    # #.#########.##
    # #.........#.##
    # #########.#.##
    # #.........#.##
    # #S#########.E#
    # #.#...#...#.##
    # #...#...#...##
    # ##############
    # bottom route is much shorter, but top route is lower cost
    # (bottom route requires 12 rotations, top requires 8 rotations)
    # so if we DFS'd and did the bottom route we'd need to update all our scores
    #
    # start from the end, and iterate backwards - drawback, we have uncertainty about directions, benefit is that we always have the cheapest route from that point to the end, and the cheapest way onto the exit is always to walk directly onto it
    # ...actually, wait a second, we can just use our plain old friend Dijkstra for this!
    def calculate_cheapest_path(self):
        # start by searching from the start position with score 0
        visited = set()

        # we add all 4 positions here because the only time that considering a 180 degree turn makes sense is at the start position
        # otherwise it always leads us back where we came which is pointless
        heap = [(0, self.start_pos, (1,0)), (1000, self.start_pos, (0,1)), (1000, self.start_pos, (0,-1)), (2000, self.start_pos, (-1,0))]
        heapify(heap)

        # each node in the heap is the score to get there, the position we'd reach, and the (x,y) delta of which way we're facing
        node = (0, self.start_pos, (1,0))
        while node[1] != self.end_pos:
            score, position, delta = node
            if (position, delta) in visited:
                # we got the cheapest route here already, ignore it
                node = heappop(heap)
                continue

            # now we've got to consider our alternatives of who we can visit
            # no point considering going backwards since we already special-cased it at the start position
            # so we can consider either moving forwards, or turning and moving as their own move
            for (score_delta, this_delta) in [(1, delta), (1001, rotate(delta, 1)), (1001, rotate(delta, -1))]:
                # consider the step in that direction
                next_position = next_pos(position, this_delta)
                
                # if it's a wall, we can't go there
                if self.get_tile(next_position) == Tile.WALL:
                    continue

                # if we already went there, there's no point, this route is more expensive
                if (next_position, this_delta) in visited:
                    continue

                # it's at least worth considering. push it to the queue!
                heappush(heap, (score + score_delta, next_position, this_delta))
            
            # we can now just say we visited here
            # if we need to get the route out, then we'd need to store the node that got us here somehow (I was thinking "we can just follow -delta" but it's not that simple since we might turn and move simultaneously)
            print(f"Visited {node}")
            visited.add((position, delta)) 

        return node[0]

# gets the position after moving delta from the start position
def next_pos(position, delta):
    return (position[0] + delta[0], position[1] + delta[1])

def rotate(delta, direction):
    match direction:
        case 1 | -1:
            return (direction * delta[1], direction * delta[0])
        case 0:
            return delta
        case 2:
            return (-delta[0], -delta[1])
        case _:
            raise Exception(f"Invalid direction {direction}")

def accept_input():
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            return Map(lines)
        lines.append(line)

def part1(map):
    return map.calculate_cheapest_path()

def part2(map):
    raise NotImplementedError("Part 2 not implemented")

def main():
    map = accept_input()
    print(map)
    print(f"Part 1: {part1(map)}")
    print(f"Part 2: {part2(map)}")

main() 