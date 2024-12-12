# core parts of the problem definition:
# > Plants of the same type can appear in multiple separate regions, and regions can even appear within other regions.
# i.e. we need to identify regions through some other means than just their letter

# we can do this by building a graph of plots, literally connecting them when they are adjacent
# each plot node can then be part of a broader matrix so we can connect them up and left as needed
# then we can sum region sizes and perimeters by going across the matrix, visiting each node and its neighbours to find the region, and multiplying them to get the price

class Plot:
    def exposed_sides(self):
        return 4 - len(self.neighbours)
    
    def __init__(self, plant_type):
        self.plant_type = plant_type
        self.neighbours = set()
    
    def __str__(self):
        return self.plant_type
    
    def add_neighbour(self, other_node):
        if self.plant_type == other_node.plant_type:
            self.neighbours.add(other_node)
    
    def _find_region(self, region):
        # to get a node's region, simply accumulate the set of itself, its neighbours, and all its neighbours' neighbours
        if self not in region:
            region.add(self)
            for neighbour in self.neighbours:
                neighbour._find_region(region)
        
        return region

    
    def get_region(self):
        return Region(self._find_region(set()))

class Region:
    def __init__(self, node_set):
        self.node_set = node_set
    
    def perimeter(self):
        return sum(plot.exposed_sides() for plot in self.node_set)
    
    def area(self):
        return len(self.node_set)


class Puzzle:
    def __init__(self, lines):
        self.matrix = []

        prev_row = None
        for line in lines:
            row = []
            left_plot = None
            for (j,v) in enumerate(line):
                plot = Plot(v)

                if left_plot is not None:
                    plot.add_neighbour(left_plot)
                    left_plot.add_neighbour(plot)

                if prev_row is not None:
                    up_plot = prev_row[j]
                    plot.add_neighbour(up_plot)
                    up_plot.add_neighbour(plot)
                
                left_plot = plot
                row.append(plot)

            self.matrix.append(row)
            prev_row = row
    
    def __str__(self):
        return "\n".join("".join(str(p) for p in line) for line in self.matrix) 
    
    def total_price(self):
        # only visit each node once, either as part of a region or at the top level
        visited_nodes = set()

        # consider every node at least once, by iterating over the map
        total_price = 0
        for row in self.matrix:
            for plot in row:
                if plot in visited_nodes:
                    continue

                # we've found an unvisited node, so now we want to visit its whole region
                region = plot.get_region()
                print(f"Region found: {[str(p) for p in region.node_set]}")

                # mark the whole region as visited so we don't consider it again
                visited_nodes = visited_nodes.union(region.node_set)

                # add the price
                total_price += region.area() * region.perimeter()
        
        return total_price


def accept_input():
    lines = []
    while True:
        try:
            lines.append(input())
        except EOFError:
            return Puzzle(lines)

def part1(puzzle):
    return puzzle.total_price()

def main():
    puzzle = accept_input()
    print(puzzle)
    print(f"Part 1: {part1(puzzle)}")

main()