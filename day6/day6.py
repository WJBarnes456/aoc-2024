def accept_input():
    # for ease of iteration this is a (y,x) coordinate
    guard_position = None
    occupancy = []
    
    # we're tracking the current line number so we know where the guard is
    i = 0
    while True:
        try:
            line = input()
        except EOFError:
            if guard_position is None:
                raise Exception("Map did not set guard position")
            return occupancy, guard_position
        line_occupancy = []
        for (j,c) in enumerate(line):
            if c == '.':
                line_occupancy.append(False)
            elif c == '#':
                line_occupancy.append(True)
            elif c == '^':
                guard_position = (i,j)
                line_occupancy.append(False)
        occupancy.append(line_occupancy)
        i += 1

def print_map(occupancy):
    for line in occupancy:
        print("".join(['#' if v else '.' for v in line]))
def build_empty_map(occupancy):
    # assume occupancy is a rectangular array (always true for our input, might not be true in general)
    # i.e. no need to worry about it being ragged
    return [[set() for _ in occupancy[0]] for _ in occupancy]

def guard_on_map(occupancy, gp):
    return gp[0] >= 0 and gp[0] < len(occupancy) and gp[1] >= 0 and gp[1] < len(occupancy[0])

class GuardLoop(Exception):
    pass

def build_occupation_map(occupancy, guard_position):
    # Assume that the guard is always facing up originally (this is true in both the example input and real input)
    # this direction vector is also in (y,x) coordinates for ease of reasoning
    guard_direction = (-1, 0)
    ever_occupied = build_empty_map(occupancy)
    
    # reassign these to shorthands for ease of typing
    gp = guard_position
    gd = guard_direction
    
    
    # while the guard is actually on the map, and not caught in a loop...
    # (I didn't actually implement loop support until seeing part2 so I could've ended up looping forever before that)
    while guard_on_map(occupancy, gp) and gd not in ever_occupied[gp[0]][gp[1]]:
        ever_occupied[gp[0]][gp[1]].add(gd)
        
        next_step = (gp[0]+gd[0], gp[1]+gd[1])
        # If there is something directly in front of you, turn right
        if guard_on_map(occupancy, next_step) and occupancy[next_step[0]][next_step[1]]:
            # up = (-1,0), right = (0,1), down = (1,0), left = (0,-1)
            gd = (gd[1],-gd[0])
        # otherwise take a step forward
        else:
            gp = next_step
    
    # if the guard is still on the map as of the above, we ended up in the same direction at the same position as seen previously
    if guard_on_map(occupancy, gp):
        raise GuardLoop(f"Looped at {gp}")
    
    return ever_occupied
        
def part1(occupancy, guard_position):
    ever_occupied = build_occupation_map(occupancy, guard_position)
    
    # return the total number of positions which ever had a direction attached
    return sum(sum((len(x) > 0) for x in row) for row in ever_occupied)    

# this works but is really quite slow - took a good few seconds on my machine
# it would be easy to parallelise (different placements are independent) but doesn't really solve the underlying complexity problem
# there are some other constant-factor improvements by using contiguous 2d arrays rather than ragged ones, and using a language other than Python with lower overheads
# however this is more than fast enough to work in a reasonable amount of time
def part2(occupancy, guard_position):
    # a later optimisation - there's no point putting an obstacle somewhere the guard never walks
    base_occupied = build_occupation_map(occupancy, guard_position)

    # we can break this down back to the original position - just add a new obstacle in each valid position and then delegate back to part 1
    valid_obstructions = 0
    for (i,row) in enumerate(occupancy):
        for (j,value) in enumerate(row):
            # give up if this is an invalid obstruction placement
            # i.e. there's already an obstruction here, or the guard is here
            if value == True or ((i,j) == guard_position):
                continue
            
            # later optimisation: don't consider positions the guard never goes to anyway
            if len(base_occupied[i][j]) == 0:
                continue
            
            # add the obstruction
            new_row = row[:j] + [True] + row[j+1:]
            new_occupancy = occupancy[:i] + [new_row] + occupancy[i+1:]
            
            # run the simulation
            try:
                part1(new_occupancy, guard_position)
            except GuardLoop:
                print(f"Looped with obstacle at {(i,j)}")
                valid_obstructions += 1
    return valid_obstructions
        

def main():
    occupancy, guard_position = accept_input()
    print(f"Guard position {guard_position}, map:")
    print_map(occupancy)
    
    part1_score = part1(occupancy, guard_position)
    print(f"Part 1: {part1_score}")
    
    part2_score = part2(occupancy, guard_position)
    print(f"Part 2: {part2_score}")

main()