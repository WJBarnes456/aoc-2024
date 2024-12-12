# okay, didn't have time for that harness I was hoping for last night. so we're Pythoning again

import itertools

def accept_input():
    out = []
    while True:
        try:
            line = input()
            out.append(line)
        except EOFError:
            return out

def is_xmas(wordsearch, offsets, i, j):
    for o in offsets:
        new_i, new_j = i+o[0], j+o[1]
        
        # don't go out of bounds (Python will automatically wrap the string for us if we go negative which we don't want)
        if new_i < 0 or new_j < 0 or new_i >= len(wordsearch) or new_j >= len(wordsearch[0]):
            return False
        
        if wordsearch[new_i][new_j] != o[2]:
            return False
    
    return True


# solve this by iterating over the wordsearch looking for XMAS in any direction starting from the letter X
def count_xmases(wordsearch, i, j):
    # only count starting from an instance of the letter X
    if wordsearch[i][j] != "X":
        return 0
    
    count = 0
    # consider each possible direction that an XMAS might appear in...
    for d in itertools.product((-1,0,1),(-1,0,1)):
        # stepping once in the direction is M, then A, then S
        offsets = [(0,0,'X'),(d[0], d[1], 'M'), (2*d[0], 2*d[1], 'A'), (3*d[0], 3*d[1], 'S')]
        if is_xmas(wordsearch, offsets, i, j):
            count += 1
            print(f"XMAS at ({j},{i}) in direction {d[1],d[0]}")
    
    return count

def count_crossmasses(wordsearch, i, j):
    # only count starting from an A (as each crossmas has only one A)
    if wordsearch[i][j] != "A":
        return 0
    
    # the three components are (delta_i, delta_j, direction of other MAS)
    for d in itertools.product((-1, 1), (-1, 1), (-1, 1)):
        # we want the current character to be an A...
        offsets = ((0,0,'A'),
            # stepping in one direction to be M in front and S behind....
            (d[0],d[1],'M'),(-d[0],-d[1],'S'),
            # and stepping in the adjacent direction to be either an M in front and an S behind or vice-versa
            (d[2] * d[0], d[2] * -d[1],'M'),(d[2] * -d[0], d[2] * d[1],'S'))
        if is_xmas(wordsearch, offsets, i, j):
            return 1
            
    return 0

def find_all_xmases(wordsearch, score_function):
    xmases = 0
    for i in range(len(wordsearch)):
        for j in range(len(wordsearch[0])):
            xmases += score_function(wordsearch, i, j)
    return xmases
    
def part1(wordsearch):
    return find_all_xmases(wordsearch, count_xmases)

def part2(wordsearch):
    return find_all_xmases(wordsearch, count_crossmasses)

def main():
    wordsearch = accept_input()
    part1_score = part1(wordsearch)
    print(f"Part 1 (XMASes): {part1_score}")
    part2_score = part2(wordsearch)
    print(f"Part 2 (X-MASes): {part2_score}")

main()