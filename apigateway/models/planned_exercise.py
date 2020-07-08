from utils import format_date, parse_date
from models.movement_tags import CardioAction, Equipment
from models.workout_program import WorkoutSection, BaseWorkoutExercise, ExerciseAction
from models.training_volume import StandardErrorRange, Assignment, MovementOption
from models.exercise import UnitOfMeasure, WeightMeasure
from serialisable import Serialisable


class PlannedWorkout(object):
    def __init__(self):
        self.name = ""
        self.program_id = None
        self.program_module_id = None
        self.event_date = None  # date for which this is planned
        self.duration = ""
        self.sections = []

    def json_serialise(self):
        ret = {
            'name': self.name,
            'event_date': format_date(self.event_date),
            'program_id': self.program_id,
            'program_module_id': self.program_module_id,
            'duration': self.duration,
            'sections': [s.json_serialise() for s in self.sections]
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        workout = cls()
        workout.name = input_dict.get('name')
        workout.event_date = parse_date(input_dict.get('event_date')) if input_dict.get('event_date') is not None else None
        workout.program_id = input_dict.get('program_id')
        workout.program_module_id = input_dict.get('program_module_id')
        workout.duration = input_dict.get('duration')
        workout.sections = [PlannedWorkoutSection.json_deserialise(section) for section in input_dict.get('sections', [])]

        return workout


# class PlannedSection(object):
#     def __init__(self):
#         self.name = ""
#         self.start_time = None  # relative time in seconds from start of the workout
#         self.duration = None
#         self.exercises = []

class PlannedWorkoutSection(WorkoutSection, Serialisable):
    def __init__(self):
        super().__init__()

    def json_serialise(self):
        ret = {
            'name': self.name,
            'start_date_time': self.start_date_time,
            'duration_seconds': self.duration_seconds,
            'exercises': [e.json_serialise() for e in self.exercises]
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        workout_section = cls()
        workout_section.name = input_dict.get('name')
        workout_section.start_date_time = input_dict.get('start_date_time')
        workout_section.duration_seconds = input_dict.get('duration_seconds')
        workout_section.exercises = [PlannedExercise.json_deserialise(workout_exercise) for workout_exercise in
                                     input_dict.get('exercises', [])]

        return workout_section


class PlannedExercise(BaseWorkoutExercise):
    def __init__(self):
        super().__init__()

        self.weight = None  # in lbs
        self.weight_measure = None

        self.reps = 1
        self.prescribed_per_side = False  # if the prescribed dosage is per side or total
        self.tempo = None  # OTF defines tempo for concentric/eccentric part of movement

        # primary assignments
        self.duration = None
        self.distance = None
        self.pace = None
        self.speed = None
        #self.grade = Assignment()
        self.grade = Assignment(assigned_value=0.0)
        self.cadence = None
        #self.stroke_rate = Assignment()
        self.stroke_rate = None

        # alternate assignments
        self.alternate_distance = []  # will be a list of Assignment objects
        self.alternate_duration = []  # will be a list of Assignment objects
        self.alternate_pace = []  # will be a list of Assignment objects
        self.alternate_speed = []  # will be a list of Assignment objects
        self.alternate_grade = []  # will be a list of Assignment objects
        self.alternate_cadence = []  # will be a list of Assignment objects
        self.alternate_stroke_rate = []  # will be a list of Assignment objects

        self.alternate_movement_ids = []

        self.stroke_adjustment = 0  # how much lower than your base stroke rate

        self.force = None
        self.power = None
        self.power_goal = None # average power goal for exercise
        # self.power_above_base = None  # e.g OTF defines as all_out as 50Watts above base, do not need to store
        # Note that the rule-of-thumb base power is your bodyweight in lbs

        self.calories = None  # calorie goal for exercise

        self.maximal_intensity = False  # Potentially use this in calculating HRMax, VO2Max etc

        self.total_volume = None
        # only need this to set default values. So, possibly need it in spreadsheet but not stored
        # self.intensity = None  # e.g. base/push/all_out for OTF, potentially used to determine pace,watts etc e.g. rowing all out power is base + 50 or more

    def json_serialise(self):
        ret = {
            'id': self.id,
            'name': self.name,
            'equipments': [equipment.value for equipment in self.equipments],
            'movement_id': self.movement_id,
            'weight': self.weight,
            'weight_measure': self.weight_measure.value if self.weight_measure is not None else None,
            'side': self.side,
            'reps': self.reps,

            'sets': self.sets,
            'reps_per_set': self.reps_per_set,
            'unit_of_measure': self.unit_of_measure.value if self.unit_of_measure is not None else None,
            'rpe': self.rpe.json_serialise() if self.rpe is not None else None,

            'predicted_rpe': self.predicted_rpe,

            'prescribed_per_side': self.prescribed_per_side,
            'tempo': self.tempo,
            'explosiveness_rating': self.explosiveness_rating,
            'duration': self.duration.json_serialise() if self.duration is not None else None,
            'distance': self.distance.json_serialise() if self.distance is not None else None,
            'pace': self.pace.json_serialise() if self.pace is not None else None,
            'speed': self.speed.json_serialise() if self.speed is not None else None,
            'grade': self.grade.json_serialise(),
            'cadence': self.cadence.json_serialise() if self.cadence is not None else None,
            #'stroke_rate': self.stroke_rate.json_serialise(),
            'stroke_rate': self.stroke_rate if self.stroke_rate is not None else None,

            'alternate_duration': [duration.json_serialise() for duration in self.alternate_duration],
            'alternate_distance': [distance.json_serialise() for distance in self.alternate_distance],
            'alternate_pace': [pace.json_serialise() for pace in self.alternate_pace],
            'alternate_speed': [speed.json_serialise() for speed in self.alternate_speed],
            'alternate_grade': [grade.json_serialise() for grade in self.alternate_grade],
            'alternate_cadence': [cadence.json_serialise() for cadence in self.alternate_cadence],
            'alternate_stroke_rate': [stroke_rate.json_serialise() for stroke_rate in self.alternate_stroke_rate],
            'alternate_movement_ids': [movement_id.json_serialise() for movement_id in self.alternate_movement_ids],

            'stroke_adjustment': self.stroke_adjustment,
            'power_goal': self.power_goal,
            'force': self.force.json_serialise() if self.force is not None else None,
            'power': self.power.json_serialise() if self.power is not None else None,
            'calories': self.calories,
            'maximal_intensity': self.maximal_intensity,
            'total_volume': self.total_volume.json_serialise() if self.total_volume is not None else None,
            'tissue_load': self.tissue_load.json_serialise() if self.tissue_load is not None else None,
            'force_load': self.force_load.json_serialise() if self.tissue_load is not None else None,
            'power_load': self.power_load.json_serialise() if self.power_load is not None else None,
            'rpe_load': self.rpe_load.json_serialise() if self.rpe_load is not None else None
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        exercise = cls()
        exercise.id = input_dict.get('id', "")
        exercise.name = input_dict.get('name', "")
        exercise.movement_id = input_dict.get('movement_id', "")

        exercise.weight = input_dict.get('weight')  # in lbs
        exercise.weight_measure = WeightMeasure(input_dict['weight_measure']) if input_dict.get(
            'weight_measure') is not None else None

        exercise.sets = input_dict.get('sets', 0)
        exercise.reps_per_set = input_dict.get('reps_per_set')
        exercise.reps = input_dict.get('reps', 1)
        exercise.side = input_dict.get('side', 0)
        exercise.equipments = [Equipment(equipment) for equipment in input_dict.get('equipments', [])]
        exercise.explosiveness_rating = input_dict.get('explosiveness_rating', 0)
        exercise.unit_of_measure = UnitOfMeasure(input_dict['unit_of_measure']) if input_dict.get(
            'unit_of_measure') is not None else None

        exercise.predicted_rpe = input_dict.get('predicted_rpe')
        exercise.rpe = StandardErrorRange.json_deserialise(input_dict.get('rpe')) if input_dict.get('rpe') is not None else None

        exercise.prescribed_per_side = input_dict.get('prescribed_per_side', False)  # if the prescribed dosage is per side or total
        exercise.tempo = input_dict.get('tempo')  # OTF defines tempo for concentric/eccentric part of movement

        # primary assignments
        exercise.duration = Assignment.json_deserialise(input_dict['duration']) if input_dict.get('duration') is not None else None
        exercise.distance = Assignment.json_deserialise(input_dict['distance']) if input_dict.get('distance') is not None else None
        exercise.pace = Assignment.json_deserialise(input_dict['pace']) if input_dict.get('pace') is not None else None
        exercise.speed = Assignment.json_deserialise(input_dict['speed']) if input_dict.get('speed') is not None else None
        #exercise.grade = Assignment.json_deserialise(input_dict['grade']) if input_dict.get('grade') is not None else Assignment()
        exercise.grade = Assignment.json_deserialise(input_dict['grade']) if input_dict.get('grade') is not None else Assignment(assigned_value=0.0)
        exercise.cadence = Assignment.json_deserialise(input_dict['cadence']) if input_dict.get('cadence') is not None else None
        #exercise.stroke_rate = Assignment.json_deserialise(input_dict['stroke_rate']) if input_dict.get('stroke_rate') is not None else Assignment()
        exercise.stroke_rate = input_dict.get('stroke_rate', None)

        # alternate assignments
        exercise.alternate_distance = [Assignment.json_deserialise(a) for a in input_dict.get('alternate_distance', [])]  # will be a list of Assignment objects
        exercise.alternate_duration = [Assignment.json_deserialise(a) for a in input_dict.get('alternate_duration', [])]   # will be a list of Assignment objects
        exercise.alternate_pace = [Assignment.json_deserialise(a) for a in input_dict.get('alternate_pace', [])]   # will be a list of Assignment objects
        exercise.alternate_speed = [Assignment.json_deserialise(a) for a in input_dict.get('alternate_speed', [])]   # will be a list of Assignment objects
        exercise.alternate_grade = [Assignment.json_deserialise(a) for a in input_dict.get('alternate_grade', [])]   # will be a list of Assignment objects
        exercise.alternate_cadence = [Assignment.json_deserialise(a) for a in input_dict.get('alternate_cadence', [])]   # will be a list of Assignment objects
        exercise.alternate_stroke_rate = [Assignment.json_deserialise(a) for a in input_dict.get('alternate_stroke_rate', [])]   # will be a list of Assignment objects

        exercise.alternate_movement_ids = [MovementOption.json_deserialise(a) for a in input_dict.get('alternate_movement_ids', [])]

        exercise.stroke_adjustment = input_dict.get('stroke_adjustment', 0)  # how much lower than your base stroke rate
        exercise.power_goal = input_dict.get('power_goal')  # average power goal for exercise
        exercise.force = StandardErrorRange.json_deserialise(input_dict['force']) if input_dict.get('force') is not None else None
        exercise.power = StandardErrorRange.json_deserialise(input_dict['power']) if input_dict.get(
            'power') is not None else None
        exercise.calories = input_dict.get('calories')  # calorie goal for exercise
        exercise.maximal_intensity = input_dict.get('maximal_intensity', False)  # calorie goal for exercise

        exercise.total_volume = Assignment.json_deserialise(input_dict['total_volume']) if input_dict.get(
            'total_volume') is not None else None

        exercise.primary_actions = [ExerciseAction.json_deserialise(action) for action in input_dict.get('primary_actions', [])]
        exercise.secondary_actions = [ExerciseAction.json_deserialise(action) for action in input_dict.get('secondary_actions', [])]

        exercise.tissue_load = StandardErrorRange.json_deserialise(input_dict.get('tissue_load')) if input_dict.get('tissue_load') is not None else None
        exercise.force_load = StandardErrorRange.json_deserialise(input_dict.get('force_load')) if input_dict.get(
            'force_load') is not None else None
        exercise.power_load = StandardErrorRange.json_deserialise(input_dict.get('power_load')) if input_dict.get(
            'power_load') is not None else None
        exercise.rpe_load = StandardErrorRange.json_deserialise(input_dict.get('rpe_load')) if input_dict.get(
            'rpe_load') is not None else None

        return exercise

    def update_primary_from_alternates(self, assignment_type):

        for duration in self.alternate_duration:
            if duration.assignment_type == assignment_type:
                self.duration = duration
                break

        for distance in self.alternate_distance:
            if distance.assignment_tye == assignment_type:
                self.distance = distance
                break

        for pace in self.alternate_pace:
            if pace.assignment_type == assignment_type:
                self.pace = pace
                break

        for grade in self.alternate_grade:
            if grade.assignment_type == assignment_type:
                self.grade = grade
                break

        if self.grade is not None and self.grade.min_value is not None and self.grade.max_value is '':
            self.grade.max_value = .15

        if self.duration is not None and self.duration.min_value is not None and isinstance(self.duration.min_value, str):
            self.duration.min_value = None
        else:
            if self.duration is not None and self.duration.min_value is not None :
                self.duration.assigned_value = None

        if self.duration is not None and self.duration.max_value is not None and isinstance(self.duration.max_value, str):
            self.duration.max_value = None

    def update_movement_id(self, movement_option):
        if movement_option is not None:
            self.movement_id = next((option.movement_id for option in self.alternate_movement_ids if option.option_type == movement_option), self.movement_id)

    def set_speed_pace(self):
        speed = None
        pace = None
        # get pace
        if self.pace is not None:
            pace = self.pace  # all others are s/m
        elif self.speed is not None:
            pace = Assignment.divide_scalar_assignment(1, self.speed)
        elif self.duration is not None and self.distance is not None:
            pace = Assignment.divide_assignments(self.duration, self.distance)
        elif self.power_goal is not None:
            if self.cardio_action == CardioAction.row:
                pace_assignment = Assignment()
                if self.power_goal.assigned_value is not None:
                    pace_assignment.assigned_value = (2.8 / self.power_goal.assigned_value) ** (1 / 3)
                else:
                    pace_assignment.min_value = (2.8 / self.power_goal.min_value) ** (1 / 3)
                    pace_assignment.max_value = (2.8 / self.power_goal.max_value) ** (1 / 3)

                pace = pace_assignment

        # get speed
        if self.speed is not None:
            speed = self.speed
        elif self.duration is not None and self.distance is not None:
            speed = Assignment.divide_assignments(self.distance, self.duration)
        elif pace is not None:
            speed = Assignment.divide_scalar_assignment(1, self.pace)
        self.speed = speed
        self.pace = pace

    def set_training_loads(self):
        if self.power is not None and self.total_volume is not None:
            power_load = self.power.plagiarize()
            self.power_load = Assignment.multiply_range_by_assignment(power_load, self.total_volume)
        if self.force is not None and self.total_volume is not None:
            force_load = self.force.plagiarize()
            self.force_load = Assignment.multiply_range_by_assignment(force_load, self.total_volume)
            self.tissue_load = self.force_load.plagiarize()
        if self.predicted_rpe is not None:
            rpe_load = self.predicted_rpe.plagiarize()
            self.rpe_load = Assignment.multiply_range_by_assignment(rpe_load, self.total_volume)


