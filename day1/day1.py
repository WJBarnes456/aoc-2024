# was busy today so just hacking together a quick solution in Python, I'd like to do the rest in Go with some nice test harness but I'll set that up when I'm in less of a rush

from collections import defaultdict
import re

# grabs the two numbers as two match groups
extract_number_regex = re.compile(r'(\d+)\s+(\d+)')

def accept_lists():
    values_1, values_2 = [],[]
    while True:
        try:
            line = input()
        except EOFError:
            return values_1, values_2
            
        if line.strip() == '':
            return values_1, values_2
        match = extract_number_regex.fullmatch(line)
        v1, v2 = match.group(1,2)
        values_1.append(int(v1))
        values_2.append(int(v2))

def main():
    values_1, values_2 = accept_lists()
    score_1 = part1(values_1, values_2)
    score_2 = part2(values_1, values_2)
    print(f"Distance: {score_1}")
    print(f"Similarity score: {score_2}")
    
def part1(values_1, values_2):
    score = 0
    for v1, v2 in zip(sorted(values_1), sorted(values_2)):
        score += abs(v1 - v2)
    return score

def part2(values_1, values_2):
    right_list_occurrences = defaultdict(int)
    for v in values_2:
        right_list_occurrences[v] += 1
    
    score = 0
    for v in values_1:
        score += v * right_list_occurrences[v]
    return score

main()