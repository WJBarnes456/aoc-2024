# also doing today in Python as I'm still in a rush


def accept_input():
    reports = []
    while True:
        try:
            line = input()
        except EOFError:
            return reports
       
        if not line:
            return reports
        reports.append([int(g) for g in line.split(' ')])

def is_change_unsafe(v1, v2, increasing):
        # using >= / <= here eliminates the difference = 0 case for us
    return (increasing and v2 <= v1) or (not increasing and v2 >= v1) or abs(v2 - v1) > 3
    

def is_report_safe_p1(report):
    current = report[0]
    increasing = (report[1] > report[0])
        
    for v in report[1:]:
        if is_change_unsafe(current, v, increasing):
            return 0
        current = v
    return 1

# this was my first approach, but I consistently got counts too low. the ones it failed on were where the first element was problematic, because that comparison would pass, and it'd only fail on the third comparison
# this implementation is also inefficient (we might check the start of the list three times) but at least linearly inefficient
def is_report_safe_p2_it(report):
    current = report[0]
    increasing = (report[1] > report[0])
    
    for (i,v) in enumerate(report[1:]):
        if is_change_unsafe(current, v, increasing):
            # the problematic element could be either of the two in this comparison
            # e.g. consider a list 10 1 2 3 4 5 - deleting the first element makes it safe
            report_discarded_current = report[:i] + report[i+1:]
            report_discarded_v = report[:i+1] + report[i+2:]
            #print(f"Discarding {current}, {v}; trying {report_discarded_current}, {report_discarded_v}")
            return (is_report_safe_p1(report_discarded_v) or is_report_safe_p1(report_discarded_current) or is_report_safe_p1(report[1:]))
        current = v
    return 1

def is_report_safe_p2(report):
    current = report[0]
    increasing = (report[1] > report[0])
    # this is worst-case quadratic in complexity but the lists are short enough for it to be computationally feasible
    for i in range(len(report)):
        if is_report_safe_p1(report[:i] + report[i+1:]):
            return 1
    return 0
       
def part1(reports):
    safe = [is_report_safe_p1(report) for report in reports]
    print(safe)
    return sum(safe)
    
def part2(reports):
    safe = [is_report_safe_p2_it(report) for report in reports]
    print(safe)
    return sum(safe)

def main():
    reports = accept_input()
    part1_result = part1(reports)
    print(f'Part 1 safe reports: {part1_result}')
    part2_result = part2(reports)
    print(f'Part 2 problem-dampened safe reports: {part2_result}')
    
    for report in reports:
        actually_safe = is_report_safe_p2(report) 
        iterative_safe = is_report_safe_p2_it(report)
        if actually_safe and not iterative_safe:
            print(f"Iterative method failed for {report}")
    
main()