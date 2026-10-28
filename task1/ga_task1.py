import pygad
from utils import *
from collections import defaultdict


# fitness func necessities
# penalize: overlapping classes in same room, class out of correct time
# teacher overbook, 

# room, start, teacher

def fitness_func(solution: list[int], problem: Problem):
    penalty = 0

    sol_rooms = [solution[3*i] for i in range(len(solution)//3)]
    sol_start = [solution[3*i +1] for i in range(len(solution)//3)]
    sol_teachers = [solution[3*i +2] for i in range(len(solution)//3)]

    room_groups = defaultdict(list)     #default dict so it doesnt raise KeyError on first entry
    teacher_groups = defaultdict(list)
    for i in range(len(sol_rooms)):
        room_groups[sol_rooms[i]].append((i, sol_start[i])) 
        #grouped by rooms for overlapping classes
        teacher_groups[sol_teachers[i]].append((i, sol_start[i]))
        #grouped by teachers for teacher overbook

    def helper_overlap_pens(group):     #same overlap algo used for rooms overlapping and teachers classes overlapping
        pen = 0
        for _, starts_list in group.items():
            intervals = []
            for (i, start) in starts_list:
                duration = problem.lectures[i][1]
                intervals.append([start, start+duration])

            intervals.sort(key= lambda l: (l[0], l[1])) #sort by start first, then end times
            max_end = intervals[0][1]
            for s, e in intervals[1:]: #start, end
                if s < max_end:
                    pen += min(e, max_end) - s   # overlapping hours with the running block
                max_end = max(max_end, e)

        return pen

    penalty += helper_overlap_pens(room_groups) #ovelap in room
    penalty += helper_overlap_pens(teacher_groups) #overlap in teachers scheduele

    #class out of correct time
    for room, lecture_per_group in room_groups.items():
        for (i, start) in lecture_per_group:
            duration = problem.lectures[i][1]
            to_soon = start-problem.rooms[problem.room_names[room]][0]
            to_late = (start+duration) - problem.rooms[problem.room_names[room]][1]
            penalty += max(-to_soon, 0) + max(to_late, 0)

    for i in range(len(sol_teachers)):
        cls = problem.lectures[i][0]
        if cls not in problem.teachers[problem.teacher_names[sol_teachers[i]]]:
            penalty += 5#larger than just 1 for hour since its a bigger mistake

    return 1 / (1+penalty)


#needed since pygad need exact function signature (ga_instance, solution, solution_idx)
def make_fitness(problem):      
    def fitness(ga_instance, solution, solution_idx):
        return fitness_func(solution, problem)
    return fitness

def make_run_ga(problem: Problem, *, 
                num_gen=100,
                num_par_mate=20,
                pop_size=50):
    ga_instance = pygad.GA(
        fitness_func=make_fitness(problem),
        num_generations=num_gen,
        num_parents_mating=num_par_mate,
        sol_per_pop=pop_size,
        gene_type=int,
        gene_space=problem.gene_space,
        stop_criteria="reach_1.0",
        num_genes=3*len(problem.lectures)
    )

    ga_instance.run()

    return ga_instance    
