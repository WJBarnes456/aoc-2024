# while you could do this with lots of multiplication, the fact you're multiplying by 2024 means it's actually easier to just use logarithms
# it's worth noting that we will run into precision issues here if we get too big - the right hand of the number will drift
# although we need to be careful that splitting the stone into two still gives us an integer after raising 10 to that power
# we could do it all with bigints instead - this would be guaranteed to be correct, but is a bit slower. Besides, I just wanted to implement it using logarithms

from math import log10, floor

log_2024 = log10(2024)

def accept_input():
    line = input()
    return [int(v) for v in line.split(" ")]

def to_logstone(stone):
    if stone == 0:
        return None
    else:
        return log10(stone)

def from_logstone(logstone):
    if logstone is None:
        return 0
    else:
        return 10**logstone

def step(logstones):
    new_logstones = []
    for logstone in logstones:
        # step from 0 to 1
        if logstone == None:
            new_logstones.append(0)
            continue

        fls = floor(logstone)        

        # if there's an even number of digits, then split it
        if fls % 2 == 1:
            stone = str(int(round(10 ** logstone)))

            # even number of digits, so it's easy to split
            halfway = (fls + 1) // 2
            new_logstones.append(to_logstone(int(stone[:halfway])))
            new_logstones.append(to_logstone(int(stone[halfway:])))
            continue

        # otherwise multiply by 2024
        new_logstones.append(logstone + log_2024)

    return new_logstones  

# for part1, it was enough to simulate all the stones directly
# however for part2 we can't do that... but we're certainly running into shared subproblems (not least for any duplicated stones)
# hence we can memoize by (stone value, blinks_remaining) and sum that rather than just stepping
# this is easier to reason about if we start using values directly rather than logarithms
def iterate(stones, blinks):
    # apply the trick - replace every stone with its value log base 10
    logstones = [to_logstone(stone) for stone in stones]

    for i in range(blinks):
        logstones = step(logstones)
        #print([from_logstone(ls) for ls in logstones])
    
    return len(logstones)

def part1(stones):
    return iterate(stones, 25)

def part2(stones):
    return iterate(stones, 75)

def main():
    stones = accept_input()
    print(f"Part 1: {part1(stones)}")
    print(f"Part 2: {part2(stones)}")

main()