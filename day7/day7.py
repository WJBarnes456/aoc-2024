# we're using Python again, again because I have other things that I'd like to get done before setting a proper test harness up

from math import log10, floor

class Equation:
    def __init__(self, target, vals):
        self.target = target
        self.vals = vals

    def __str__(self):
        return f"{self.target}: {' '.join(str(v) for v in self.vals)}"

    # this solution is nice, but isn't the problem being asked here. the problem is not (solve the two equations and concat them), it's concatting the underlying operators i.e. can be done at the lowest level
    def could_be_true_with_top_level_concats(self):
        # key observation: concatenations can't work for subproblems, they can only work at the top level
        # i.e. you add a single multiplicative factor doing this

        # base case, if the equation itself is true, then it's true with concats too
        if self.could_be_true():
            return True

        # decomposition: if the equation with a concat at some point is then true with concats, then it is also true
        target_st = str(self.target)
        for i in range(1, len(target_st)):
            first_half = int(target_st[:i])
            second_half = int(target_st[i:])
            print(f"decomposing {self.target} into {first_half} || {second_half}")
            # now you need to iterate through the vals list to figure out the corresponding list
            for j in range(1,len(self.vals)):
                first_half_vals = self.vals[:j]
                second_half_vals = self.vals[j:]

                print(f"trying to make ({first_half}, {second_half}) with ({first_half_vals}, {second_half_vals})")
                if Equation(first_half, first_half_vals).could_be_true_with_concats() and  Equation(second_half, second_half_vals).could_be_true_with_concats():
                    return True
        return False

    # this solution is _also_ nice, but again isn't the problem being asked here
    # I should've checked the 7290 example - 6 * 8 || 6 * 15 is evaluated left to right, then the append is made to it
    def could_be_true_with_bottom_level_concats(self):
            # base case, if the equation itself is true, then it's true with concats too
            if self.could_be_true():
                return True
            else:
                print(f"Cannot make {self.target} with {self.vals}")

            # otherwise, the target is the same, but you can concatenate the values instead
            for i in range(1, len(self.vals)):
                # try merging element i-1 with element i, and solving that equation
                new_vals = self.vals[:(i-1)] + [int(str(self.vals[i-1]) + str(self.vals[i]))] + self.vals[(i+1):]
                print(f"Trying to make {self.target} with {new_vals}")
                if Equation(self.target, new_vals).could_be_true_with_concats():
                    return True

            return False

    # the real solution (e.g. 7290 = 6 * 8 || 6 * 15) is made by concatenation _to the result so far_, i.e. multiplying by 10 ^ ceil log10 of the next digit and adding that digit
    # this vastly raises the max value possible making that heuristic much less useful
    def could_be_true_with_concats(self):
        # base case: if there is only one value and that is the target, then it is true
        # NB: might need to consider the empty equation equalling zero, but the spec doesn't clarify that
        if len(self.vals) == 1:
            return self.vals[0] == self.target
        # as the product of two integers is always greater than or equal to their sum for a,b >=2, the largest possible result is adding ones across the smallest numbers in the values, and taking the product of the rest
        # > Furthermore, numbers in the equations cannot be rearranged

        # minimum value - multiply by ones and add everything else
        # as the concat operation is always at least a multiplication by 10 there's no way it can ever be smaller
        min_value = 0
        for v in self.vals:
            if v < 2:
                min_value *= v
            else:
                min_value += v

        if self.target < min_value:
            print(f"Rejecting: minimum value for {self.vals} ({min_value}) less than {self.target}")
            return False

        # maximum value - now easier to calculate by just calculating all three and picking the biggest
        max_value = 1
        for v in self.vals:
            max_value = max(max_value + v, max_value * v, int(str(max_value) + str(v)))

        if self.target > max_value:
            print(f"Rejecting: maximum possible value for {self.vals} ({max_value}) is less than {self.target}")
            return False

        # the target is in the plausible range, so it makes sense to search for operators which might satisfy it
        # like the normal one, solve this recursively by adding another case to the heuristic - since concat is equivalent to subtraction then division by ceil(log10(v)), we can attempt this first as again it reduces the value the most
        last = self.vals[-1]
        tail = self.vals[:-1]

        concat_cand = self.target - last
        concat_mult = (10**floor(log10(last)+1))
        print(f"{concat_cand}, {concat_mult}")
        return (concat_cand % concat_mult == 0 and Equation(concat_cand // concat_mult, tail).could_be_true_with_concats()) or (self.target % last == 0 and Equation(self.target / last, tail).could_be_true_with_concats()) or Equation(self.target - last, tail).could_be_true_with_concats()

    def could_be_true(self):
        # base case: if there is only one value and that is the target, then it is true
        # NB: might need to consider the empty equation equalling zero, but the spec doesn't clarify that
        if len(self.vals) == 1:
            return self.vals[0] == self.target
        # as the product of two integers is always greater than or equal to their sum for a,b >=2, the largest possible result is adding ones across the smallest numbers in the values, and taking the product of the rest
        # > Furthermore, numbers in the equations cannot be rearranged

        # minimum value - multiply by ones and add everything else
        min_value = 0
        for v in self.vals:
            if v < 2:
                min_value *= v
            else:
                min_value += v

        if self.target < min_value:
            print(f"Rejecting: minimum value for {self.vals} ({min_value}) less than {self.target}")
            return False

        # maximum value - add ones and multiply by everything else
        max_value = 1
        for v in self.vals:
            if v < 2:
                max_value += v
            else:
                max_value *= v
        if self.target > max_value:
            print(f"Rejecting: maximum possible value for {self.vals} ({max_value}) is less than {self.target}")
            return False

        # the target is in the plausible range, so it makes sense to search for operators which might satisfy it
        # we can solve this recursively, using a heuristic - if the target is divisible by the value at the tail of the list, try that (brings the value down as much as possible), or sum and rely on the sum base case to stop things getting too small
        last = self.vals[-1]
        tail = self.vals[:-1]
        return (self.target % last == 0 and Equation(self.target / last, tail).could_be_true()) or Equation(self.target - last, tail).could_be_true()

def accept_input():
    equations = []
    while True:
        try:
            line = input()
            line_parts = line.split(' ')
            target = int(line_parts[0][:-1])
            values = [int(v) for v in line_parts[1:]]
            equations.append(Equation(target, values))
        except EOFError:
            return equations

def part1(equations):
    return sum(e.target for e in equations if e.could_be_true())

def part2(equations):
    return sum(e.target for e in equations if e.could_be_true_with_concats())

def main():
    equations = accept_input()
    print(f"Equations: {[str(e) for e in equations]}")
    print(f"Part 1: {part1(equations)}")
    print(f"Part 2: {part2(equations)}")

main()
