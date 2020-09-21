import os, json
from models.planned_exercise import PlannedWorkout
from models.workout_program import WorkoutProgramModule, CompletedWorkoutSection, WorkoutExercise
from models.training_volume import Assignment, StandardErrorRange


def convert_planned_workout_to_completed(lib):
    # all_workouts = []
    if lib == 'NTC':
        base_path = 'libraries/workouts/'
    else:
        base_path = 'libraries/NRC_workouts/'
    dirs = os.listdir(base_path)
    for dir in dirs:
        if '.DS_' in dir:
            continue
        files = os.listdir(f"{base_path}/{dir}")
        for workout_file_name in files:
            if '.json' in workout_file_name:
                with open(f'{base_path}/{dir}/{workout_file_name}', 'r') as f:
                    json_data = json.load(f)
                    planned_workout = PlannedWorkout.json_deserialise(json_data)
                    completed_workout = convert_workout(planned_workout)
                    completed_workout_json = completed_workout.json_serialise()
                    write_json(completed_workout_json, workout_file_name, dir, lib)
                    # all_workouts.append(workout)
    # return all_workouts

def convert_assignment_or_ser_to_number(value):
    if value is not None:
        if isinstance(value, Assignment):
            if value.assigned_value is not None:
                return value.assigned_value
            elif value.min_value is not None and value.max_value is not None:
                return (value.min_value + value.max_value) / 2
            elif value.min_value is not None:
                return value.min_value
            elif value.max_value is not None:
                return value.max_value
            else:
                return None
        elif isinstance(value, StandardErrorRange):
            if value.observed_value is not None:
                return value.observed_value
            elif value.lower_bound is not None and value.upper_bound is not None:
                return (value.lower_bound + value.upper_bound) / 2
            elif value.lower_bound is not None:
                return value.lower_bound
            elif value.upper_bound is not None:
                return value.upper_bound
            else:
                return None

    return value


def write_json(workout, workout_name, directory, lib):
    json_string = json.dumps(workout, indent=4)
    full_dir_path = f"libraries/{lib}_completed/{directory}"
    file_name = os.path.join(full_dir_path, f"{workout_name}")
    if not os.path.exists(full_dir_path):
        os.makedirs(full_dir_path)
    print(f"writing: {file_name}")
    f1 = open(file_name, 'w')
    f1.write(json_string)
    f1.close()


def convert_workout(planned_workout):
    completed_workout = WorkoutProgramModule()
    completed_workout.name = planned_workout.name
    completed_workout.program_module_id = planned_workout.program_module_id
    completed_workout.program_id = planned_workout.program_id
    completed_workout.distance = convert_assignment_or_ser_to_number(planned_workout.distance)
    completed_workout.duration = convert_assignment_or_ser_to_number(planned_workout.duration)
    completed_workout.rpe = convert_assignment_or_ser_to_number(planned_workout.rpe)
    for planned_section in planned_workout.sections:
        completed_section = CompletedWorkoutSection()
        completed_section.name = planned_section.name
        completed_section.start_date_time = planned_section.start_date_time
        completed_section.duration_seconds = planned_section.duration_seconds
        completed_section.assess_load = planned_section.assess_load
        completed_workout.workout_sections.append(completed_section)
        for planned_exercise in planned_section.exercises:
            completed_exercise = WorkoutExercise()
            completed_exercise.id = planned_exercise.id
            completed_exercise.name = planned_exercise.name
            completed_exercise.movement_id = planned_exercise.movement_id
            completed_exercise.equipments = planned_exercise.equipments
            completed_exercise.name = planned_exercise.name
            completed_exercise.reps_per_set = convert_assignment_or_ser_to_number(planned_exercise.reps_per_set)
            completed_exercise.sets = planned_exercise.sets
            completed_exercise.distance = convert_assignment_or_ser_to_number(planned_exercise.distance)
            completed_exercise.duration = convert_assignment_or_ser_to_number(planned_exercise.duration)
            completed_exercise.weight = convert_assignment_or_ser_to_number(planned_exercise.weight)
            completed_exercise.weight_measure = planned_exercise.weight_measure
            completed_exercise.grade = convert_assignment_or_ser_to_number(planned_exercise.grade)
            completed_exercise.rpe = planned_exercise.rpe
            completed_exercise.pace = convert_assignment_or_ser_to_number(planned_exercise.pace)
            completed_exercise.speed = convert_assignment_or_ser_to_number(planned_exercise.speed)
            completed_exercise.stroke_rate = convert_assignment_or_ser_to_number(planned_exercise.stroke_rate)
            completed_exercise.cadence = convert_assignment_or_ser_to_number(planned_exercise.cadence)
            completed_exercise.power = convert_assignment_or_ser_to_number(planned_exercise.power)
            completed_exercise.calories = convert_assignment_or_ser_to_number(planned_exercise.calories)
            completed_section.exercises.append(completed_exercise)

    return completed_workout

if __name__ == '__main__':
    for lib in ['NTC', 'NRC']:
        convert_planned_workout_to_completed(lib)
