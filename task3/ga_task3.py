import pygad
from utils import *
from collections import defaultdict
import math


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
    hours_per_teacher = [0]*len(problem.teacher_names)   #TASK 3, init hours for everyone to 0
    for i in range(len(sol_rooms)):
        room_groups[sol_rooms[i]].append((i, sol_start[i]))     #grouped by rooms for overlapping classes
        teacher_groups[sol_teachers[i]].append((i, sol_start[i]))   #grouped by teachers for teacher overbook
        hours_per_teacher[sol_teachers[i]] += problem.lectures[i][1]    #TASK 3, count teacher hours

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

#====================== TASK 3 penalties =========================================
    def interval_overlap(interval1, interval2):  #[start, end]
        return max(0, min(interval1[1], interval2[1])-max(interval1[0], interval2[0]))

    #DISLIKES LIKES
    soft_penalty_likes = 0
    total_duration = 0
    for i in range(len(sol_rooms)):
        teacher_prefs = problem.preferences.get(problem.teacher_names[sol_teachers[i]])
        duration = problem.lectures[i][1]
        total_duration += duration

        if teacher_prefs is None: 
            soft_penalty_likes += duration
            continue
        overlap_likes = interval_overlap(teacher_prefs[0], [sol_start[i], sol_start[i]+duration])
        overlap_dislikes = interval_overlap(teacher_prefs[1], [sol_start[i], sol_start[i]+duration])

        soft_penalty_likes += duration + overlap_dislikes - overlap_likes

    #BALANCE OF TEACHER SCHEDUELES
    if len(hours_per_teacher) <= 1 or total_duration == 0:
        soft_penalty_balance = 0
    else:
        entropy = -sum([
            (h / total_duration) * math.log(h/total_duration)
            for h in hours_per_teacher if h > 0     #log(0) je undefined
        ])
        soft_penalty_balance = 1 - entropy / math.log(len(hours_per_teacher))

    #===========================================
    return (
        1 / (1+penalty),
        1 / (1+soft_penalty_likes),
        1 / (1+soft_penalty_balance)
        )


#needed since pygad need exact function signature (ga_instance, solution, solution_idx)
def make_fitness(problem):      
    def fitness(ga_instance, solution, solution_idx):
        return fitness_func(solution, problem)
    return fitness

def make_run_ga(problem: Problem, *, 
                num_gen=100,
                num_par_mate=20,
                pop_size=50):

    best_valid_solution = {
        "solution": None,
        "fitness": None,
        "score": float("-inf")
    }

    def save_valid(ga_instance, population_fitness):
        for solution, fitness in zip(ga_instance.population, population_fitness):
            if fitness[0] != 1.0:     #fitness[0] is the hard penalty score (1 is perfrect). Needs to have a valid scheduele first
                continue

            score = (fitness[1]+fitness[2]) / 2 #equal weight for soft scores

            if score > best_valid_solution["score"]:
                best_valid_solution["solution"] = solution.copy()
                best_valid_solution["fitness"] = fitness.copy()
                best_valid_solution["score"] = score
    
    ga_instance = pygad.GA(
        fitness_func=make_fitness(problem),
        num_generations=num_gen,
        num_parents_mating=num_par_mate,
        sol_per_pop=pop_size,
        gene_type=int,
        gene_space=problem.gene_space,
        num_genes=3*len(problem.lectures),
        parent_selection_type="nsga2",   #this is necessary to work for fitness function returning multiple scores
        stop_criteria=None,     #Only num_generations stop learning, because we must not stop when schedule is valid but also preferences maxed
        on_fitness=save_valid,
    )

    ga_instance.run()

    save_valid(ga_instance, ga_instance.last_generation_fitness)    #save last generations as well

    return ga_instance, best_valid_solution
