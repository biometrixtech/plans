import abc
import uuid
import datetime
from enum import Enum
from serialisable import Serialisable

from models.soreness_base import HistoricSorenessStatus, BodyPartLocation
from models.exercise import AssignedExercise
from models.goal import AthleteGoalType, AthleteGoal
from models.dosage import ExerciseDosage, DosageProgression
from models.body_parts import BodyPartFactory, BodyPart
from models.exercise_phase import ExercisePhase, ExercisePhaseType
from models.functional_movement import BodyPartFunction
from utils import parse_datetime, format_datetime


class MovementPrep(object):
    def __init__(self, user_id, created_date_time):
        self.movement_prep_id = None
        self.user_id = user_id
        self.created_date_time = created_date_time
        self.movement_integration_prep = None

    def json_serialise(self):
        return {
            "movement_prep_id": self.movement_prep_id,
            "user_id": self.user_id,
            "created_date_time": format_datetime(self.created_date_time) if self.created_date_time is not None else None,
            "movement_integration_prep": self.movement_integration_prep.json_serialise() if self.movement_integration_prep is not None else None
        }

    @classmethod
    def json_deserialise(cls, input_dict):
        movement_prep = cls(input_dict['user_id'], input_dict['created_date_time'])
        movement_prep.movement_prep_id = input_dict.get("movement_prep_id")
        movement_prep.movement_integration_prep = Activity.json_deserialise(input_dict['movement_integration_prep']) if input_dict.get('movement_integration_prep') is not None else None
        return movement_prep

    def __setattr__(self, name, value):
        if name in ['created_date_time']:
            if value is not None and not isinstance(value, datetime.datetime):
                value = parse_datetime(value)
        if name == 'movement_prep_id' and value is None:
            value = str(uuid.uuid4())
        super().__setattr__(name, value)


class MobilityWOD(object):
    def __init__(self, user_id, created_date_time):
        self.mobility_wod_id = None
        self.user_id = user_id
        self.created_date_time = created_date_time
        self.active_rest = None

    def json_serialise(self):
        return {
            "mobility_wod_id": self.mobility_wod_id,
            "user_id": self.user_id,
            "created_date_time": format_datetime(self.created_date_time) if self.created_date_time is not None else None,
            "active_rest": self.active_rest.json_serialise() if self.active_rest is not None else None
        }

    @classmethod
    def json_deserialise(cls, input_dict):
        mobility_wod = cls(input_dict['user_id'], input_dict['created_date_time'])
        mobility_wod.mobility_wod_id = input_dict.get("mobility_wod_id")
        mobility_wod.active_rest = Activity.json_deserialise(input_dict['active_rest']) if input_dict.get('active_rest') is not None else None
        return mobility_wod

    def __setattr__(self, name, value):
        if name in ['created_date_time']:
            if value is not None and not isinstance(value, datetime.datetime):
                value = parse_datetime(value)
        if name == 'mobility_wod_id' and value is None:
            value = str(uuid.uuid4())
        super().__setattr__(name, value)


class ResponsiveRecovery(object):
    def __init__(self, user_id, created_date_time):
        self.responsive_recovery_id = None
        self.user_id = user_id
        self.created_date_time = created_date_time
        self.active_rest = None
        self.active_recovery = None
        self.ice = None
        self.cold_water_immersion = None

    def json_serialise(self):
        return {
            "responsive_recovery_id": self.responsive_recovery_id,
            "user_id": self.user_id,
            "created_date_time": format_datetime(self.created_date_time) if self.created_date_time is not None else None,
            "active_rest": self.active_rest.json_serialise() if self.active_rest is not None else None,
            "active_recovery": self.active_recovery.json_serialise() if self.active_recovery is not None else None,
            "ice": self.ice.json_serialise() if self.ice is not None else None,
            "cold_water_immersion": self.cold_water_immersion.json_serialise() if self.cold_water_immersion is not None else None
        }

    @classmethod
    def json_deserialise(cls, input_dict):
        post_training_recovery = cls(input_dict['user_id'], input_dict['created_date_time'])
        post_training_recovery.responsive_recovery_id = input_dict.get("responsive_recovery_id")
        post_training_recovery.active_rest = Activity.json_deserialise(input_dict['active_rest']) if input_dict.get('active_rest') is not None else None
        post_training_recovery.active_recovery = Activity.json_deserialise(input_dict['active_recovery']) if input_dict.get('active_recovery') is not None else None
        post_training_recovery.ice = IceSession.json_deserialise(input_dict['ice']) if input_dict.get('ice') is not None else None
        post_training_recovery.cold_water_immersion = ColdWaterImmersion.json_deserialise(input_dict['cold_water_immersion']) if input_dict.get('cold_water_immersion') is not None else None
        return post_training_recovery

    def __setattr__(self, name, value):
        if name in ['created_date_time']:
            if value is not None and not isinstance(value, datetime.datetime):
                value = parse_datetime(value)
        if name == 'responsive_recovery_id' and value is None:
            value = str(uuid.uuid4())
        super().__setattr__(name, value)


class ActivityType(Enum):
    movement_integration_prep = 0
    active_rest = 1
    active_recovery = 2
    cold_water_immersion = 3
    ice = 4

    def get_display_name(self):
        display_names = {
            0: 'Movement Integration Prep',
            1: 'Active Rest',
            2: 'Active Recovery',
            3: 'Cold Water Immersion',
            4: 'Ice'
            }
        return display_names[self.value]


class ActivityGoal(Serialisable):
    def __init__(self):
        self.efficient_active = False
        self.complete_active = False
        self.comprehensive_active = False

    def json_serialise(self):
        ret = {
            'efficient_active': self.efficient_active,
            'complete_active': self.complete_active,
            'comprehensive_active': self.comprehensive_active
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        goal = cls()
        goal.efficient_active = input_dict.get('efficient_active', False)
        goal.complete_active = input_dict.get('complete_active', False)
        goal.comprehensive_active = input_dict.get('comprehensive_active', False)
        return goal


class DosageDuration(object):
    def __init__(self, efficient_duration, complete_duration, comprehensive_duration):
        self.efficient_duration = efficient_duration
        self.complete_duration = complete_duration
        self.comprehensive_duration = comprehensive_duration


class Activity(object):
    def __init__(self, event_date_time, activity_type, relative_load_level=3):
        self.id = None
        self.type = activity_type
        self.title = self.type.get_display_name().upper()
        self.start_date_time = None
        self.completed_date_time = None
        self.event_date_time = event_date_time
        self.completed = False
        self.active = True
        self.default_plan = "Complete"
        self.dosage_durations = {}
        self.initialize_dosage_durations()
        self.force_data = False
        self.goal_title = ""
        self.display_image = ""
        self.goal_defs = []
        self.goals = {}
        self.exercise_phases = []

        self.relative_load_level = relative_load_level
        self.efficient_winner = 1
        self.complete_winner = 1
        self.comprehensive_winner = 1
        self.rankings = set()

    def json_serialise(self):
        return {
            "id": self.id,
            "type": self.type.value,
            "title": self.title,
            "start_date_time": format_datetime(self.start_date_time) if self.start_date_time is not None else None,
            "completed_date_time": format_datetime(self.completed_date_time) if self.completed_date_time is not None else None,
            "event_date_time": format_datetime(self.event_date_time) if self.event_date_time is not None else None,
            "completed": self.completed,
            "default_plan": self.default_plan,
            "goals": {goal_text: goal.json_serialise() for (goal_text, goal) in self.goals.items()},
            "exercise_phases": [ex_phase.json_serialise() for ex_phase in self.exercise_phases]
         }

    @classmethod
    def json_deserialise(cls, input_dict):
        modality_type = ActivityType(input_dict["type"])
        if modality_type == ActivityType.movement_integration_prep:
            modality = MovementIntegrationPrep(event_date_time=input_dict.get('event_date_time'),
                                               force_data=input_dict.get('force_data', False))
        elif modality_type == ActivityType.active_rest:
            modality = ActiveRest(event_date_time=input_dict.get('event_date_time'),
                                  force_data=input_dict.get('force_data', False))
        elif modality_type == ActivityType.active_recovery:
            modality = ActiveRecovery(event_date_time=input_dict.get('event_date_time'))
        else:
            raise ValueError("Unknown activity type")
        modality.id = input_dict.get("id")
        modality.start_date_time = input_dict.get('start_date_time', None)
        modality.completed_date_time = input_dict.get('completed_date_time', None)
        modality.event_date_time = input_dict.get('event_date_time', None)
        modality.completed = input_dict.get('completed', False)
        modality.default_plan = input_dict.get('default_plan', 'Complete')
        modality.goals = {goal_type: ActivityGoal.json_deserialise(goal) for
                          (goal_type, goal) in input_dict.get('goals', {}).items()}
        modality.exercise_phases = [ExercisePhase.json_deserialise(ex_phase) for ex_phase in input_dict.get('exercise_phases', [])]
        return modality

    def __setattr__(self, name, value):
        if name in ['event_date_time', 'start_date_time', 'completed_date_time']:
            if value is not None and not isinstance(value, datetime.datetime):
                value = parse_datetime(value)
        if name == 'id' and value is None:
            value = str(uuid.uuid4())
        super().__setattr__(name, value)

    @abc.abstractmethod
    def fill_exercises(self, exercise_library, injury_risk_dict, sport_cardio_plyometrics, sport_body_parts):
        pass

    def get_total_exercises(self):
        total_exercises = 0
        for phase in self.exercise_phases:
            total_exercises += len(phase.exercises)
        return total_exercises

    def initialize_dosage_durations(self):

        self.dosage_durations[1] = DosageDuration(0, 0, 0)
        self.dosage_durations[2] = DosageDuration(0, 0, 0)
        self.dosage_durations[3] = DosageDuration(0, 0, 0)
        self.dosage_durations[4] = DosageDuration(0, 0, 0)
        self.dosage_durations[5] = DosageDuration(0, 0, 0)

    @abc.abstractmethod
    def conditions_for_increased_sensitivity_met(self, soreness_list, muscular_strain_high):
        return False

    def reconcile_default_plan_with_active_time(self):

        efficient_duration = self.dosage_durations[self.efficient_winner].efficient_duration

        complete_duration = self.dosage_durations[self.complete_winner].complete_duration

        if complete_duration == 0 and self.default_plan == "Complete":
            self.reactivate_complete_goals()
        elif efficient_duration == 0 and complete_duration == 0:
            self.reactivate_complete_goals()
            self.default_plan = "Complete"

    def get_dosage_rank_and_progression(self, goal, severity, tier):

        if goal.goal_type == AthleteGoalType.pain or goal.goal_type == AthleteGoalType.sore:
            if 7 <= severity:
                if tier == 1:
                    return 1, DosageProgression.mod_max_super_max
                else:
                    return 2, DosageProgression.mod_max_super_max
            elif 4 <= severity < 7:
                if tier == 1:
                    return 1, DosageProgression.mod_max_super_max
                else:
                    return 2, DosageProgression.mod_max_super_max
            else:
                if tier == 1:
                    return 2, DosageProgression.min_mod_max
                else:
                    return 3, DosageProgression.min_mod_max

        elif goal.goal_type == AthleteGoalType.high_load:
            if tier == 1:
                return 1, DosageProgression.min_mod_max
            elif tier == 2:
                return 2, DosageProgression.min_mod_max
            elif tier == 3:
                return 3, DosageProgression.min_mod_max
            elif tier == 4:
                return 4, DosageProgression.min_mod_max
            elif tier == 5:
                return 5, DosageProgression.min_mod_max
            else:
                return 0, None

        elif goal.goal_type == AthleteGoalType.asymmetric_session or goal.goal_type == AthleteGoalType.on_request:
            if tier == 1:
                return 1, DosageProgression.min_mod_max
            elif tier == 2:
                return 2, DosageProgression.min_mod_max
            elif tier == 3:
                return 3, DosageProgression.min_mod_max
            elif tier == 4:
                return 4, DosageProgression.min_mod_max
            elif tier == 5:
                return 5, DosageProgression.min_mod_max
            else:
                return 0, None

        elif goal.goal_type == AthleteGoalType.corrective:
            if tier == 1:
                return 2, DosageProgression.min_mod_max
            elif tier == 2:
                return 3, DosageProgression.min_mod_max
            else:
                return 0, None
        else:
            return 0, None

    def add_goals(self, dosages):

        for dosage in dosages:
            if dosage.goal.text not in self.goals:
                if ((dosage.efficient_reps_assigned > 0 and dosage.efficient_sets_assigned > 0) or
                        (dosage.complete_reps_assigned > 0 and dosage.complete_sets_assigned > 0) or
                        (dosage.comprehensive_reps_assigned > 0 and dosage.comprehensive_sets_assigned > 0)):
                    self.goals[dosage.goal.text] = ActivityGoal()

    def update_goals(self, dosage):

        if dosage.goal.text not in self.goals:
            if ((dosage.efficient_reps_assigned > 0 and dosage.efficient_sets_assigned > 0) or
                    (dosage.complete_reps_assigned > 0 and dosage.complete_sets_assigned > 0) or
                    (dosage.comprehensive_reps_assigned > 0 and dosage.comprehensive_sets_assigned > 0)):
                self.goals[dosage.goal.text] = ActivityGoal()

        # self.goals[dosage.goal.text].efficient_active = False
        # self.goals[dosage.goal.text].complete_active = False
        # self.goals[dosage.goal.text].comprehensive_active = False

        if dosage.efficient_reps_assigned > 0 and dosage.efficient_sets_assigned > 0:
            self.goals[dosage.goal.text].efficient_active = True
        if dosage.complete_reps_assigned > 0 and dosage.complete_sets_assigned > 0:
            self.goals[dosage.goal.text].complete_active = True
        if dosage.comprehensive_reps_assigned > 0 and dosage.comprehensive_sets_assigned > 0:
            self.goals[dosage.goal.text].comprehensive_active = True

    def set_plan_dosage(self):
        if 1 not in self.rankings and 2 not in self.rankings:
            self.default_plan = "Efficient"
        else:
            self.default_plan = "Complete"

    def copy_exercises(self, source_collection, target_phase, goal, tier, severity, exercise_library,
                       sports=[]):

        position_order = 0

        try:
            target_collection = [phase.exercises for phase in self.exercise_phases if phase.type==target_phase][0]
        except IndexError:
            print("phase not initialized")
            phase = ExercisePhase(target_phase)
            self.exercise_phases.append(phase)
            target_collection = phase.exercises
        for s in source_collection:

            if s.exercise.id not in target_collection:
                target_collection[s.exercise.id] = AssignedExercise(library_id=str(s.exercise.id))
                exercise_list = [ex for ex in exercise_library if ex.id == str(s.exercise.id)]
                target_collection[s.exercise.id].exercise = exercise_list[0]
                target_collection[s.exercise.id].equipment_required = target_collection[
                    s.exercise.id].exercise.equipment_required
                target_collection[s.exercise.id].position_order = position_order

            ranking, progression = self.get_dosage_rank_and_progression(goal, severity, tier)

            if ranking > 0:
                self.rankings.add(ranking)
            dosage = ExerciseDosage()
            dosage.dosage_progression = progression
            dosage.tier = tier
            dosage.last_severity = severity
            dosage.ranking = ranking
            dosage.sports = sports
            dosage.goal = goal
            #dosage = self.update_dosage(dosage, target_collection[s.exercise.id].exercise)
            #if dosage.get_total_dosage() > 0:
            target_collection[s.exercise.id].dosages.append(dosage)
            position_order += 1

    def aggregate_dosages(self):
        for phase in self.exercise_phases:
            self.aggregate_dosage_by_severity_exercise_collection(phase.exercises)

    def reactivate_complete_goals(self):
        for phase in self.exercise_phases:
            self.reactivate_complete_corrective_goals_by_collection(phase.exercises)

    def reactivate_complete_corrective_goals_by_collection(self, assigned_exercises):

        for ex, a in assigned_exercises.items():
            for d in a.dosages:
                if d.goal.goal_type == AthleteGoalType.corrective:
                    d.complete_reps_assigned = d.default_complete_reps_assigned
                    d.complete_sets_assigned = d.default_complete_sets_assigned
                    self.update_goals(d)

    def aggregate_dosage_by_severity_exercise_collection(self, assigned_exercises):

        for ex, a in assigned_exercises.items():
            a.dosages = [dosage for dosage in a.dosages if isinstance(dosage.priority, str)]
            if len(a.dosages) > 0:

                a.dosages = sorted(a.dosages, key=lambda x: (3 - int(x.priority),
                                                             x.default_efficient_sets_assigned,
                                                             x.default_efficient_reps_assigned,
                                                             x.default_complete_sets_assigned,
                                                             x.default_complete_reps_assigned,
                                                             x.default_comprehensive_sets_assigned,
                                                             x.default_comprehensive_reps_assigned), reverse=True)

                self.add_goals(a.dosages)
                dosage = a.dosages[0]
                for goal_dosage in a.dosages:
                    self.update_goals(goal_dosage)

                if dosage.priority == "1":
                    self.calc_dosage_durations(1, a, dosage)
                elif dosage.priority == "2" and dosage.severity() > 4:
                    self.calc_dosage_durations(2, a, dosage)
                elif dosage.priority == "2" and dosage.severity() <= 4:
                    self.calc_dosage_durations(3, a, dosage)
                elif dosage.priority == "3" and dosage.severity() > 4:
                    self.calc_dosage_durations(4, a, dosage)
                elif dosage.priority == "3" and dosage.severity() <= 4:
                    self.calc_dosage_durations(5, a, dosage)

    def set_winners(self):

        # key off efficient as the guide
        total_efficient = 0
        total_complete = 0
        total_comprehensive = 0
        benchmarks = [1, 2, 3, 4, 5]

        proposed_limit = 300

        for b in range(0, len(benchmarks) - 1):
            total_efficient += self.dosage_durations[benchmarks[b]].efficient_duration
            #proposed_efficient = total_efficient + self.dosage_durations[benchmarks[b + 1]].efficient_duration
            proposed_efficient = self.dosage_durations[benchmarks[b + 1]].efficient_duration
            if 0 < proposed_efficient < proposed_limit:
                continue
            elif abs(total_efficient - proposed_limit) < abs(proposed_efficient - proposed_limit):
                self.efficient_winner = benchmarks[b]
                break
            else:
                self.efficient_winner = benchmarks[b + 1]

    def scale_all_active_time(self):
        for phase in self.exercise_phases:
            self.scale_active_time(phase.exercises)

    def scale_active_time(self, assigned_exercises):

        if self.efficient_winner is not None:  # if None, don't reduce
            for ex, a in assigned_exercises.items():
                if len(a.dosages) > 0:

                    if self.efficient_winner == 1:
                        for d in a.dosages:
                            if d.priority != '1':
                                d.efficient_reps_assigned = 0
                                d.efficient_sets_assigned = 0
                    elif self.efficient_winner == 2:
                        for d in a.dosages:
                            if d.priority == '3' or (d.priority == '2' and d.severity() <= 4):
                                d.efficient_reps_assigned = 0
                                d.efficient_sets_assigned = 0
                    elif self.efficient_winner == 3:
                        for d in a.dosages:
                            if d.priority == '3':
                                d.efficient_reps_assigned = 0
                                d.efficient_sets_assigned = 0
                    elif self.efficient_winner == 4:
                        for d in a.dosages:
                            if d.priority == '3' and d.severity() <= 4:
                                d.efficient_reps_assigned = 0
                                d.efficient_sets_assigned = 0
                    elif self.efficient_winner == 5:
                        pass
                    elif self.efficient_winner == 0:
                        pass

    def calc_dosage_durations(self, benchmark_value, assigned_exercise, dosage):
        if dosage.efficient_reps_assigned is not None and dosage.efficient_sets_assigned is not None:
            self.dosage_durations[benchmark_value].efficient_duration += assigned_exercise.duration(
                dosage.efficient_reps_assigned, dosage.efficient_sets_assigned)
        if dosage.complete_reps_assigned is not None and dosage.complete_sets_assigned is not None:
            self.dosage_durations[benchmark_value].complete_duration += assigned_exercise.duration(
                dosage.complete_reps_assigned, dosage.complete_sets_assigned)
        if dosage.comprehensive_reps_assigned is not None and dosage.comprehensive_sets_assigned is not None:
            self.dosage_durations[benchmark_value].comprehensive_duration += assigned_exercise.duration(
                dosage.comprehensive_reps_assigned, dosage.comprehensive_sets_assigned)


    #@staticmethod
    def update_dosage(self, dosage, exercise):
        if dosage.goal.goal_type == AthleteGoalType.high_load or dosage.goal.goal_type == AthleteGoalType.asymmetric_session:
            if self.relative_load_level == 3:
                if dosage.priority == "1":
                    dosage.efficient_reps_assigned = exercise.min_reps
                    dosage.efficient_sets_assigned = 1
                    dosage.default_efficient_reps_assigned = exercise.min_reps
                    dosage.default_efficient_sets_assigned = 1

                if dosage.priority == "1" or dosage.priority == "2":
                    dosage.complete_reps_assigned = exercise.min_reps
                    dosage.complete_sets_assigned = 1
                    dosage.default_complete_reps_assigned = exercise.min_reps
                    dosage.default_complete_sets_assigned = 1

                dosage.comprehensive_reps_assigned = exercise.max_reps
                dosage.comprehensive_sets_assigned = 1
                dosage.default_comprehensive_reps_assigned = exercise.max_reps
                dosage.default_comprehensive_sets_assigned = 1

            elif self.relative_load_level == 2:
                if dosage.priority == "1":
                    dosage.efficient_reps_assigned = exercise.min_reps
                    dosage.efficient_sets_assigned = 1
                    dosage.default_efficient_reps_assigned = exercise.min_reps
                    dosage.default_efficient_sets_assigned = 1

                if dosage.priority == "1" or dosage.priority == "2":
                    dosage.complete_reps_assigned = exercise.min_reps
                    dosage.complete_sets_assigned = 1
                    dosage.default_complete_reps_assigned = exercise.min_reps
                    dosage.default_complete_sets_assigned = 1

                dosage.comprehensive_reps_assigned = exercise.min_reps
                dosage.comprehensive_sets_assigned = 1
                dosage.default_comprehensive_reps_assigned = exercise.min_reps
                dosage.default_comprehensive_sets_assigned = 1

            elif self.relative_load_level == 1:
                if dosage.priority == "1":
                    dosage.efficient_reps_assigned = exercise.max_reps
                    dosage.efficient_sets_assigned = 1
                    dosage.default_efficient_reps_assigned = exercise.max_reps
                    dosage.default_efficient_sets_assigned = 1

                if dosage.priority == "1" or dosage.priority == "2":
                    dosage.complete_reps_assigned = exercise.max_reps
                    dosage.complete_sets_assigned = 1
                    dosage.default_complete_reps_assigned = exercise.max_reps
                    dosage.default_complete_sets_assigned = 1

                dosage.comprehensive_reps_assigned = exercise.max_reps
                dosage.comprehensive_sets_assigned = 1
                dosage.default_comprehensive_reps_assigned = exercise.max_reps
                dosage.default_comprehensive_sets_assigned = 1

        if dosage.goal.goal_type == AthleteGoalType.corrective:
            if dosage.priority == "1":
                dosage.efficient_reps_assigned = exercise.max_reps
                dosage.efficient_sets_assigned = 1
                dosage.default_efficient_reps_assigned = exercise.max_reps
                dosage.default_efficient_sets_assigned = 1

            if dosage.priority == "1" or dosage.priority == "2":
                dosage.complete_reps_assigned = exercise.max_reps
                dosage.complete_sets_assigned = 1
                dosage.default_complete_reps_assigned = exercise.max_reps
                dosage.default_complete_sets_assigned = 1

            dosage.comprehensive_reps_assigned = exercise.max_reps
            dosage.comprehensive_sets_assigned = 2
            dosage.default_comprehensive_reps_assigned = exercise.max_reps
            dosage.default_comprehensive_sets_assigned = 2

        if dosage.goal.goal_type == AthleteGoalType.pain or dosage.goal.goal_type == AthleteGoalType.sore:
            if dosage.last_severity < 1.0:
                if dosage.priority == "1":
                    dosage.efficient_reps_assigned = exercise.min_reps
                    dosage.efficient_sets_assigned = 1
                    dosage.default_efficient_reps_assigned = exercise.min_reps
                    dosage.default_efficient_sets_assigned = 1

                    dosage.complete_reps_assigned = exercise.max_reps
                    dosage.complete_sets_assigned = 1
                    dosage.default_complete_reps_assigned = exercise.max_reps
                    dosage.default_complete_sets_assigned = 1

                if dosage.priority == "1" or dosage.priority == "2":
                    dosage.comprehensive_reps_assigned = exercise.min_reps
                    dosage.comprehensive_sets_assigned = 1
                    dosage.default_comprehensive_reps_assigned = exercise.min_reps
                    dosage.default_comprehensive_sets_assigned = 1

            elif 1.0 <= dosage.last_severity < 3.0:
                if dosage.priority == "1":
                    dosage.efficient_reps_assigned = exercise.min_reps
                    dosage.efficient_sets_assigned = 1
                    dosage.default_efficient_reps_assigned = exercise.min_reps
                    dosage.default_efficient_sets_assigned = 1
                if dosage.priority == "1" or dosage.priority == "2":
                    dosage.complete_reps_assigned = exercise.min_reps
                    dosage.complete_sets_assigned = 1
                    dosage.default_complete_reps_assigned = exercise.min_reps
                    dosage.default_complete_sets_assigned = 1

                    dosage.comprehensive_reps_assigned = exercise.max_reps
                    dosage.comprehensive_sets_assigned = 1
                    dosage.default_comprehensive_reps_assigned = exercise.max_reps
                    dosage.default_comprehensive_sets_assigned = 1
            elif 3 <= dosage.last_severity < 5:
                if dosage.priority == "1":
                    dosage.efficient_reps_assigned = exercise.min_reps
                    dosage.efficient_sets_assigned = 1
                    dosage.default_efficient_reps_assigned = exercise.min_reps
                    dosage.default_efficient_sets_assigned = 1
                if dosage.priority == "1" or dosage.priority == "2":
                    dosage.complete_reps_assigned = exercise.min_reps
                    dosage.complete_sets_assigned = 1
                    dosage.default_complete_reps_assigned = exercise.min_reps
                    dosage.default_complete_sets_assigned = 1

                dosage.comprehensive_reps_assigned = exercise.min_reps
                dosage.comprehensive_sets_assigned = 1
                dosage.default_comprehensive_reps_assigned = exercise.min_reps
                dosage.default_comprehensive_sets_assigned = 1
            elif 5 <= dosage.last_severity < 7:
                if dosage.priority == "1" or dosage.priority == "2":
                    dosage.efficient_reps_assigned = exercise.min_reps
                    dosage.efficient_sets_assigned = 1
                    dosage.default_efficient_reps_assigned = exercise.min_reps
                    dosage.default_efficient_sets_assigned = 1
                # trial
                dosage.complete_reps_assigned = exercise.min_reps
                dosage.complete_sets_assigned = 1
                dosage.default_complete_reps_assigned = exercise.min_reps
                dosage.default_complete_sets_assigned = 1
                dosage.comprehensive_reps_assigned = exercise.max_reps
                dosage.comprehensive_sets_assigned = 1
                dosage.default_comprehensive_reps_assigned = exercise.max_reps
                dosage.default_comprehensive_sets_assigned = 1
            elif 7 <= dosage.last_severity < 9:
                dosage.efficient_reps_assigned = exercise.min_reps
                dosage.efficient_sets_assigned = 1
                dosage.complete_reps_assigned = exercise.max_reps
                dosage.complete_sets_assigned = 1
                dosage.comprehensive_reps_assigned = exercise.max_reps
                dosage.comprehensive_sets_assigned = 2
                dosage.default_efficient_reps_assigned = exercise.min_reps
                dosage.default_efficient_sets_assigned = 1
                dosage.default_complete_reps_assigned = exercise.max_reps
                dosage.default_complete_sets_assigned = 1
                dosage.default_comprehensive_reps_assigned = exercise.max_reps
                dosage.default_comprehensive_sets_assigned = 2
            elif dosage.last_severity >= 9:
                dosage.efficient_reps_assigned = exercise.max_reps
                dosage.efficient_sets_assigned = 1

                dosage.complete_reps_assigned = exercise.max_reps
                dosage.complete_sets_assigned = 2
                dosage.comprehensive_reps_assigned = exercise.max_reps
                dosage.comprehensive_sets_assigned = 3
                dosage.default_efficient_reps_assigned = exercise.max_reps
                dosage.default_efficient_sets_assigned = 1

                dosage.default_complete_reps_assigned = exercise.max_reps
                dosage.default_complete_sets_assigned = 2
                dosage.default_comprehensive_reps_assigned = exercise.max_reps
                dosage.default_comprehensive_sets_assigned = 3

        elif dosage.goal.goal_type == AthleteGoalType.on_request:
            if dosage.priority == "1":
                dosage.efficient_reps_assigned = exercise.min_reps
                dosage.efficient_sets_assigned = 1
                dosage.default_efficient_reps_assigned = exercise.min_reps
                dosage.default_efficient_sets_assigned = 1

                dosage.complete_reps_assigned = exercise.max_reps
                dosage.complete_sets_assigned = 1
                dosage.default_complete_reps_assigned = exercise.max_reps
                dosage.default_complete_sets_assigned = 1

            if dosage.priority == "1" or dosage.priority == "2":

                dosage.comprehensive_reps_assigned = exercise.min_reps
                dosage.comprehensive_sets_assigned = 1
                dosage.default_comprehensive_reps_assigned = exercise.min_reps
                dosage.default_comprehensive_sets_assigned = 1
        return dosage

    @staticmethod
    def rank_dosages(target_collections):
        for target_collection in target_collections:
            for ex in target_collection.values():
                ex.set_dosage_ranking()

    def prioritize_dosages(self, exercise_collection, target_ranking, priority):
        for exercise_int, assigned_exercise in exercise_collection.items():
            for dosage in assigned_exercise.dosages:
                if dosage.ranking == target_ranking:
                    dosage.priority = str(priority)
                    dosage.set_reps_and_sets(assigned_exercise.exercise)

    def set_exercise_dosage_ranking(self):
        ordered_ranks = sorted(self.rankings)
        rank_max = min(3, len(ordered_ranks))
        for r in range(0, rank_max):
            current_ranking = ordered_ranks[r]
            for phase in self.exercise_phases:
                self.prioritize_dosages(phase.exercises, current_ranking, r + 1)


class ActiveRestBase(Activity):
    def __init__(self, event_date_time, modality_type, force_data=False, relative_load_level=3, force_on_demand=True):
        super().__init__(event_date_time, modality_type, relative_load_level)
        self.force_data = force_data
        self.force_on_demand = force_on_demand

    @abc.abstractmethod
    def check_recovery(self, body_part_side, body_part_injury_risk, exercise_library, max_severity, sport_cardio_plyometrics, sport_body_parts):
        pass

    @abc.abstractmethod
    def check_care(self, body_part_side, body_part_injury_risk, exercise_library, max_severity):
        pass

    @abc.abstractmethod
    def check_prevention(self, body_part_side, body_part_injury_risk, exercise_library, max_severity, sport_body_parts):
        pass

    def conditions_for_increased_sensitivity_met(self, soreness_list, muscular_strain_high):

        if muscular_strain_high:
            return True
        else:
            for s in soreness_list:
                if (s.first_reported_date_time is not None and
                        (s.is_persistent_soreness() or
                         s.historic_soreness_status == HistoricSorenessStatus.persistent_2_soreness)):
                    days_sore = (self.event_date_time - s.first_reported_date_time).days
                    if days_sore < 30:
                        return True
        return False

    def is_body_part_overactive_short(self, body_part_injury_risk):

        is_overactive_short = False

        if body_part_injury_risk.overactive_short_count_last_0_20_days >= 3:
            is_overactive_short = True

        return is_overactive_short

    def is_body_part_overactive_long(self, body_part_injury_risk):

        is_overactive_long = False

        if body_part_injury_risk.overactive_long_count_last_0_20_days >= 3:
            is_overactive_long = True

        return is_overactive_long

    def is_body_part_underactive_long(self, body_part_injury_risk):

        is_underactive_long = False

        if body_part_injury_risk.underactive_long_count_last_0_20_days >= 3:
            is_underactive_long = True

        return is_underactive_long

    def is_body_part_underactive_short(self, body_part_injury_risk):
        is_underactive_short = False

        if body_part_injury_risk.underactive_short_count_last_0_20_days >= 3:
            is_underactive_short = True

        return is_underactive_short

    def is_body_part_long(self, body_part_injury_risk):

        is_long = False

        if body_part_injury_risk.long_count_last_0_20_days >= 3:
            is_long = True
        return is_long

    def is_body_part_short(self, body_part_injury_risk):

        is_short = False

        if body_part_injury_risk.knots_count_last_0_20_days >= 3:
            is_short = True
        if body_part_injury_risk.tight_count_last_0_20_days >= 3:
            is_short = True
        if body_part_injury_risk.sharp_count_last_0_20_days >= 3:
            is_short = True
        if body_part_injury_risk.ache_count_last_0_20_days >= 4:
            is_short = True
        if body_part_injury_risk.short_count_last_0_20_days >= 3:
            is_short = True
        return is_short

    def is_body_part_weak(self, body_part_injury_risk):

        is_weak = False

        if body_part_injury_risk.weak_count_last_0_20_days >= 3:
            is_weak = True

        return is_weak

    def is_functional_overreaching(self, body_part_injury_risk):
        if (body_part_injury_risk.last_functional_overreaching_date is not None and
              body_part_injury_risk.last_functional_overreaching_date == self.event_date_time.date()):
            return True
        else:
            return False

    def is_non_functional_overreaching(self, body_part_injury_risk):

        two_days_ago = self.event_date_time.date() - datetime.timedelta(days=1)

        if (body_part_injury_risk.last_non_functional_overreaching_date is not None and
              body_part_injury_risk.last_non_functional_overreaching_date >= two_days_ago):
            return True
        else:
            return False

    def is_excessive_strain(self, body_part_injury_risk):

        two_days_ago = self.event_date_time.date() - datetime.timedelta(days=1)

        if (body_part_injury_risk.last_excessive_strain_date is not None and
                body_part_injury_risk.last_excessive_strain_date == self.event_date_time.date()):
            return True
        elif (body_part_injury_risk.last_excessive_strain_date is not None and
              body_part_injury_risk.last_non_functional_overreaching_date is not None and
              body_part_injury_risk.last_non_functional_overreaching_date >= two_days_ago):
            return True
        else:
            return False

    def fill_exercises(self, exercise_library, injury_risk_dict, sport_cardio_plyometrics=False, sport_body_parts=None):

        max_severity = 0
        for body_part, body_part_injury_risk in injury_risk_dict.items():
            if (body_part_injury_risk.last_sharp_level > 0 and body_part_injury_risk.last_sharp_date is not None
                    and body_part_injury_risk.last_sharp_date == self.event_date_time.date()):
                max_severity = max(max_severity, body_part_injury_risk.last_sharp_level)
            if (body_part_injury_risk.last_ache_level > 0 and body_part_injury_risk.last_ache_date is not None
                    and body_part_injury_risk.last_ache_date == self.event_date_time.date()):
                max_severity = max(max_severity, body_part_injury_risk.last_ache_level)

        if self.force_data:
            self.get_general_exercises(exercise_library, max_severity)
        else:
            if len(injury_risk_dict) > 0:
                for body_part, body_part_injury_risk in injury_risk_dict.items():
                    self.check_recovery(body_part, body_part_injury_risk, exercise_library, max_severity, sport_cardio_plyometrics, sport_body_parts)
                    self.check_care(body_part, body_part_injury_risk, exercise_library, max_severity)
                    self.check_prevention(body_part, body_part_injury_risk, exercise_library, max_severity, sport_body_parts)
            else:
                if self.force_on_demand:
                    self.get_general_exercises(exercise_library, max_severity)

    def get_last_severity(self, body_part_injury_risk):

        last_severity = 0

        if (body_part_injury_risk.last_sharp_level > 0 and body_part_injury_risk.last_sharp_date is not None
                and body_part_injury_risk.last_sharp_date == self.event_date_time.date()):
            last_severity = max(last_severity, body_part_injury_risk.last_sharp_level)
        if (body_part_injury_risk.last_ache_level > 0 and body_part_injury_risk.last_ache_date is not None
                and body_part_injury_risk.last_ache_date == self.event_date_time.date()):
            last_severity = max(last_severity, body_part_injury_risk.last_ache_level)
        if (body_part_injury_risk.last_tight_level > 0 and body_part_injury_risk.last_tight_date is not None
                and body_part_injury_risk.last_tight_date == self.event_date_time.date()):
            last_severity = max(last_severity, body_part_injury_risk.last_tight_level)
        if (body_part_injury_risk.last_knots_level > 0 and body_part_injury_risk.last_knots_date is not None
                and body_part_injury_risk.last_knots_date == self.event_date_time.date()):
            last_severity = max(last_severity, body_part_injury_risk.last_knots_level)

        return last_severity

    def get_general_exercises(self, exercise_library, max_severity):

        pass


class MovementIntegrationPrep(ActiveRestBase):
    def __init__(self, event_date_time, force_data=False, relative_load_level=3, force_on_demand=True):
        super().__init__(event_date_time, ActivityType.movement_integration_prep, force_data, relative_load_level, force_on_demand)
        self.exercise_phases = [ExercisePhase(ExercisePhaseType.inhibit),
                                ExercisePhase(ExercisePhaseType.static_stretch),
                                ExercisePhase(ExercisePhaseType.active_stretch),
                                ExercisePhase(ExercisePhaseType.dynamic_stretch),
                                ExercisePhase(ExercisePhaseType.isolated_activate),
                                ExercisePhase(ExercisePhaseType.static_integrate),
                                ExercisePhase(ExercisePhaseType.dynamic_integrate)]

    def get_general_exercises(self, exercise_library, max_severity):

        body_part_factory = BodyPartFactory()

        body_part = body_part_factory.get_general()

        goal = AthleteGoal("Improve mobility", 1, AthleteGoalType.on_request)

        for a in body_part.agonists:
            agonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(a), None))
            if agonist is not None:
                self.copy_exercises(agonist.inhibit_exercises, ExercisePhaseType.inhibit, goal, 1, 0,
                                    exercise_library)
                if max_severity < 7:
                    self.copy_exercises(agonist.static_stretch_exercises, ExercisePhaseType.static_stretch, goal, 1, 0, exercise_library)
                    self.copy_exercises(agonist.active_stretch_exercises, ExercisePhaseType.active_stretch, goal, 1, 0, exercise_library)
                if max_severity < 5:
                    self.copy_exercises(agonist.isolated_activate_exercises, ExercisePhaseType.isolated_activate, goal,
                                        1, 0, exercise_library)

        for y in body_part.synergists:
            synergist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(y), None))
            if synergist is not None:
                self.copy_exercises(synergist.inhibit_exercises, ExercisePhaseType.inhibit, goal, 2, 0,
                                    exercise_library)
                if max_severity < 7:
                    self.copy_exercises(synergist.active_stretch_exercises, ExercisePhaseType.active_stretch, goal, 2, 0, exercise_library)
                if max_severity < 5:
                    self.copy_exercises(synergist.isolated_activate_exercises, ExercisePhaseType.isolated_activate, goal,
                                        2, 0, exercise_library)

        for t in body_part.stabilizers:
            stabilizer = body_part_factory.get_body_part(BodyPart(BodyPartLocation(t), None))
            if stabilizer is not None:
                self.copy_exercises(stabilizer.inhibit_exercises, ExercisePhaseType.inhibit, goal, 3, 0,
                                    exercise_library)
                if max_severity < 7:
                    self.copy_exercises(stabilizer.active_stretch_exercises, ExercisePhaseType.active_stretch, goal, 3, 0, exercise_library)
                if max_severity < 5:
                    self.copy_exercises(stabilizer.isolated_activate_exercises, ExercisePhaseType.isolated_activate, goal,
                                        3, 0, exercise_library)

        if max_severity < 5:
            self.copy_exercises(body_part.static_integrate_exercises, ExercisePhaseType.static_integrate, goal, 1, 0,
                                exercise_library)

    def check_recovery(self, body_part, body_part_injury_risk, exercise_library, max_severity, sport_cardio_plyometrics, sport_body_parts):
        compensating = False
        excessive_strain = False

        if body_part is not None and body_part.location in sport_body_parts.keys():
            if 0 < body_part_injury_risk.total_volume_percent_tier < 4:
                excessive_strain = True

            if (body_part_injury_risk.last_movement_dysfunction_stress_date is not None and
                    body_part_injury_risk.last_movement_dysfunction_stress_date == self.event_date_time.date()):
                compensating = True
                body_part_injury_risk.total_compensation_percent_tier = 1
            elif (body_part_injury_risk.last_compensation_date is not None
                  and body_part_injury_risk.last_compensation_date == self.event_date_time.date() and
                  0 < body_part_injury_risk.total_compensation_percent_tier < 4):
                compensating = True

            # TODO: what should the goal name be?
            goal = AthleteGoal("Recover from training", 1, AthleteGoalType.high_load)

            if excessive_strain or compensating:
                high_load_tier = 0
                comp_tier = 0
                tier = 0

                if excessive_strain:
                    high_load_tier = body_part_injury_risk.total_volume_percent_tier
                if compensating:
                    comp_tier = body_part_injury_risk.total_compensation_percent_tier

                if high_load_tier > 0 and comp_tier > 0:
                    tier = min(high_load_tier, comp_tier)
                elif high_load_tier > 0:
                    tier = high_load_tier
                elif comp_tier > 0:
                    tier = comp_tier

                if tier > 0:
                    self.copy_exercises(body_part.inhibit_exercises, ExercisePhaseType.inhibit, goal,
                                        tier, 0, exercise_library)
                    if max_severity < 7.0:
                        if sport_cardio_plyometrics:
                            self.copy_exercises(body_part.dynamic_stretch_exercises, ExercisePhaseType.dynamic_stretch, goal,
                                                tier, 0, exercise_library)
                        else:
                            self.copy_exercises(body_part.active_stretch_exercises, ExercisePhaseType.active_stretch, goal,
                                                tier, 0, exercise_library)

            if excessive_strain:
                if max_severity < 5.0:
                    if sport_body_parts[body_part.location] in [BodyPartFunction.prime_mover, BodyPartFunction.stabilizer]:
                        self.copy_exercises(body_part.isolated_activate_exercises, ExercisePhaseType.isolated_activate, goal,
                                            body_part_injury_risk.total_volume_percent_tier,
                                            0, exercise_library)
                    # self.copy_exercises(body_part.static_integrate_exercises, ExercisePhaseType.static_integrate, goal,
                    #                     body_part_injury_risk.total_volume_percent_tier,
                    #                     0, exercise_library)
                # if max_severity < 4.0:
                #     # TODO: What does "match upcoming sport and intensity mean"
                #     if body_part.location in sport_body_parts.keys():
                #         self.copy_exercises(body_part.dynamic_integrate_exercises, ExercisePhaseType.dynamic_integrate, goal,
                #                             body_part_injury_risk.total_volume_percent_tier,
                #                             0, exercise_library)

    def check_care(self, body_part, body_part_injury_risk, exercise_library, max_severity):
        muscle_spasm = False
        knots = False
        inflammation = False

        if (body_part_injury_risk.last_inflammation_date is not None and
                body_part_injury_risk.last_inflammation_date == self.event_date_time.date()):
            inflammation = True

        if (body_part_injury_risk.last_muscle_spasm_date is not None and
                body_part_injury_risk.last_muscle_spasm_date == self.event_date_time.date()):
            muscle_spasm = True

        if (body_part_injury_risk.last_knots_date is not None and
                body_part_injury_risk.last_knots_date == self.event_date_time.date()):
            knots = True

        goal = AthleteGoal("Care for symptoms", 1, AthleteGoalType.sore)

        if muscle_spasm or knots or inflammation:

            last_severity = 0

            if muscle_spasm:
                last_severity = max(last_severity, body_part_injury_risk.get_muscle_spasm_severity(self.event_date_time.date()))
            if knots:
                last_severity = max(last_severity, body_part_injury_risk.get_knots_severity(self.event_date_time.date()))
            if inflammation:
                last_severity = max(last_severity, body_part_injury_risk.get_inflammation_severity(self.event_date_time.date()))

            self.copy_exercises(body_part.inhibit_exercises, ExercisePhaseType.inhibit, goal, 1, last_severity,
                                exercise_library)

            if max_severity < 7.0:
                self.copy_exercises(body_part.active_stretch_exercises, ExercisePhaseType.active_stretch, goal, 1,
                                    last_severity, exercise_library)
            if max_severity < 5.0:  # TODO: this threshold needs to be updated
                self.copy_exercises(body_part.dynamic_stretch_exercises, ExercisePhaseType.dynamic_stretch, goal, 1,
                                    last_severity, exercise_library)

            body_part_factory = BodyPartFactory()

            for s in body_part.synergists:
                synergist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(s), None))
                self.copy_exercises(synergist.inhibit_exercises, ExercisePhaseType.inhibit, goal, 2, last_severity,
                                    exercise_library)

                if max_severity < 7.0:
                    self.copy_exercises(synergist.active_stretch_exercises, ExercisePhaseType.active_stretch, goal, 2,
                                        last_severity, exercise_library)
                if max_severity < 5.0:  # TODO: this threshold needs to be updated
                    self.copy_exercises(synergist.dynamic_stretch_exercises, ExercisePhaseType.dynamic_stretch, goal, 2,
                                        last_severity, exercise_library)

        if muscle_spasm or knots:

            last_severity = 0

            if muscle_spasm:
                last_severity = max(last_severity,
                                    body_part_injury_risk.get_muscle_spasm_severity(self.event_date_time.date()))
            if knots:
                last_severity = max(last_severity,
                                    body_part_injury_risk.get_knots_severity(self.event_date_time.date()))

            if max_severity < 7.0:
                self.copy_exercises(body_part.static_stretch_exercises, ExercisePhaseType.static_stretch, goal, 1,
                                    last_severity, exercise_library)

            body_part_factory = BodyPartFactory()

            for s in body_part.synergists:
                synergist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(s), None))

                if max_severity < 7.0:
                    self.copy_exercises(synergist.static_stretch_exercises, ExercisePhaseType.static_stretch, goal, 2,
                                        last_severity, exercise_library)

    def check_prevention(self, body_part, body_part_injury_risk, exercise_library, max_severity, sport_body_parts):
        if body_part is not None and body_part.location in sport_body_parts.keys():

            # is_short = self.is_body_part_short(body_part_injury_risk)
            is_overactive_short = self.is_body_part_overactive_short(body_part_injury_risk)
            is_overactive_long = self.is_body_part_overactive_long(body_part_injury_risk)
            is_underactive_long = self.is_body_part_underactive_long(body_part_injury_risk)
            is_underactive_short = self.is_body_part_underactive_short(body_part_injury_risk)
            is_weak = self.is_body_part_weak(body_part_injury_risk)
            # tier_one = False

            if is_overactive_short:
                goal = AthleteGoal("Reduce injury risks", 1, AthleteGoalType.corrective)
                # tier_one = True
                self.copy_exercises(body_part.inhibit_exercises, ExercisePhaseType.inhibit, goal, 1, 0, exercise_library)
                if max_severity < 7.0:
                    self.copy_exercises(body_part.static_stretch_exercises, ExercisePhaseType.static_stretch, goal, 1,
                                        0, exercise_library)

            elif is_underactive_long or is_weak:

                goal = AthleteGoal("Reduce injury risks", 1, AthleteGoalType.corrective)
                # tier_one = True
                if max_severity < 5.0:
                    self.copy_exercises(body_part.isolated_activate_exercises, ExercisePhaseType.isolated_activate, goal, 1,
                                        0, exercise_library)

            elif is_overactive_long:
                goal = AthleteGoal("Reduce injury risks", 1, AthleteGoalType.corrective)
                # tier_one = True
                self.copy_exercises(body_part.inhibit_exercises, ExercisePhaseType.inhibit, goal, 1, 0, exercise_library)

            elif is_underactive_short:

                goal = AthleteGoal("Reduce injury risks", 1, AthleteGoalType.corrective)
                # tier_one = True
                self.copy_exercises(body_part.inhibit_exercises, ExercisePhaseType.inhibit, goal, 1, 0, exercise_library)
                if max_severity < 7.0:
                    self.copy_exercises(body_part.static_stretch_exercises, ExercisePhaseType.static_stretch, goal, 1, 0, exercise_library)
                    self.copy_exercises(body_part.active_stretch_exercises, ExercisePhaseType.active_stretch, goal, 1, 0, exercise_library)
                if max_severity < 5.0:
                    self.copy_exercises(body_part.isolated_activate_exercises, ExercisePhaseType.isolated_activate, goal, 1, 0, exercise_library)
                if max_severity < 5.0:  # TODO: this threshold might need to change
                    self.copy_exercises(body_part.dynamic_stretch_exercises, ExercisePhaseType.dynamic_stretch, goal, 1, 0, exercise_library)

            # TODO: The logic below is not found in movement_prep spreadsheet.
            # elif is_short:
            #     goal = AthleteGoal("Reduce injury risks", 1, AthleteGoalType.corrective)
            #     tier_one = True
            #     self.copy_exercises(body_part.inhibit_exercises, ExercisePhaseType.inhibit, goal, 2, 0, exercise_library)
            #
            #     if max_severity < 7.0:
            #         self.copy_exercises(body_part.static_stretch_exercises, ExercisePhaseType.static_stretch, goal, 2,
            #                             0, exercise_library)

            # if not tier_one and body_part_injury_risk.limited_mobility_tier == 2:
            #     goal = AthleteGoal("Reduce injury risks", 1, AthleteGoalType.corrective)
            #
            #     self.copy_exercises(body_part.inhibit_exercises, ExercisePhaseType.inhibit, goal, 2,
            #                         0, exercise_library)
            #
            #     if max_severity < 7.0:
            #         self.copy_exercises(body_part.static_stretch_exercises, ExercisePhaseType.static_stretch, goal, 2, 0, exercise_library)
            #         # self.copy_exercises(body_part.active_stretch_exercises, ExercisePhaseType.active_stretch, goal, "1",
            #         #                     last_severity, exercise_library)
            #
            # if not tier_one and body_part_injury_risk.underactive_weak_tier == 2:
            #
            #     goal = AthleteGoal("Reduce injury risks", 1, AthleteGoalType.corrective)
            #
            #     if max_severity < 5.0:
            #         self.copy_exercises(body_part.isolated_activate_exercises, ExercisePhaseType.isolated_activate, goal,
            #                             2, 0, exercise_library)


class ActiveRest(ActiveRestBase):
    def __init__(self, event_date_time, force_data=False, relative_load_level=3, force_on_demand=True):
        super().__init__(event_date_time, ActivityType.active_rest, force_data, relative_load_level, force_on_demand)
        self.exercise_phases = [ExercisePhase(ExercisePhaseType.inhibit),
                                ExercisePhase(ExercisePhaseType.static_stretch),
                                ExercisePhase(ExercisePhaseType.isolated_activate),
                                ExercisePhase(ExercisePhaseType.static_integrate)]

    def get_general_exercises(self, exercise_library, max_severity):

        body_part_factory = BodyPartFactory()

        body_part = body_part_factory.get_general()

        goal = AthleteGoal("Improve mobility", 1, AthleteGoalType.on_request)

        for a in body_part.agonists:
            agonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(a), None))
            if agonist is not None:
                self.copy_exercises(agonist.inhibit_exercises, ExercisePhaseType.inhibit, goal, 1, 0,
                                    exercise_library)
                if max_severity < 7:
                    self.copy_exercises(agonist.static_stretch_exercises, ExercisePhaseType.static_stretch, goal, 1,
                                        0, exercise_library)
                if max_severity < 5:
                    self.copy_exercises(agonist.isolated_activate_exercises, ExercisePhaseType.isolated_activate, goal,
                                        1, 0, exercise_library)

        for y in body_part.synergists:
            synergist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(y), None))
            if synergist is not None:
                self.copy_exercises(synergist.inhibit_exercises, ExercisePhaseType.inhibit, goal, 2, 0,
                                    exercise_library)
                if max_severity < 7:
                    self.copy_exercises(synergist.static_stretch_exercises, ExercisePhaseType.static_stretch, goal, 2,
                                        0, exercise_library)
                if max_severity < 5:
                    self.copy_exercises(synergist.isolated_activate_exercises, ExercisePhaseType.isolated_activate, goal,
                                        2, 0, exercise_library)

        for t in body_part.stabilizers:
            stabilizer = body_part_factory.get_body_part(BodyPart(BodyPartLocation(t), None))
            if stabilizer is not None:
                self.copy_exercises(stabilizer.inhibit_exercises, ExercisePhaseType.inhibit, goal, 3, 0,
                                    exercise_library)
                if max_severity < 7:
                    self.copy_exercises(stabilizer.static_stretch_exercises, ExercisePhaseType.static_stretch, goal, 3,
                                        0, exercise_library)
                if max_severity < 5:
                    self.copy_exercises(stabilizer.isolated_activate_exercises, ExercisePhaseType.isolated_activate, goal,
                                        3, 0, exercise_library)

        if max_severity < 5:
            self.copy_exercises(body_part.static_integrate_exercises, ExercisePhaseType.static_integrate, goal, 1, 0,
                                exercise_library)

    def check_recovery(self, body_part, body_part_injury_risk, exercise_library, max_severity, sport_cardio_plyometrics, sport_body_parts):

        goals = []

        compensating = False
        high_load = False

        if body_part is not None:

            if 0 < body_part_injury_risk.total_volume_percent_tier < 4:
                # goals.append(AthleteGoal("Recover from Training", 1, AthleteGoalType.high_load))
                high_load = True

            if (body_part_injury_risk.last_movement_dysfunction_stress_date is not None and
                    body_part_injury_risk.last_movement_dysfunction_stress_date == self.event_date_time.date()):

                compensating = True
                body_part_injury_risk.total_compensation_percent_tier = 1
            elif (body_part_injury_risk.last_compensation_date is not None
                  and body_part_injury_risk.last_compensation_date == self.event_date_time.date() and
                  0 < body_part_injury_risk.total_compensation_percent_tier < 4):

                compensating = True

            # if compensating:
            #     goals.append(AthleteGoal("Recover from Training", 1, AthleteGoalType.asymmetric_session))

            # for goal in goals:
            goal = AthleteGoal("Recover from training", 1, AthleteGoalType.high_load)

            if high_load or compensating:

                high_load_tier = 0
                comp_tier = 0
                tier = 0

                if high_load:
                    high_load_tier = body_part_injury_risk.total_volume_percent_tier
                if compensating:
                    comp_tier = body_part_injury_risk.total_compensation_percent_tier

                if high_load_tier > 0 and comp_tier > 0:
                    tier = min(high_load_tier, comp_tier)
                elif high_load_tier > 0:
                    tier = high_load_tier
                elif comp_tier > 0:
                    tier = comp_tier

                if tier > 0:
                    self.copy_exercises(body_part.inhibit_exercises, ExercisePhaseType.inhibit, goal,
                                        tier, 0, exercise_library)

                    if max_severity < 7.0:
                        self.copy_exercises(body_part.static_stretch_exercises, ExercisePhaseType.static_stretch, goal,
                                            tier, 0, exercise_library)

            if high_load:

                if max_severity < 5.0:
                    self.copy_exercises(body_part.isolated_activate_exercises, ExercisePhaseType.isolated_activate, goal,
                                        body_part_injury_risk.total_volume_percent_tier,
                                        0, exercise_library)

    def check_care(self, body_part, body_part_injury_risk, exercise_library, max_severity):

        goals = []

        muscle_spasm = False
        knots = False
        inflammation = False

        if (body_part_injury_risk.last_inflammation_date is not None and
                body_part_injury_risk.last_inflammation_date == self.event_date_time.date()):
            # goals.append(AthleteGoal("Care for symptoms", 1, AthleteGoalType.pain))
            inflammation = True

        if (body_part_injury_risk.last_muscle_spasm_date is not None and
                body_part_injury_risk.last_muscle_spasm_date == self.event_date_time.date()):
            muscle_spasm = True

        if (body_part_injury_risk.last_knots_date is not None and
                body_part_injury_risk.last_knots_date == self.event_date_time.date()):
            knots = True

        # if muscle_spasm or knots:
        #     goals.append(AthleteGoal("Care for symptoms", 1, AthleteGoalType.sore))

        # for goal in goals:
        goal = AthleteGoal("Care for symptoms", 1, AthleteGoalType.sore)

        if muscle_spasm or knots or inflammation:

            last_severity = 0

            if muscle_spasm:
                last_severity = max(last_severity, body_part_injury_risk.get_muscle_spasm_severity(self.event_date_time.date()))
            if knots:
                last_severity = max(last_severity, body_part_injury_risk.get_knots_severity(self.event_date_time.date()))
            if inflammation:
                last_severity = max(last_severity, body_part_injury_risk.get_inflammation_severity(self.event_date_time.date()))

            self.copy_exercises(body_part.inhibit_exercises, ExercisePhaseType.inhibit, goal, 1, last_severity,
                                exercise_library)

            if max_severity < 7.0:
                self.copy_exercises(body_part.static_stretch_exercises, ExercisePhaseType.static_stretch, goal, 1,
                                    last_severity, exercise_library)

            body_part_factory = BodyPartFactory()

            for s in body_part.synergists:
                synergist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(s), None))
                self.copy_exercises(synergist.inhibit_exercises, ExercisePhaseType.inhibit, goal, 2, last_severity,
                                    exercise_library)

                if max_severity < 7.0:
                    self.copy_exercises(synergist.static_stretch_exercises, ExercisePhaseType.static_stretch, goal, 2,
                                        last_severity, exercise_library)

    def check_prevention(self, body_part, body_part_injury_risk, exercise_library, max_severity, sport_body_parts):

        if body_part is not None:

            is_short = self.is_body_part_short(body_part_injury_risk)
            is_overactive_short = self.is_body_part_overactive_short(body_part_injury_risk)
            is_overactive_long = self.is_body_part_overactive_long(body_part_injury_risk)
            is_underactive_short = self.is_body_part_underactive_short(body_part_injury_risk)
            is_underactive_long = self.is_body_part_underactive_long(body_part_injury_risk)
            is_weak = self.is_body_part_weak(body_part_injury_risk)
            tier_one = False

            if is_overactive_short:

                goal = AthleteGoal("Reduce injury risks", 1, AthleteGoalType.corrective)
                tier_one = True
                self.copy_exercises(body_part.inhibit_exercises, ExercisePhaseType.inhibit, goal, 1, 0, exercise_library)

                if max_severity < 7.0:
                    self.copy_exercises(body_part.static_stretch_exercises, ExercisePhaseType.static_stretch, goal, 1,
                                        0, exercise_library)

            elif is_underactive_long or is_weak:

                goal = AthleteGoal("Reduce injury risks", 1, AthleteGoalType.corrective)
                tier_one = True
                if max_severity < 5.0:
                    self.copy_exercises(body_part.isolated_activate_exercises, ExercisePhaseType.isolated_activate, goal, 1,
                                        0, exercise_library)

            elif is_overactive_long:

                goal = AthleteGoal("Reduce injury risks", 1, AthleteGoalType.corrective)
                tier_one = True
                self.copy_exercises(body_part.inhibit_exercises, ExercisePhaseType.inhibit, goal, 1, 0, exercise_library)

            elif is_underactive_short:

                goal = AthleteGoal("Reduce injury risks", 1, AthleteGoalType.corrective)
                tier_one = True
                self.copy_exercises(body_part.inhibit_exercises, ExercisePhaseType.inhibit, goal, 1, 0, exercise_library)

                if max_severity < 7.0:
                    self.copy_exercises(body_part.static_stretch_exercises, ExercisePhaseType.static_stretch, goal, 1, 0, exercise_library)

                if max_severity < 5.0:
                    self.copy_exercises(body_part.isolated_activate_exercises, ExercisePhaseType.isolated_activate, goal,
                                        1, 0, exercise_library)

            elif is_short:

                goal = AthleteGoal("Reduce injury risks", 1, AthleteGoalType.corrective)
                tier_one = True
                self.copy_exercises(body_part.inhibit_exercises, ExercisePhaseType.inhibit, goal, 2, 0, exercise_library)

                if max_severity < 7.0:
                    self.copy_exercises(body_part.static_stretch_exercises, ExercisePhaseType.static_stretch, goal, 2,
                                        0, exercise_library)

            if not tier_one and body_part_injury_risk.limited_mobility_tier == 2:

                goal = AthleteGoal("Reduce injury risks", 1, AthleteGoalType.corrective)

                self.copy_exercises(body_part.inhibit_exercises, ExercisePhaseType.inhibit, goal, 2, 0, exercise_library)

                if max_severity < 7.0:
                    self.copy_exercises(body_part.static_stretch_exercises, ExercisePhaseType.static_stretch, goal, 2,
                                        0, exercise_library)

            if not tier_one and body_part_injury_risk.underactive_weak_tier == 2:

                goal = AthleteGoal("Reduce injury risks", 1, AthleteGoalType.corrective)

                if max_severity < 5.0:
                    self.copy_exercises(body_part.isolated_activate_exercises, ExercisePhaseType.isolated_activate, goal,
                                        2, 0, exercise_library)


class ActiveRecovery(Activity):
    def __init__(self, event_date_time):
        super().__init__(event_date_time, ActivityType.active_recovery)

    def fill_exercises(self, exercise_library, injury_risk_dict, sport_cardio_plyometrics=False, sport_body_parts=None):

        max_severity = 0
        for body_part, body_part_injury_risk in injury_risk_dict.items():
            if (body_part_injury_risk.last_sharp_level > 0 and body_part_injury_risk.last_sharp_date is not None
                    and body_part_injury_risk.last_sharp_date == self.event_date_time.date()):
                max_severity = max(max_severity, body_part_injury_risk.last_sharp_level)
            if (body_part_injury_risk.last_ache_level > 0 and body_part_injury_risk.last_ache_date is not None
                    and body_part_injury_risk.last_ache_date == self.event_date_time.date()):
                max_severity = max(max_severity, body_part_injury_risk.last_ache_level)

        if len(injury_risk_dict) > 0:
            for body_part, body_part_injury_risk in injury_risk_dict.items():
                self.check_recovery(body_part, body_part_injury_risk, exercise_library, max_severity)

    def check_recovery(self, body_part, body_part_injury_risk, exercise_library, max_severity):

        goals = []

        compensating = False
        high_load = False

        if body_part is not None:

            if 0 < body_part_injury_risk.total_volume_percent_tier < 4:
                # goals.append(AthleteGoal("Recover from Training", 1, AthleteGoalType.high_load))
                high_load = True

            if (body_part_injury_risk.last_movement_dysfunction_stress_date is not None and
                    body_part_injury_risk.last_movement_dysfunction_stress_date == self.event_date_time.date()):

                compensating = True
                body_part_injury_risk.total_compensation_percent_tier = 1
            elif (body_part_injury_risk.last_compensation_date is not None
                  and body_part_injury_risk.last_compensation_date == self.event_date_time.date() and
                  0 < body_part_injury_risk.total_compensation_percent_tier < 4):

                compensating = True

            # if compensating:
            #     goals.append(AthleteGoal("Recover from Training", 1, AthleteGoalType.asymmetric_session))

            # for goal in goals:
            goal = AthleteGoal("Recover from training", 1, AthleteGoalType.high_load)

            if high_load or compensating:

                high_load_tier = 0
                comp_tier = 0
                tier = 0

                if high_load:
                    high_load_tier = body_part_injury_risk.total_volume_percent_tier
                if compensating:
                    comp_tier = body_part_injury_risk.total_compensation_percent_tier

                if high_load_tier > 0 and comp_tier > 0:
                    tier = min(high_load_tier, comp_tier)
                elif high_load_tier > 0:
                    tier = high_load_tier
                elif comp_tier > 0:
                    tier = comp_tier

                if tier > 0:

                    if max_severity < 4.0:
                        self.copy_exercises(body_part.dynamic_integrate_exercises, ExercisePhaseType.dynamic_integrate, goal,
                                            tier, 0, exercise_library)


class IceSession(object):
    def __init__(self, event_date_time, minutes=0):
        self.minutes = minutes
        self.start_date_time = None
        self.completed_date_time = None
        self.event_date_time = event_date_time
        self.completed = False
        self.body_parts = []
        self.goal = None

    def json_serialise(self):

        ret = {
            'minutes': self.minutes,
            'start_date_time': format_datetime(self.start_date_time) if self.start_date_time is not None else None,
            'completed_date_time': format_datetime(self.completed_date_time) if self.completed_date_time is not None else None,
            'event_date_time': format_datetime(self.event_date_time) if self.event_date_time is not None else None,
            'completed': self.completed,
            'body_parts': [ice.json_serialise() for ice in self.body_parts],
            'goal': self.goal.json_serialise() if self.goal is not None else None
        }

        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        ice_session = cls(event_date_time=input_dict['event_date_time'], minutes=input_dict.get('minutes', 0))
        ice_session.start_date_time = input_dict.get('start_date_time', None)
        ice_session.completed_date_time = input_dict.get('completed_date_time', None)
        ice_session.completed = input_dict.get('completed', False)
        ice_session.goal = AthleteGoal.json_deserialise(input_dict['goal']) if input_dict.get('goal') is not None else None
        ice_session.body_parts = [Ice.json_deserialise(body_part) for body_part in input_dict.get('body_parts', [])]
        if len(ice_session.body_parts) > 0:
            return ice_session
        else:
            return None

    def __setattr__(self, name, value):
        if name in ['event_date_time', 'start_date_time', 'completed_date_time']:
            if value is not None and not isinstance(value, datetime.datetime):
                value = parse_datetime(value)
        super().__setattr__(name, value)


class Ice(object):
    def __init__(self, body_part_location=None, side=0):
        self.body_part_location = body_part_location
        self.side = side
        self.completed = False

    def json_serialise(self):
        ret = {
            'body_part_location': self.body_part_location.value,
            'side': self.side,
            'completed': self.completed
        }

        return ret

    def __eq__(self, other):
        return self.body_part_location == other.body_part_location and self.side == other.side

    @classmethod
    def json_deserialise(cls, input_dict):
        ice = cls(body_part_location=BodyPartLocation(input_dict['body_part_location']),
                  side=input_dict['side'])
        ice.completed = input_dict.get('completed', False)

        return ice


class ColdWaterImmersion(Serialisable):
    def __init__(self, event_date_time, minutes=10):
        self.id = None
        self.minutes = minutes
        self.start_date_time = None
        self.completed_date_time = None
        self.event_date_time = event_date_time
        self.completed = False
        self.goals = set()

    def json_serialise(self):
        ret = {
            'minutes': self.minutes,
            'goals': [goal.json_serialise() for goal in self.goals],
            'start_date_time': format_datetime(self.start_date_time) if self.start_date_time is not None else None,
            'completed_date_time': format_datetime(self.completed_date_time) if self.completed_date_time is not None else None,
            'event_date_time': format_datetime(self.event_date_time) if self.event_date_time is not None else None,
            'completed': self.completed
        }

        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        cold_water_immersion = cls(event_date_time=input_dict['event_date_time'], minutes=input_dict['minutes'])
        cold_water_immersion.start_date_time = input_dict.get('start_date_time', None)
        cold_water_immersion.completed_date_time = input_dict.get('completed_date_time', None)
        cold_water_immersion.completed = input_dict.get('completed', False)
        cold_water_immersion.goals = set([AthleteGoal.json_deserialise(goal) for goal in input_dict.get('goals', [])])

        return cold_water_immersion

    def __setattr__(self, name, value):
        if name in ['event_date_time', 'start_date_time', 'completed_date_time']:
            if value is not None and not isinstance(value, datetime.datetime):
                value = parse_datetime(value)
        super().__setattr__(name, value)
