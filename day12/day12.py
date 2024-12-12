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

        self.neighbours = {}
    
    def __str__(self):
        return self.plant_type
    
    def add_neighbour(self, direction, other_node):
        if self.plant_type == other_node.plant_type:
            self.neighbours[direction] = other_node
    
    def _find_region(self, region):
        # to get a node's region, simply accumulate the set of itself, its neighbours, and all its neighbours' neighbours
        if self not in region:
            region.add(self)
            for neighbour in self.neighbours.values():
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
    
    def count_sides_from(self, start_node, direction, visited):
        # assert that the provided direction is a normal
        if direction in start_node.neighbours:
            return 0
        
        # don't walk around a side we already walked
        # we could trade time for memory by only storing the start node/directions and only giving up when we hit them
        # memory goes from O(number of nodes) to O(number of sides), and time goes up to O(number of nodes^2) given the worst case of a line of nodes of the same type
        if (start_node, direction) in visited:
            return 0

        # now we can walk around the edge of this side

        # if you're wondering why the comments are weird, I started by writing the comments first and turning it into code later
        # call the direction we got here in the "normal direction" (originally derived since we just iterated that way til we hit a side)
        normal = direction

        clockwise_direction = {'u' : 'r', 'r' : 'd', 'd' : 'l', 'l' : 'u'}
        # pick a perpendicular direction to move in (whether we're doing a clockwise or counterclockwise traversal. I'm going oldschool)
        travel = clockwise_direction[normal]

        opposite_direction = {'u' : 'd', 'd' : 'u', 'l' : 'r', 'r' : 'l'}

        # until we end up at the original node...
        node = start_node
        back_at_start = False
        sides = 0
        while not back_at_start:
            visited.add((node, normal))
            # one of these cases is true:
            if travel in node.neighbours:
                travel_node = node.neighbours[travel]
                
                # - there is a node in that direction, and a node in the normal direction.
                if normal in travel_node.neighbours:
                    # this is a concave corner. add to the count, set the normal direction to the opposite of the direction of travel, set the direction of travel to the old normal direction, and move to that new node
                    # note that it has to be empty space since the new travel node's normal points into the same empty square as the original node's normal
                    node = travel_node.neighbours[normal]

                    sides += 1
                    (normal, travel) = opposite_direction[travel], normal
                else:
                    # - there is a node in that direction, and no node in the normal direction. this is the same side, do not add to the count and just move to that node
                    node = travel_node
            else:
                # - there is no node in that direction. this is a convex corner. add to the count, rotate around but stay on the same node
                sides += 1
                (normal, travel) = travel, opposite_direction[normal]
            
            # when we get back to the original node facing the same way, then we're done. we already counted that side when we hit the corner, so no need to add to the count
            back_at_start = (node == start_node) and normal == direction
        
        return sides

    def side_count(self):
        # the example where the shape has both an inside and an outside is tricky, but it's fine - we just need to make sure that we consider every position where a side might start

        # consider all nodes in the region - we'll visit each external facing component once, so if it's already in the visited set we'll ignore it (see above)
        visited = set()
        total_sides = 0
        for node in self.node_set:
            for direction in "udlr":
                total_sides += self.count_sides_from(node, direction, visited)

        return total_sides


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
                    plot.add_neighbour('l', left_plot)
                    left_plot.add_neighbour('r', plot)

                if prev_row is not None:
                    up_plot = prev_row[j]
                    plot.add_neighbour('u', up_plot)
                    up_plot.add_neighbour('d', plot)
                
                left_plot = plot
                row.append(plot)

            self.matrix.append(row)
            prev_row = row
    
    def __str__(self):
        return "\n".join("".join(str(p) for p in line) for line in self.matrix)

    def get_regions(self):
        # to find the regions, iterate over the matrix and extract them
        visited_nodes = set()

        regions = set()        
        for row in self.matrix:
            for plot in row:
                if plot in visited_nodes:
                    continue

                # we've found an unvisited node, so now we want to visit its whole region
                region = plot.get_region()
                print(f"Region found: {[str(p) for p in region.node_set]}")
                regions.add(region)

                # mark the whole region as visited so we don't consider it again
                visited_nodes = visited_nodes.union(region.node_set)
        
        return regions

    
    def total_price(self): 
        return sum(region.area() * region.perimeter() for region in self.get_regions())
    
    def bulk_discount(self):
        return sum(region.area() * region.side_count() for region in self.get_regions())


def accept_input():
    lines = []
    while True:
        try:
            lines.append(input())
        except EOFError:
            return Puzzle(lines)

def part1(puzzle):
    return puzzle.total_price()

def part2(puzzle):
    return puzzle.bulk_discount()

def main():
    puzzle = accept_input()
    print(puzzle)
    print(f"Part 1: {part1(puzzle)}")
    print(f"Part 2: {part2(puzzle)}")

main()