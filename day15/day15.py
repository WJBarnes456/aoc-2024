from enum import Enum
import copy

class Tile(Enum):
    FREE = 0
    WALL = 1
    BOX = 2
    BOX_LEFT = 3
    BOX_RIGHT = 4

    def __str__(self):
        match self:
            case Tile.FREE:
                return '.'
            case Tile.WALL:
                return '#'
            case Tile.BOX:
                return 'O'
            case Tile.BOX_LEFT:
                return '['
            case Tile.BOX_RIGHT:
                return ']'

class Map:
    @staticmethod
    def from_lines(map_lines):

        map = []
        robot_position = None

        for (y,text_line) in enumerate(map_lines):
            tile_line = []
            for (x,c) in enumerate(text_line):
                match c:
                    case '.':
                        tile_line.append(Tile.FREE)
                    case 'O':
                        tile_line.append(Tile.BOX)
                    case '#':
                        tile_line.append(Tile.WALL)
                    case '@':
                        # as our protagonist, we'll treat the robot differently
                        # mark the space free, and keep track of its position instead
                        tile_line.append(Tile.FREE)
                        robot_position = (x,y)
                    case _:
                        raise Exception(f"Invalid character {c} at position {x,y}")
            map.append(tile_line)

        if robot_position is None:
            raise Exception("Map does not contain robot")
        
        return Map(map, robot_position)
    
    def __init__(self, map_tiles, robot_position):
        self.map = map_tiles
        self.robot_position = robot_position
    
    def __str__(self):
        # turn each tile into its string, then join those lines together
        return "\n".join("".join(str(t) for t in line) for line in self.map)
    
    # "(This process does not stop at wall tiles; measure all the way to the edges of the map.)"
    # easier just to keep the outer walls in our representation.
    def total_gps_score(self):
        total = 0
        for (y, line) in enumerate(self.map):
            for (x,tile) in enumerate(line):
                if tile == Tile.BOX:
                    total += x + 100*y
        
        return total
    
    def copy(self):
        return Map(copy.deepcopy(self.map), self.robot_position)
    
    def widen(self):
        new_map = []
        for line in self.map:
            new_line = []
            for tile in line:
                match tile:
                    case Tile.FREE:
                        new_line += [Tile.FREE, Tile.FREE]
                    case Tile.BOX:
                        new_line += [Tile.BOX_LEFT, Tile.BOX_RIGHT]
                    case Tile.WALL:
                        new_line += [Tile.WALL, Tile.WALL]
                    case _:
                        raise Exception(f"Tried to widen invalid tile {tile}") 
            
            new_map.append(new_line)
        
        new_robot_position = (2 * self.robot_position[0], self.robot_position[1])
        return Map(new_map, new_robot_position)
    
    def get_tile(self, position):
        return self.map[position[1]][position[0]]
    
    def set_tile(self, position, tile):
        self.map[position[1]][position[0]] = tile
    
    # "The problem is that the movements will sometimes fail as boxes are shifted around"
    # i.e. we'll need to check if the robot actually pushes boxes and move them all as one if possible
    def execute_move(self, move):
        # map from positions in the input to (x, y) changes (given this is a top-left centered coordinate system)
        direction_dict = {'<': (-1, 0), '^': (0, -1), '>': (1, 0), 'v': (0, 1)}

        delta = direction_dict[move]
        # start by looking from the robot's own position
        next_pos = self.robot_position

        # now figure out how many boxes need moving, and move them across
        while True:
            next_pos = (next_pos[0] + delta[0], next_pos[1] + delta[1])
            next_tile = self.get_tile(next_pos)
            match next_tile:
                # if we hit a wall, nothing can happen, so just return (the move was a no-op)
                case Tile.WALL:
                    return
                # if we hit a box, then we add it to the stack
                case Tile.BOX:
                    continue

                # if we hit a free, then we need to move the entire stack so far. we can do this by stepping back over the array and moving them in turn
                case Tile.FREE:
                    # move them one by one starting from the previous position all the way back to the robot 
                    prev_pos = (next_pos[0] - delta[0], next_pos[1] - delta[1])
                    while self.get_tile(prev_pos) == Tile.BOX:
                        self.set_tile(next_pos, Tile.BOX)
                        self.set_tile(prev_pos, Tile.FREE)
                        next_pos = prev_pos
                        prev_pos = (next_pos[0] - delta[0], next_pos[1] - delta[1])
                    
                    # finally, the robot managed to move the whole stack across, so step it in the right direction
                    self.robot_position = (self.robot_position[0] + delta[0], self.robot_position[1] + delta[1])
                    return
                
                case _:
                    raise Exception(f"Unhandled tile {next_tile} at {next_pos}")

class Puzzle:
    def __init__(self, puzzle_map, moves):
        self.map = puzzle_map
        self.moves = moves
    
    def __str__(self):
        return str(self.map) + "\n\n" + self.moves
    
    def total_gps_score(self):
        return self.map.total_gps_score()
    
    # it would be easiest to just mutate the map for this, but to keep the base map intact we'll clone it instead
    def run_moves(self):
        this_map = self.map.copy()
        for move in self.moves:
            this_map.execute_move(move)
        
        return this_map
    
    def run_moves_part2(self):
        this_map = self.map.widen()
        for move in self.moves:
            this_map.execute_move(move)
        
        return this_map
    
def accept_map():
    lines = []
    while True:
        line = input()
        if not line:
            return Map.from_lines(lines)
        
        lines.append(line)

def accept_moves():
    moves = ""
    while True:
        try:
            line = input()
            moves += line
        except EOFError:
            return moves

def accept_input():
    puzzle_map = accept_map()
    puzzle_moves = accept_moves()
    return Puzzle(puzzle_map, puzzle_moves)

def part1(puzzle):
    executed_map = puzzle.run_moves()
    return executed_map.total_gps_score()

def part2(puzzle):
    wide_map = puzzle.run_moves_part2()
    return wide_map.total_gps_score()

def main():
    puzzle = accept_input()
    print(puzzle)
    print(f"Part 1: {part1(puzzle)}")
    print(f"Part 2: {part2(puzzle)}")

main()