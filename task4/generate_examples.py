# Generate input files for Tasks 1-4. Call generate_example() from a notebook.

from dataclasses import dataclass
import json
from pathlib import Path
import random


@dataclass
class Config:
    classes: int = 8
    rooms: int = 4
    teachers: int = 6
    lectures_per_class: int = 2
    min_duration: int = 1
    max_duration: int = 3
    day_length: int = 8                 # Hours are numbered from 0 to day_length.
    difficulty: str = "random"         # random / easy / hard / impossible
    preferences: bool = False
    seed: int | None = 42               # None gives a different example each time.


def generate_example(output_dir, config=None):
    """Write Classes.txt, Classrooms.txt, Teachers.txt and optional Preferences.txt.

    random: Independent room windows and teacher qualifications. A class may
            have no qualified teacher, so feasibility is unknown.
    easy:   Full-day rooms; every teacher can teach every class.
    hard:   Shorter room windows; each class has only one or two assigned teachers,
            plus any otherwise unused teachers given a subject afterward.
    impossible: Full-day rooms, but one lecture is longer than the entire day.
    """
    config = config if config is not None else Config()
    if config.difficulty not in ("random", "easy", "hard", "impossible"):
        raise ValueError("difficulty must be random, easy, hard or impossible.")
    output = Path(output_dir)
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise FileExistsError(f"Choose an empty or new output directory: {output}")

    rng = random.Random(config.seed)
    classes = {
        f"Class{i + 1}": [rng.randint(config.min_duration, config.max_duration)
                          for _ in range(config.lectures_per_class)]
        for i in range(config.classes)
    }
    class_names = list(classes)
    room_names = [f"Room{i + 1}" for i in range(config.rooms)]
    teacher_names = [f"Teacher{i + 1}" for i in range(config.teachers)]

    rooms = {}
    for room in room_names:
        if config.difficulty == "random":
            start = rng.randrange(config.day_length)
            end = rng.randint(start + 1, config.day_length)
        elif config.difficulty == "hard":
            length = rng.randint(max(1, config.day_length // 2), config.day_length)
            start = rng.randint(0, config.day_length - length)
            end = start + length
        else:
            start, end = 0, config.day_length
        rooms[room] = [start, end]

    if config.difficulty == "random":
        teachers = {
            teacher: rng.sample(class_names, rng.randint(1, config.classes))
            for teacher in teacher_names
        }
    elif config.difficulty == "hard":
        teachers = {teacher: [] for teacher in teacher_names}
        for subject in class_names:
            count = rng.randint(1, min(2, config.teachers))
            for teacher in rng.sample(teacher_names, count):
                teachers[teacher].append(subject)
        # Give unused teachers a subject too; every class still has coverage.
        for teacher in teacher_names:
            if not teachers[teacher]:
                teachers[teacher].append(rng.choice(class_names))
    else:
        teachers = {teacher: list(classes) for teacher in teacher_names}

    if config.difficulty == "impossible":
        # Intentionally exceeds max_duration if necessary to guarantee failure.
        classes["Class1"][0] = config.day_length + 1

    preferences = {}
    if config.preferences:
        if config.day_length < 2:
            raise ValueError("Teacher preferences require a day of at least 2 hours.")
        for teacher in teacher_names:
            # Choose disjoint intervals, with possible neutral hours around them.
            split = rng.randint(1, config.day_length - 1)
            first_start = rng.randrange(split)
            second_start = rng.randrange(split, config.day_length)
            windows = [[first_start, rng.randint(first_start + 1, split)],
                       [second_start, rng.randint(second_start + 1, config.day_length)]]
            rng.shuffle(windows)
            preferences[teacher] = {"likes": windows[0], "dislikes": windows[1]}

    files = {
        "Classes.txt": "".join(f"{name} {durations}\n"
                               for name, durations in classes.items()),
        "Classrooms.txt": "".join(f"{name} {hours}\n"
                                  for name, hours in rooms.items()),
        "Teachers.txt": "".join(f"{name} [{', '.join(subjects)}]\n"
                                for name, subjects in teachers.items()),
    }
    if config.preferences:
        files["Preferences.txt"] = "".join(
            f"{teacher} {json.dumps(pref)}\n" for teacher, pref in preferences.items()
        )

    output.mkdir(parents=True, exist_ok=True)
    for filename, content in files.items():
        with (output / filename).open("x", encoding="utf-8") as handle:
            handle.write(content)

    return {"classes": classes, "rooms": rooms,
            "teachers": teachers, "preferences": preferences}
