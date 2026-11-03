from utils import *
import numpy as np
import random as rd



def improve_initial_pop(problem, pop_size=50):

    population=[]

    for i in range(pop_size):
        pop=make_solution(problem)
        population.append(pop)

    return np.array(population)


def make_solution(problem):
    solution = [None] * (3*len(problem.lectures))

    

    #track occupied intervals
    teacher_free = {teacher: [] for teacher in problem.teacher_names}
    classroom_free = {classroom: [] for classroom in problem.room_names}
    #shuffle lectures
    lectures = list(enumerate(problem.lectures))
    rd.shuffle(lectures)

    for idx, lct in lectures:
        eligible_teacher = [
            tch for tch in problem.teacher_names
            if lct[0] in problem.teachers[tch]
        ]
        rd.shuffle(eligible_teacher)

        available_rooms = problem.room_names.copy()
        rd.shuffle(available_rooms)

        flag = False

        for room in available_rooms:
            free_intervals_room = get_free_intervals_room(problem, room, classroom_free[room])

            for teacher in eligible_teacher:
                free_intervals_tch = get_free_intervals_teacher(problem, teacher, teacher_free[teacher])

                good_intervals = intersection_of_intervals(free_intervals_room, free_intervals_tch)

                #find the shortest interval that fits the lecture
                min_interval = None
                min_interval_length = 24

                for interval in good_intervals:
                    interval_length = interval[1] - interval[0]

                    if interval_length >= lct[1] and interval_length < min_interval_length:
                        min_interval_length = interval_length
                        min_interval = interval

                if min_interval is not None:
                    start = min_interval[0]
                    end = start + lct[1]

                    #update occupied intervals
                    classroom_free[room].append((start, end))
                    teacher_free[teacher].append((start, end))

                    solution[3*idx] = problem.room_names.index(room)
                    solution[3*idx+1] = start
                    solution[3*idx+2] = problem.teacher_names.index(teacher)

                    flag = True
                    break

            if flag:
                break

        if not flag:
            #pregled vseh moznih ucilnic, uciteljev za predavanja je prevec casovno potratno
            # zatorej raje nekaj random ucilnic, nekaj random uciteljev in dodas tistega z najmanjso napako
            
            rnd_rooms=rd.sample(problem.room_names, min(5, len(problem.room_names)))
            rnd_tch=rd.sample(eligible_teacher, min(5, len(eligible_teacher)))
            if not eligible_teacher:
                rnd_tch=rd.sample(problem.teacher_names,min(5,len(problem.teacher_names)))
            possible_hours=list(range(5,21))
            rnd_hours=rd.sample(possible_hours,5)
            min_penalty=0#it can be a value from 0 to 1, we want as high as possible
            rnd_choice_room=rnd_rooms[0]
            rnd_choice_tch=rnd_tch[0]
            rnd_choice_hour=rnd_hours[0]
            for r in rnd_rooms:
                for t in rnd_tch:
                    for h in rnd_hours:
                        pen=penalty_calculation(problem,lct,r,t,h,classroom_free,teacher_free)
                        if pen>min_penalty:
                            min_penalty=pen
                            rnd_choice_room=r
                            rnd_choice_tch=t
                            rnd_choice_hour=h
            #adding the one with the lowest penalty
            r=rnd_choice_room
            t=rnd_choice_tch
            h=rnd_choice_hour
            end = h + lct[1]
            classroom_free[r].append((h, end))
            teacher_free[t].append((h, end))
            solution[3*idx] = problem.room_names.index(r)
            solution[3*idx+1] = h
            solution[3*idx+2] = problem.teacher_names.index(t)


    return solution


def penalty_calculation(problem,lct,r,t,h,classroom_free,teacher_free):
    penalty = 0
    duration = lct[1]
    end = h+duration

    #prosta soba?
    room_start, room_end = problem.rooms[r]

    penalty += max(room_start-h, 0)
    penalty += max(end-room_end, 0)

    #ali se prekrivajo termini sob?
    for start, finish in classroom_free[r]:
        if h < finish and end > start:
            penalty += min(end, finish)-max(h, start)

    #ali se prekrivajo termini profesorjev?
    for start, finish in teacher_free[t]:
        if h < finish and end > start:
            penalty += min(end, finish)-max(h, start)

    #ali so profesorji usposobljeni za ta predmet?
    if lct[0] not in problem.teachers[t]:
        penalty += 5

    return 1 / (1+penalty)

def get_free_intervals_room(problem, room, dic):
    rooms_start, room_end = problem.rooms[room]
    occupied = sorted(dic, key=lambda x: x[0])
    free_intervals = [[rooms_start, room_end]]

    for occupied_start, occupied_end in occupied:
        new_free_intervals = []

        for free_start, free_end in free_intervals:
            #ni prekrivanja
            if occupied_end <= free_start or occupied_start >= free_end:
                new_free_intervals.append([free_start, free_end])
            else:
                #prosti del pred zasedenim intervalom
                if free_start < occupied_start:
                    new_free_intervals.append([free_start, occupied_start])

                #prosti del za zasedenim intervalom
                if occupied_end < free_end:
                    new_free_intervals.append([occupied_end, free_end])

        free_intervals = new_free_intervals

    return free_intervals



def get_free_intervals_teacher(problem, tch, dic):
    occupied=sorted(dic,key=lambda x: x[0])
    #neke smiselne zacetne vrednosti
    free_intervals=[[5,21]]
    for occupied_start, occupied_end in occupied:
            new_free_intervals = []
    
            for free_start, free_end in free_intervals:
                #ni prekrivanja
                if occupied_end <= free_start or occupied_start >= free_end:
                    new_free_intervals.append([free_start, free_end])
                else:
                    #prosti del pred zasedenim intervalom
                    if free_start < occupied_start:
                        new_free_intervals.append([free_start, occupied_start])
    
                    #prosti del za zasedenim intervalom
                    if occupied_end < free_end:
                        new_free_intervals.append([occupied_end, free_end])
    
            free_intervals = new_free_intervals
    
    return free_intervals


def intersection_of_intervals(free_room, free_tch):
    intersection=[]

    for free_room_start, free_room_end in free_room:
        for free_tch_start, free_tch_end in free_tch:

            start=max(free_room_start, free_tch_start)
            end=min(free_room_end, free_tch_end)

            if start<end:
                intersection.append([start, end])

    return intersection
