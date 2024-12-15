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
        # to print the map, convert each tile to its string, special-casing the robot
        # in retrospect this would've been easier to reason about if I'd just had the robot as its own tile from the beginning...

        out = []
        for (y, line) in enumerate(self.map):
            out_line = []
            for (x, t) in enumerate(line):
                if (x,y) == self.robot_position:
                    out_line.append('@')
                else:
                    out_line.append(str(t))
            out.append("".join(out_line))
        return "\n".join(out)
    
    # "(This process does not stop at wall tiles; measure all the way to the edges of the map.)"
    # easier just to keep the outer walls in our representation.
    def total_gps_score(self):
        total = 0
        for (y, line) in enumerate(self.map):
            for (x,tile) in enumerate(line):
                # closest edge to the top left corner in part 2 is always the left part of the box
                if tile == Tile.BOX or tile == Tile.BOX_LEFT:
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
    
    # worth noting that we can try moving boxes in whichever way, and it might eventually fail
    # a not-super-nice workaround here is to be eager and back out, undoing changes to the map if it fails at the top level
    def move_boxes_starting_from(self, position, delta, cloned_map = None):
        next_pos = position
        while True:
            next_pos = (next_pos[0] + delta[0], next_pos[1] + delta[1])
            next_tile = self.get_tile(next_pos)
            match next_tile:
                # if we hit a wall, nothing can happen, so just return (the move was a no-op)
                case Tile.WALL:
                    # we return the existing map in this scenario since we don't want to revert in the instance we just hit the wall without attempting to move anything
                    return (False, self.map)
                # if we hit a whole box, then we add it to the stack
                case Tile.BOX:
                    continue

                # if we hit a partial box, then we have two cases...
                # we merged this with Free because Python doesn't support case fall-through
                case Tile.BOX_LEFT | Tile.BOX_RIGHT | Tile.FREE:

                    # handle a partial box
                    if next_tile != Tile.FREE:
                        # if we're moving horizontally, it's no different to the one box case. just stack that up and move them at once
                        if delta[1] == 0:
                            continue

                        # if we're moving vertically, then we might be in contact with 0, 1 or 2 other boxes
                        if next_tile == Tile.BOX_LEFT:
                            other_box_pos = (next_pos[0] + 1, next_pos[1])
                        elif next_tile == Tile.BOX_RIGHT:
                            other_box_pos = (next_pos[0] - 1, next_pos[1])
                        
                        # try moving both of the tiles above us 
                        # we might be about to make a mistake, so take a copy of the map now, and pass that into the children
                        # this is so we don't unnecessarily clone the map every single time, only when we're doing something we might need to undo 
                        if cloned_map == None:
                            cloned_map = copy.deepcopy(self.map)
                        
                        (first_box_moved, _) = self.move_boxes_starting_from(next_pos, delta, cloned_map=cloned_map)
                        
                        if not first_box_moved:
                            return False, cloned_map
                        
                        (second_box_moved, _) = self.move_boxes_starting_from(other_box_pos, delta, cloned_map=cloned_map)

                        if not second_box_moved:
                            return False, cloned_map
                        
                        # if we succeeded moving both parts of the box above us, we now have a free on top of us... so we can fall through into the free case
                        # (my initial implementation actually wouldn't have worked in a mixed box type scenario I don't think, as we wouldn't have moved the other boxes we skipped over)

                    # move them one by one starting from the previous position all the way back to the robot 
                    prev_pos = (next_pos[0] - delta[0], next_pos[1] - delta[1])
                    prev_tile = self.get_tile(prev_pos)

                    prev_prev_pos = next_pos
                    while True:
                        self.set_tile(prev_prev_pos, prev_tile)
                        self.set_tile(prev_pos, Tile.FREE) # we free this temporarily

                        # if we're about to overstep our starting position, then stop here
                        if prev_pos == position:
                            break

                        prev_prev_pos = prev_pos
                        prev_pos = (prev_pos[0] - delta[0], prev_pos[1] - delta[1])
                        prev_tile = self.get_tile(prev_pos)
                    
                    return (True, None)
                case _:
                    raise Exception(f"Unhandled tile {next_tile} at {next_pos}")


    
    # "The problem is that the movements will sometimes fail as boxes are shifted around"
    # i.e. we'll need to check if the robot actually pushes boxes and move them all as one if possible
    def execute_move(self, move):
        # map from positions in the input to (x, y) changes (given this is a top-left centered coordinate system)
        direction_dict = {'<': (-1, 0), '^': (0, -1), '>': (1, 0), 'v': (0, 1)}

        delta = direction_dict[move]

        # eagerly try moving the robot. this might fail, and if it does we'll be told what the map state used to be
        # we let the underlying function make this decision as there's only one (relatively rare) path that we actually need to undo
        (robot_moved, next_map) = self.move_boxes_starting_from(self.robot_position, delta)

        # we successfully moved the robot!
        if robot_moved:
            self.robot_position = (self.robot_position[0] + delta[0], self.robot_position[1] + delta[1])
        else:
            # we failed to move the robot, so reset to the state we were told it was in before
            self.map = next_map

class Puzzle:
    def __init__(self, puzzle_map, moves):
        self.map = puzzle_map
        self.moves = moves
    
    def __str__(self):
        return str(self.map) + "\n\n" + self.moves
    
    def total_gps_score(self):
        return self.map.total_gps_score()
    
    def run_moves(self):
        # it would be easiest to just mutate the map for this, but to keep the base map intact we'll clone it instead
        this_map = self.map.copy()
        for move in self.moves:
            this_map.execute_move(move)
        
        return this_map
    
    def run_moves_part2(self):
        this_map = self.map.widen()
        for move in self.moves:
            this_map.execute_move(move)

            #print(f"Move {move}:\n{this_map}")
       
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