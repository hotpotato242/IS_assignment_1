
import re, ast
from dataclasses import dataclass


class Problem:
    #describes the problem, should be read-only
    def __init__(self, classes, rooms, teachers):
        #returned from the parses
        self.classes = classes      
        self.rooms = rooms
        self.teachers = teachers

        self.lectures = [(c, d) for c, durs in classes.items() for d in durs]
        # list of lectures [("programming", 2), ...] (programming is 2 hours long)
        self.room_names = [k for k, _ in rooms.items()]
        self.teacher_names = [k for k, _ in teachers.items()]
        #get the room/teacher names respectivly

        self.gene_space = self.make_gene_space()

    def make_gene_space(self):
        space = []
        min_open = min(o for o, _ in self.rooms.values())
        max_close = max(c for _, c in self.rooms.values())
        for i in range(len(self.lectures)):
            space.append(list(range(len(self.room_names))))
            space.append(list(range(min_open, max_close)))           
            space.append(list(range(len(self.teacher_names))))

        return space

def read_lines(path):
    with open(path) as f:
        return [l.strip() for l in f if l.strip()]

def parse_classes(path):
    """returns dict of classes {string class name: array int [length of i-th class]}"""
    classes = {}
    for line in read_lines(path):
        name, rest = line.split("[", 1) 
        classes[name.strip().lower()] = ast.literal_eval("["+rest)

    return classes

def parse_rooms(path):
    """returns dict of classrooms {string classroom name: array int [free-at, free-until]}"""
    rooms = {}
    for line in read_lines(path):
        name, rest = line.split("[", 1)
        start, end = ast.literal_eval("[" + rest)
        rooms[name.strip()] = (start, end)
    return rooms

def parse_teachers(path):
    """returns dict of teachers {string teacher: array string [teachables]}"""
    teachers = {}
    for line in read_lines(path):
        name, rest = line.split("[", 1)
        subjects = [s.strip().lower() for s in rest.rstrip("]").split(",")]
        teachers[name.strip()] = subjects
    return teachers


# the information for the GA will be coded like:
# [room_0, start_0, teacher_0, room_1, start_1, teacher_1, ...]
# where the _i is the index of the lecture in lectures (name, duration) list
# room_i is the index of the room in room_names, start_i is the time of start (int), teacher_i is the index of the teacher in teacher_names
def decode(solution, problem: Problem):
    schedule = []
    for i, (cls, dur) in enumerate(problem.lectures):
        room = problem.room_names[int(solution[3*i])]
        start = int(solution[3*i+1])
        teacher = problem.teacher_names[int(solution[3*i+2])]
        schedule.append({"class": cls,
                         "classroom": room,
                         "start": start,
                         "end": start+dur,
                         "teacher": teacher})

    return schedule

def print_solution(solution, problem):
    schedule = decode(solution, problem)
    schedule.sort(key=lambda l: (l["classroom"], l["start"]))
    
    for s in schedule:
        print(f'{s["classroom"]:>6} {s["start"]:02d}:00-{s["end"]:02d}:00  '
              f'{s["class"]:<15} {s["teacher"]}')


