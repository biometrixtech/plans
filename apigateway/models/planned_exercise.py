from utils import format_date, parse_date


class PlannedWorkout(object):
    def __init__(self):
        self.name = ""
        self.event_date = None  # date for which this is planned
        self.duration = ""
        self.sections = []

    def json_serialise(self):
        ret = {
            'name': self.name,
            'event_date': format_date(self.event_date),
            'duration': self.duration,
            'sections': [s.json_serialise() for s in self.sections]
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        workout = cls()
        workout.name = input_dict.get('name')
        workout.event_date = parse_date(input_dict.get('event_date')) if input_dict.get('event_date') is not None else None
        workout.duration = input_dict.get('duration')
        workout.sections = [PlannedSection.json_deserialise(section) for section in input_dict.get('sections', [])]

        return workout


class PlannedSection(object):
    def __init__(self):
        self.name = ""
        self.start_time = None  # relative time in seconds from start of the workout
        self.duration = None
        self.exercises = []

    def json_serialise(self):
        ret = {
            'name': self.name,
            'start_time': self.start_time,
            'duration': self.duration,
            'exercises': [e.json_serialise() for e in self.exercises]
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        workout_section = cls()
        workout_section.name = input_dict.get('name')
        workout_section.start_time = input_dict.get('start_time')
        workout_section.duration = input_dict.get('duration')
        workout_section.exercises = [PlannedExercise.json_deserialise(workout_exercise) for workout_exercise in input_dict.get('exercises', [])]

        return workout_section


class PlannedExercise(object):
    def __init__(self):
        self.id = ""
        self.name = ""
        self.equipments = []  # probably need to define this but could come from movement
        self.movement_id = ""

        self.weight = None  # in lbs
        self.weight_measure = None

        self.reps = 1
        self.prescribed_per_side = False  # if the prescribed dosage is per side or total
        self.tempo = None  # OTF defines tempo for concentric/eccentric part of movement

        # primary assignments
        self.duration = Assignment()
        self.distance = Assignment()
        self.pace = Assignment()
        self.speed = Assignment()
        self.grade = Assignment()
        self.cadence = Assignment()
        self.stroke_rate = Assignment()

        # alternate assignments
        self.alternate_distance = []  # will be a list of Assignment objects
        self.alternate_duration = []  # will be a list of Assignment objects
        self.alternate_pace = []  # will be a list of Assignment objects
        self.alternate_speed = []  # will be a list of Assignment objects
        self.alternate_grade = []  # will be a list of Assignment objects
        self.alternate_cadence = []  # will be a list of Assignment objects
        self.alternate_stroke_rate = []  # will be a list of Assignment objects

        self.stroke_adjustment = 0  # how much lower than your base stroke rate

        self.power = None  # average power goal for exercise
        # self.power_above_base = None  # e.g OTF defines as all_out as 50Watts above base, do not need to store
        # Note that the rule-of-thumb base power is your bodyweight in lbs

        self.calories = None  # calorie goal for exercise

        self.maximal_intensity = False  # Potentially use this in calculating HRMax, VO2Max etc

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
            'reps': self.reps,
            'prescribed_per_side': self.prescribed_per_side,
            'tempo': self.tempo,

            'duration': self.duration.json_serialise(),
            'distance': self.distance.json_serialise(),
            'pace': self.pace.json_serialise(),
            'speed': self.speed.json_serialise(),
            'grade': self.grade.json_serialise(),
            'cadence': self.cadence.json_serialise(),
            'stroke_rate': self.stroke_rate.json_serialise(),

            'alternate_duration': [duration.json_serialise() for duration in self.alternate_duration],
            'alternate_distance': [distance.json_serialise() for distance in self.alternate_duration],
            'alternate_pace': [pace.json_serialise() for pace in self.alternate_duration],
            'alternate_speed': [speed.json_serialise() for speed in self.alternate_duration],
            'alternate_grade': [grade.json_serialise() for grade in self.alternate_duration],
            'alternate_cadence': [cadence.json_serialise() for cadence in self.alternate_duration],
            'alternate_stroke_rate': [stroke_rate.json_serialise() for stroke_rate in self.alternate_duration],

            'stroke_adjustment': self.stroke_adjustment,
            'power': self.power,
            'calories': self.calories,
            'maximal_intensity': self.maximal_intensity
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        exercise = cls()
        exercise.id = input_dict.get('id', "")
        exercise.name = input_dict.get('name', "")
        exercise.equipments = []  # probably need to define this but could come from movement
        exercise.movement_id = input_dict.get('movement_id', "")

        exercise.weight = input_dict.get('weight')  # in lbs
        exercise.weight_measure = input_dict.get('weight_measure')

        exercise.reps = input_dict.get('reps', 1)
        exercise.prescribed_per_side = input_dict.get('prescribed_per_side', False)  # if the prescribed dosage is per side or total
        exercise.tempo = input_dict.get('tempo')  # OTF defines tempo for concentric/eccentric part of movement

        # primary assignments
        exercise.duration = Assignment.json_deserialise(input_dict['duration']) if input_dict.get('duration') is not None else Assignment()
        exercise.distance = Assignment.json_deserialise(input_dict['distance']) if input_dict.get('distance') is not None else Assignment()
        exercise.pace = Assignment.json_deserialise(input_dict['pace']) if input_dict.get('pace') is not None else Assignment()
        exercise.speed = Assignment.json_deserialise(input_dict['speed']) if input_dict.get('speed') is not None else Assignment()
        exercise.grade = Assignment.json_deserialise(input_dict['grade']) if input_dict.get('grade') is not None else Assignment()
        exercise.cadence = Assignment.json_deserialise(input_dict['cadence']) if input_dict.get('cadence') is not None else Assignment()
        exercise.stroke_rate = Assignment.json_deserialise(input_dict['stroke_rate']) if input_dict.get('stroke_rate') is not None else Assignment()

        # alternate assignments
        exercise.alternate_distance = [Assignment.json_deserialise(a) for a in input_dict.get('alternate_distance', [])]  # will be a list of Assignment objects
        exercise.alternate_duration = [Assignment.json_deserialise(a) for a in input_dict.get('alternate_duration', [])]   # will be a list of Assignment objects
        exercise.alternate_pace = [Assignment.json_deserialise(a) for a in input_dict.get('alternate_pace', [])]   # will be a list of Assignment objects
        exercise.alternate_speed = [Assignment.json_deserialise(a) for a in input_dict.get('alternate_speed', [])]   # will be a list of Assignment objects
        exercise.alternate_grade = [Assignment.json_deserialise(a) for a in input_dict.get('alternate_grade', [])]   # will be a list of Assignment objects
        exercise.alternate_cadence = [Assignment.json_deserialise(a) for a in input_dict.get('alternate_cadence', [])]   # will be a list of Assignment objects
        exercise.alternate_stroke_rate = [Assignment.json_deserialise(a) for a in input_dict.get('alternate_stroke_rate', [])]   # will be a list of Assignment objects

        exercise.stroke_adjustment = input_dict.get('stroke_adjustment', 0)  # how much lower than your base stroke rate
        exercise.power = input_dict.get('power')  # average power goal for exercise
        exercise.calories = input_dict.get('calories')  # calorie goal for exercise
        exercise.maximal_intensity = input_dict.get('maximal_intensity', False)  # calorie goal for exercise

        return exercise


class Assignment(object):
    def __init__(self, assignment_type=None, assigned_value=None, min_value=None, max_value=None):
        self.assignment_type = assignment_type  # e.g. runner/jogger/power walker for OTF. This might have to be provider specific
        self.assigned_value = assigned_value
        self.min_value = min_value
        self.max_value = max_value

    def json_serialise(self):
        ret = {
            'assignment_type': self.assignment_type,
            'assigned_value': self.assigned_value,
            'min_value': self.min_value,
            'max_value': self.max_value
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        assignment = cls()
        assignment.assignment_type = input_dict.get('assignment_type')
        assignment.assigned_value = input_dict.get('assigned_value')
        assignment.min_value = input_dict.get('min_value')
        assignment.max_value = input_dict.get('max_value')

        return assignment
