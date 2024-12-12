# ok it's gonna be no harness again both today and tomorrow because of other life things but we're fine

from collections import defaultdict

def accept_input():
    rules = []
    while True:
        line = input()
        if not line:
            break
        x,y = line.split('|')
        rules.append((int(x),int(y)))
    
    updates = []
    while True:
        try:
            line = input()
        except EOFError:
            return rules, updates
        
        updates.append([int(x) for x in line.split(',')])


# Part 1
# for the update to be correct, it must satisfy every ordering rule...
# but you don't need to iterate through all the rules to do that
# a cleverer way is to build a dictionary to look up each value that's distilled to the rules it relates to
# and have the set of values that cannot appear before it
# my first thought was that you need two dictionaries, but I misunderstood the spec - missing page numbers are ignored, so you don't need to worry about them occurring after
# then step through the list taking intersections of the set of values up to that point
#
# for the input length and this part, I think it'd be possible to just naively iterate through each rule, but I want to do it the sets way so I will
def build_lookups(rules):
    rule_lookup = defaultdict(set)
    
    # x must appear before y, so if y is already present when x is considered, it's not valid.
    for (x,y) in rules:
        rule_lookup[x].add(y)
    
    return rule_lookup

def valid_update(lookup, update):
    previous_values = set()
    for v in update:
        prohibited_values = lookup[v]
        print(f"{v} must appear before {prohibited_values}")
        if len(previous_values.intersection(prohibited_values)) != 0:
            return False
        previous_values.add(v)
    return True

def get_middle_value(update):
    # assume updates are odd in length, but don't error if it's even
    mid_index = (len(update)-1)//2
    return update[mid_index]

def part1(rules, updates):
    lookup = build_lookups(rules)
    print(lookup)
    
    count = 0
    for update in updates:
        if valid_update(lookup, update):
            middle_page_number = get_middle_value(update)
            print(f"{update} is valid, adding middle_page_number {middle_page_number}")
            count += middle_page_number
    return count

# Part 2
# we're building a sorting algorithm using these non-standard comparison rules!
# my naive idea was very similar to an insertion sort (do the set membership tests again, if something is in the wrong place, pop it across)
# however it's actually pretty easy to do a quicksort too - take the first one as a pivot, and being "in the set" puts it on the right partition (otherwise put it on the left)
# we'll do this out-of-place by separating and combining lists simply because it's easier to write and reason about (I could do an in-place one if I wanted but not required for performance here)
def quicksort(update, lookup):
    if len(update) < 2:
        return update
    pivot = update[0]
    after_pivot = lookup[pivot]
    left, right = [], []
    for v in update[1:]:
        if v in after_pivot:
            right.append(v)
        else:
            left.append(v)
    return quicksort(left, lookup) + [pivot] + quicksort(right, lookup)

def part2(rules, updates):
    lookup = build_lookups(rules)
    
    count = 0
    for update in updates:
        sorted_update = quicksort(update, lookup)
        print(f"update: {update}, sorted: {sorted_update}")
        if update != sorted_update:
            count += get_middle_value(sorted_update)
    return count
    

def main():
    rules, updates = accept_input()
    print(f"Rules: {rules}, updates {updates}")
    part1_score = part1(rules, updates)
    print(f"Part1: {part1_score}")
    part2_score = part2(rules, updates)
    print(f"Part2: {part2_score}")

main()