# at this rate I'm just doing the whole thing in Python....
# rough approach: accept the lines as input, then turn this into a graph where each node leads to its uphill neighbours
# because each path has a maximum length of 10, there's a fairly easy way of solving part 1 - simply do 10 iterations over the data, starting with just the 9s, and iterate back until you have 0s
# if we no longer require it to be uphill (maybe part 2?) then we want to instead spread outwards from the 9s until the entire graph is covered
# i.e. the 9s are already considered nodes, then you can proceed outwards by either DFS or BFS, ignoring any nodes from which that 9 was already reachable
# since there's a reasonable chance of this, let's define the problem such that we can change what makes nodes adjacent

from collections import deque

class Node:
    # because we flow from 9s outwards, each node's neighbour is downward only
    # we do both directions here so we only need to consider up and left when building the puzzle
    def add_relation(self, other_node):
        if self.height == (other_node.height - 1):
            other_node.leads_to.add(self)
         
        if other_node.height == (self.height - 1):
            self.leads_to.add(other_node)
    
    def score(self):
        return len(self.visible_9s)
    
    def __init__(self, height, position):
        self.visible_9s = set()
        self.leads_to = set()
        self.height = height
        self.rating = 0
        
        # we don't actually use this but it's very helpful for debugging
        self.position = position
    
    def __str__(self):
        return f"{self.height} {self.position} (rating: {self.rating})"

class Puzzle:
    def __str__(self):
        return f"Puzzle: peaks {[str(p) for p in self.peaks]}, trailheads {[str(th) for th in self.trailheads]}"
    
    def __init__(self, lines):
        self.peaks = set()
        self.trailheads = set()
        
        prev_row = None
        for (i, line) in enumerate(lines):
            node_row = []
            prev_node = None
            for (j, v) in enumerate(line):
                # catch invalid ints so we can use the impassable examples
                try:
                    node = Node(int(v), (j, i))
                    if node.height == 0:
                        self.trailheads.add(node)
                    elif node.height == 9:
                        self.peaks.add(node)
                except ValueError:
                    node_row.append(None)
                    prev_node = None
                    continue
                
                # do left-right relations (doesn't loop round the map so only needs to be )
                if prev_node is not None:
                    node.add_relation(prev_node)
                
                # do up-down relations
                if prev_row is not None:
                    up_node = prev_row[j]
                    if up_node is not None:
                        node.add_relation(up_node)
                
                node_row.append(node)
                prev_node = node
            prev_row = node_row
    
    def solve(self):
        # part 1: sum the score of every trailhead, so iterate from each peak until we've propagated it to every node that it could reach
        # I implemented this as a DFS rather than a BFS, but either's fine
        for peak in self.peaks:
            queue = [peak]
            while len(queue) > 0:
                node = queue.pop()
                print(f"Visiting {node} (leads to {[str(n) for n in node.leads_to]})")
                
                for candidate in node.leads_to:
                    if peak not in candidate.visible_9s:
                        candidate.visible_9s.add(peak)
                        queue.append(candidate)

        # part 2: sum the _rating_ of each trailhead, which you can do since each peak has a rating of 1, and when you BFS you visit the node of each level in turn
        # you could do this in a single pass by propagating the visible peaks at each step too, but it's easier to reason about doing it in two passes
        
        # start at all the peaks, which each only have one way to reach them
        queue = deque()
        for peak in self.peaks:
            peak.rating = 1
            queue.append(peak)
        
        # for every other node, their base rating is 0 (set in constructor), so we can simply add the currently-being-considered node's rating to it
        # starting from all the peaks means we can sum them in one fell swoop and know we've visited every outbound path from there already, i.e. we know it propagates safely
        # (wouldn't work if the adjacency relation weren't one-way)
        ever_queued_nodes = set()
        while len(queue) > 0:
            node = queue.popleft()
            print(f"Visiting {node} (rating leads to {[str(n) for n in node.leads_to]})")
            
            for candidate in node.leads_to:
                candidate.rating += node.rating
                if candidate not in ever_queued_nodes:
                    ever_queued_nodes.add(candidate)
                    queue.append(candidate)
def accept_input():
    lines = []
    while True:
        try:
            lines.append(input())
        except EOFError:
            return Puzzle(lines)

def part1(puzzle):
    total = 0
    for trailhead in puzzle.trailheads:
        th_score = trailhead.score()
        print(f"Trailhead {trailhead} has score {th_score}")
        total += th_score
    
    return total

def part2(puzzle):
    total = 0
    for trailhead in puzzle.trailheads:
        th_rating = trailhead.rating
        print(f"Trailhead {trailhead} has rating {th_rating}")
        total += th_rating
    
    return total

def main():
    puzzle = accept_input()
    puzzle.solve()
    print(f"Part 1: {part1(puzzle)}")
    print(f"Part 2: {part2(puzzle)}")

main()