class File:
    # represent free space as a "file" with None id
    def is_free(self):
        return self.file_id is None
    
    def id(self):
        return file_id
        
    def __init__(self, file_id, length):
        self.file_id = file_id
        self.length = length
    
    def __str__(self):
        c = str(self.file_id)
        if self.file_id is None:
            c = '.'
        
        return c * self.length

def files_from_string(file_st):
    files = []
    current_id = 0
    free_space = False
    
    # flip between free_space and not
    for c in file_st:
        length = int(c)
        if free_space:
            next_file = File(None, length)
        else:
            next_file = File(current_id, length)
            current_id += 1
        
        # micro-optimisation - don't bother appending files with 0 length
        if length != 0:
            files.append(next_file)
            
        free_space ^= True
    
    return files

def accept_input():
    line = input()
    return files_from_string(line)

# you can do part1 without needing to ever expand the representation - have two pointers, one walking the list of files left to right and the other right to left
# left to right one - add when you see actual files, and pull from the right hand side when you're on empty space
# right to left one - skip empty space, and just return the relevant amount
# need to be careful when they eventually end up pointing at the same file so that we don't end up overstepping the total length
def part1(files, debug = False):
    left_index = 0
    right_index = len(files)-1
    right_blocks_taken = 0
    
    current_pos = 0
    count = 0
    
    if debug:
        serialised_file = ""
    
    while left_index != right_index:
        left_file = files[left_index]
        
        # if the left file is a real file - pull it into the checksum
        if left_file.file_id is not None:
            for i in range(left_file.length):
                if debug:
                    serialised_file += str(left_file.file_id)
                
                count += current_pos * left_file.file_id
                current_pos += 1
            left_index += 1
            continue
        
        # if the left file is empty space - pull from the right hand side instead
        # you could special case the left hand empty space being larger than the right hand file but it's safer to just treat it as one case
        # (consider the edge case where we're using parts of an already-partially-consumed file)
        # nb. we don't need to worry about the left hand empty space somehow being the same as the right hand non-empty file, since by definition it means we've ended up on an empty space
        
        # loop invariant - we're pointing at a file with length > right_blocks_taken
        for i in range(left_file.length):
            # skip empty space with the right hand pointer - we need an actual file to pull from
            while files[right_index].file_id is None:
                # edge case - if we end up hitting the very same empty space, it means we've hit the end of the file!
                if right_index == left_index:
                    if debug:
                        print(serialised_file)
                    return count
                right_index -= 1
            
            # we're now pointing at an actual file which still has blocks available, so take a block from it
            right_file = files[right_index]
            if debug:
                serialised_file += str(right_file.file_id)
            count += current_pos * right_file.file_id
            current_pos += 1
            right_blocks_taken += 1
            
            # if we just depleted the file, step to the previous one
            if right_blocks_taken == right_file.length:
                right_index -= 1
                right_blocks_taken = 0
        
        left_index += 1
    
    # we've hit an edge case - both the left index and the right index point at the same file
   
    last_file = files[left_index]
    # if it's empty space, we're finished
    if last_file.file_id is not None:
        # the right index may have already taken some value off of this, so we can do it as just one for loop...
        for i in range(last_file.length - right_blocks_taken):
            if debug:
                serialised_file += str(last_file.file_id)
            count += current_pos * last_file.file_id
            current_pos += 1
    
    if debug:
        print(serialised_file)
        
    return count

# I learned while implementing part1 that it is actually possible to serialise the file; if I were implementing this I would've been annoying
# however part2 is a really natural fit to the representation I'm using as it's possible to simply splice the file into the free space
def part2(files, debug = False):
    # in order to modify the unconsidered files underneath us without breaking things
    # treat the list of files as a stack where we only finalise stuff once we've hit it from the right hand side
    rev_considered_files = []
    while len(files) > 0:
        right_file = files.pop()
        
        # if it's empty space, we can't do anything with it, just chuck it on the considered file list
        if right_file.is_free():
            rev_considered_files.append(right_file)
            continue
        
        # it's an actual file, so consider candidates to the left
        spliced = False
        for (i, left_file) in enumerate(files):
            # can't splice into used space
            if not left_file.is_free():
                continue
            
            # can't splice into empty space smaller than the file
            if left_file.length < right_file.length:
                continue
                
            # we've found an empty space we can splice into!
            # the splicing operation has two steps:
            
            # free up the right file's space (replacing where it was with empty space)
            # we could coalesce this with adjacent empty space to avoid creating new files, but this is at worst a doubling and free files can be done in 0 time
            rev_considered_files.append(File(None, right_file.length))
            
            # splice the right file into where the left file currently is
            gap_length = left_file.length - right_file.length
            left_file.file_id = right_file.file_id
            left_file.length = right_file.length
            
            # add the new empty space to the file list
            if gap_length > 0:
                files = files[:i+1] + [File(None, gap_length)] + files[i+1:]
                if debug:
                    print("".join(str(f) for f in files))
            
            spliced = True
            break
        
        # we failed to splice, so just add to the list
        if not spliced:
            rev_considered_files.append(right_file)
    
    # we've now reordered the files, so we can just compute the checksum
    # no need for clever logic here, just sum it up
    count = 0
    current_pos = 0
    for file in reversed(rev_considered_files):
        if file.is_free():
            current_pos += file.length
            continue
        
        # file is not free, so add it. I could write this out directly, but as the maximum file length is 9 it's easier just to do as a for loop
        for i in range(file.length):
            count += file.file_id * current_pos
            current_pos+=1
    return count 
    

def main():
    files = accept_input()
    print([str(f) for f in files])
    print(f"Part 1: {part1(files)}")
    print(f"Part 2: {part2(files)}")

main()