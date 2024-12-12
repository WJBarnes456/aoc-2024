# I had initially implemented this as logarithms base 10, but given we want to memoise by stone value then representing everything as exact integers makes it easier
# python ints are bigints by default which makes this easy enough

from math import log10, floor

def accept_input():
    line = input()
    return [int(v) for v in line.split(" ")]

# for part1, it was safe to simulate all the stones directly
# however for part2 we can't do that... but we're certainly running into shared subproblems (not least for any duplicated stones)
# hence we can memoize by (stone value, blinks_remaining) and sum that rather than just stepping
# this is easier to reason about if we start using values directly rather than logarithms - I should've just used values to start off with
# (although using the list representation to start off with was nicer in case we changed how the step function worked) 
memo = {}
def stones_for_count(stone, blinks):
    if (stone, blinks) in memo:
        return memo[(stone, blinks)]
    else:
        # base case, no blinks left => it's just this number
        # no need to memoise that
        if blinks == 0:
            return 1

        # otherwise, you've got blinks left, so step the stone
        if stone == 0:
            val = stones_for_count(1, blinks - 1)
        elif floor(log10(stone)) % 2 == 1:
            # even number of digits, so split it into the two subproblems
            string_stone = str(stone)
            halfway = len(string_stone) // 2
            left = int(string_stone[:halfway])
            right = int(string_stone[halfway:])

            # you can halve the size of the memo with no real slowdown by only memoising the result for these fork points (which are also the most expensive to compute)
            # as it is it's easier to reason about setting in all cases
            val = stones_for_count(left, blinks-1) + stones_for_count(right, blinks-1)
        else:
            val = stones_for_count(stone * 2024, blinks-1)
        
        memo[(stone, blinks)] = val
        return val

def part1(stones):
    return sum(stones_for_count(stone, 25) for stone in stones)

def part2(stones):
    return sum(stones_for_count(stone, 75) for stone in stones)

def main():
    stones = accept_input()
    print(f"Part 1: {part1(stones)}")
    print(f"Part 2: {part2(stones)}")

    print(f"Memo size: {len(memo)}")

main()