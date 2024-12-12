from collections import defaultdict
from itertools import combinations
import re



class Map:
    antenna_re = re.compile(r'[0-9a-zA-Z]')

    # for ease of working things out, this method might return antinodes outside the map
    # in part1, we can do this by doing the vector once
    def get_antinodes_for_frequency_part1(self, frequency):
        antennae = self.frequency_lookup[frequency]

        # Problem statement: "for any pair of antennas with the same frequency, there are two antinodes, one on either side of them."
        # i.e. to work this out we can get all combinations of two antenna on the same frequency, and work out the coordinates of each location

        antinodes = set()
        for (node1, node2) in combinations(antennae, 2):
            print(f"node pair: {node1}, {node2}")
            # the frequency generates two antinodes - consider the vector node1 -> node2, one antinode is node1 - (node1 -> node2), the other antinode is node2 + (node1 -> node2)
            # the vector (node1 -> node2) is node2 - node1, so substitute this in
            # i.e. the two antinode coordinates are
            antinode1 = (2 * node1[0] - node2[0], 2*node1[1] - node2[1])
            antinode2 = (2 * node2[0] - node1[0], 2*node2[1] - node1[1])

            antinodes.add(antinode1)
            antinodes.add(antinode2)

        print(f"antinodes for frequency {frequency}: {antinodes}")
        return antinodes

    def get_antinodes_for_frequency_part2(self, frequency):
        antennae = self.frequency_lookup[frequency]

        antinodes = set()
        for (node1, node2) in combinations(antennae, 2):
            # different to part1: we need to get the vector between the two, and iterate in both directions until we hit the ends of the map
            # we can do this a few different ways, but for ease of writing let's do this in two passes

            # first pass - step forward from node2
            forward_vec = (node2[0] - node1[0], node2[1] - node1[1])
            current_val = node2
            while self.coord_on_map(current_val):
                antinodes.add(current_val)
                current_val = (current_val[0] + forward_vec[0], current_val[1] + forward_vec[1])

            # second pass - step back from node1
            current_val = node1
            while self.coord_on_map(current_val):
                antinodes.add(current_val)
                current_val = (current_val[0] - forward_vec[0], current_val[1] - forward_vec[1])

        return antinodes


    def coord_on_map(self, coord):
        return coord[0] >= 0 and coord[0] < self.width and coord[1] >= 0 and coord[1] < self.height

    # now let's have this method do the deduplication
    def get_antinodes(self, get_antinodes_for_frequency):
        antinodes = set()

        # get the potential antinode locations for each frequency
        for frequency in self.frequency_lookup.keys():
            freq_antinodes = get_antinodes_for_frequency(frequency)
            for antinode in freq_antinodes:
                # validate the antinode is on the map
                if not self.coord_on_map(antinode):
                    continue

                # if it is on the map, add it
                # since it's a set, that handles the deduplication for us
                antinodes.add(antinode)

        # then return all the antinodes
        print(f"Antinodes: {sorted(antinodes)}")
        return antinodes

    def __init__(self, lines):
        # assume the lines aren't ragged
        self.height = len(lines)
        self.width = len(lines[0])

        self.frequency_lookup = defaultdict(list)
        for (y, line) in enumerate(lines):
            for (x, v) in enumerate(line):
                # dots are empty space, so discard them
                # also discard hashes etc
                if not self.antenna_re.match(v):
                    continue

                self.frequency_lookup[v].append((x,y))

def accept_input():
    lines = []
    while True:
        try:
            line = input()
            lines.append(line)
        except EOFError:
            return Map(lines)

def part1(puzzle):
    return len(puzzle.get_antinodes(puzzle.get_antinodes_for_frequency_part1))

def part2(puzzle):
    return len(puzzle.get_antinodes(puzzle.get_antinodes_for_frequency_part2))

def main():
    puzzle = accept_input()
    print(f"Parsed: {puzzle.frequency_lookup}")
    print(f"Part 1: {part1(puzzle)}")
    print(f"Part 2: {part2(puzzle)}")

main()
