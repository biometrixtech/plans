import abc
import uuid
import datetime
from enum import Enum
from serialisable import Serialisable

from models.soreness import Alert
from models.soreness_base import HistoricSorenessStatus, BodyPartLocation, BodyPartFunction
from models.exercise import AssignedExercise
from models.goal import AthleteGoalType, AthleteGoal
from models.trigger import TriggerType
from models.dosage import ExerciseDosage, DosageProgression
from models.body_parts import BodyPartFactory, BodyPart
from models.exercise_phase import ExercisePhase, ExercisePhaseType
from models.functional_movement_activities import Activity, ActivityType, ActivityGoal, ActiveRecovery, DosageDuration, ActiveRestBase, ActiveRest, MovementIntegrationPrep
from utils import parse_datetime, format_datetime


class ModalityType(Enum):
    pre_active_rest = 0
    post_active_rest = 1
    warm_up = 2
    cool_down = 3
    functional_strength = 4
    movement_integration_prep = 5
    active_recovery = 6
    cold_water_immersion = 7
    ice = 8

    def get_display_name(self):
        display_names = {
            0: 'Mobilize',
            1: 'Mobility',
            2: 'Warm Up',
            3: 'Cool Down',
            4: 'Functional Strength',
            5: 'Movement Prep',
            6: 'Active Recovery',
            7: 'Cold Water Immersion',
            8: 'Ice'
            }
        return display_names[self.value]

    def get_image(self):
            images = {
                0: 'pre_active_rest',
                1: 'post_active_rest',
                2: 'warm_up',
                3: 'cool_down',
                4: 'functional_strength',
                5: 'warm_up',
                6: 'cool_down',
                7: 'cool_down',
                8: 'cool_down'
                }
            return images[self.value]


class ModalityTypeDisplay(object):
    def __init__(self, modality_type):
        self.type = modality_type
        self.name = ModalityType.get_display_name(self.type)
        self.image = ModalityType.get_image(self.type)

    def json_serialise(self):
        return {
            "type": self.type.value,
            "name": self.name,
            "image": self.image
        }

    @classmethod
    def json_deserialise(cls, input_dict):
        return cls(ModalityType(input_dict['type']))


# class ModalityGoal(Serialisable):
#     def __init__(self):
#         self.efficient_active = False
#         self.complete_active = False
#         self.comprehensive_active = False
#
#     def json_serialise(self):
#         ret = {
#             'efficient_active': self.efficient_active,
#             'complete_active': self.complete_active,
#             'comprehensive_active': self.comprehensive_active
#         }
#         return ret
#
#     @classmethod
#     def json_deserialise(cls, input_dict):
#         goal = cls()
#         goal.efficient_active = input_dict.get('efficient_active', False)
#         goal.complete_active = input_dict.get('complete_active', False)
#         goal.comprehensive_active = input_dict.get('comprehensive_active', False)
#         return goal


# class DosageDuration(object):
#     def __init__(self, efficient_duration, complete_duration, comprehensive_duration):
#         self.efficient_duration = efficient_duration
#         self.complete_duration = complete_duration
#         self.comprehensive_duration = comprehensive_duration


class Modality(Activity):
    def __init__(self, event_date_time, modality_type, relative_load_level=3, possible_benchmarks=5):
        super().__init__(event_date_time, modality_type, relative_load_level, possible_benchmarks=possible_benchmarks)
        #self.id = None
        self.type = modality_type
        #self.title = self.type.get_display_name().upper()
        self.when = ""
        self.when_card = ""
        #self.start_date_time = None
        #self.completed_date_time = None
        #self.event_date_time = event_date_time
        #self.completed = False
        #self.active = True
        #self.default_plan = "Complete"
        #self.dosage_durations = {}
        #self.initialize_dosage_durations()
        #self.force_data = False
        #self.goal_title = ""
        #self.display_image = ""
        self.locked_text = ""
        #self.goal_defs = []
        #self.goals = {}
        #self.exercise_phases = []

        #self.relative_load_level = relative_load_level
        self.efficient_winner = 1
        self.complete_winner = 1
        self.comprehensive_winner = 1
        self.rankings = set()

        self.source_training_session_id = None

    def __setattr__(self, name, value):
        if name in ['type']:
            if value is not None and isinstance(value, ActivityType):
                if value == ActivityType.movement_integration_prep:
                    value = ModalityType.movement_integration_prep
                elif value == ActivityType.active_rest:
                    value = ModalityType.post_active_rest
                elif value == ActivityType.active_recovery:
                    value = ModalityType.active_recovery
                elif value == ActivityType.ice:
                    value = ModalityType.ice
                elif value == ActivityType.cold_water_immersion:
                    value = ModalityType.cold_water_immersion
                else:
                    value = ModalityType.post_active_rest
        super().__setattr__(name, value)

    def json_serialise(self, mobility_api=False, api=False, consolidated=False):
         return {
             "id": self.id,
             "type": self.type.value,
             "title": self.title,
             "when": self.when,
             "when_card": self.when_card,
             "start_date_time": format_datetime(self.start_date_time) if self.start_date_time is not None else None,
             "completed_date_time": format_datetime(self.completed_date_time) if self.completed_date_time is not None else None,
             "event_date_time": format_datetime(self.event_date_time) if self.event_date_time is not None else None,
             "completed" : self.completed,
             "active" : self.active,
             "default_plan": self.default_plan,
             "force_data": self.force_data,
             "goal_title": self.goal_title,  ## make dynamic based on selected routine
             "display_image": self.display_image,
             "locked_text": self.locked_text,
             # "goal_defs": [agd.json_serialise() for agd in self.goal_defs],
             "goals": {goal_text: goal.json_serialise() for (goal_text, goal) in self.goals.items()},
             "exercise_phases":[ex_phase.json_serialise(mobility_api=mobility_api, api=api, consolidated=consolidated) for ex_phase in self.exercise_phases],
             "source_training_session_id": self.source_training_session_id if self.source_training_session_id is not None else None
             }

    @classmethod
    def json_deserialise(cls, input_dict):
        modality_type = ModalityType(input_dict["type"])
        if modality_type == ModalityType.pre_active_rest:
            modality = ActiveRestBeforeTraining(event_date_time=input_dict.get('event_date_time'),
                                                force_data=input_dict.get('force_data', False))
        elif modality_type == ModalityType.post_active_rest:
            modality = ActiveRestAfterTraining(event_date_time=input_dict.get('event_date_time'),
                                               force_data=input_dict.get('force_data', False))
        elif modality_type == ModalityType.movement_integration_prep:
            modality = MovementIntegrationPrepModality(event_date_time=input_dict.get('event_date_time'),
                                                       force_data=input_dict.get('force_data', False))
        elif modality_type == ModalityType.active_recovery:
            modality = ActiveRecoveryModality(event_date_time=input_dict.get('event_date_time'))
        elif modality_type == ModalityType.warm_up:
            modality = WarmUp(event_date_time=input_dict.get('event_date_time'))
        elif modality_type == ModalityType.cool_down:
            modality = CoolDown(event_date_time=input_dict.get('event_date_time'))
        elif modality_type == ModalityType.functional_strength:
            modality = FunctionalStrength(event_date_time=input_dict.get('event_date_time'))
        else:
            raise ValueError("Unknown modality type")
        modality.id = input_dict.get("id")
        modality.start_date_time = input_dict.get('start_date_time', None)
        modality.completed_date_time = input_dict.get('completed_date_time', None)
        modality.event_date_time = input_dict.get('event_date_time', None)
        modality.completed = input_dict.get('completed', False)
        modality.active = input_dict.get('active', True)
        modality.default_plan = input_dict.get('default_plan', 'Complete')
        modality.force_data = input_dict.get('force_data', False)
        modality.goal_title = input_dict.get('goal_title', '')
        # modality.display_image = input_dict.get('display_image', '')
        # modality.locked_text = input_dict.get('locked_text', '')
        # modality.goal_defs = [AthleteGoalDef.json_deserialise(agd) for agd in input_dict.get('goal_defs', [])]
        modality.goals = {goal_type: ActivityGoal.json_deserialise(goal) for
                                 (goal_type, goal) in input_dict.get('goals', {}).items()}
        modality.exercise_phases = [ExercisePhase.json_deserialise(ex_phase) for ex_phase in input_dict.get('exercise_phases', [])]
        modality.source_training_session_id = input_dict.get('source_training_session_id')
        return modality

    # def __setattr__(self, name, value):
    #     if name in ['event_date_time', 'start_date_time', 'completed_date_time']:
    #         if value is not None and not isinstance(value, datetime.datetime):
    #             value = parse_datetime(value)
    #     if name == 'id' and value is None:
    #         value = str(uuid.uuid4())
    #     super().__setattr__(name, value)

    @abc.abstractmethod
    def fill_exercises(self, exercise_library, injury_risk_dict, sport_body_parts={}, high_intensity_session=False):
        pass

    # def get_total_exercises(self):
    #     total_exercises = 0
    #     for phase in self.exercise_phases:
    #         total_exercises += len(phase.exercises)
    #     return total_exercises

    # def initialize_dosage_durations(self):
    #
    #     self.dosage_durations[1] = DosageDuration(0, 0, 0)
    #     self.dosage_durations[2] = DosageDuration(0, 0, 0)
    #     self.dosage_durations[3] = DosageDuration(0, 0, 0)
    #     self.dosage_durations[4] = DosageDuration(0, 0, 0)
    #     self.dosage_durations[5] = DosageDuration(0, 0, 0)


    # @abc.abstractmethod
    # def conditions_for_increased_sensitivity_met(self, soreness_list, muscular_strain_high):
    #     return False

    # def reconcile_default_plan_with_active_time(self):
    #
    #     efficient_duration = self.dosage_durations[self.efficient_winner].efficient_duration
    #
    #     complete_duration = self.dosage_durations[self.complete_winner].complete_duration
    #
    #     if complete_duration == 0 and self.default_plan == "Complete":
    #         self.reactivate_complete_goals()
    #     elif efficient_duration == 0 and complete_duration == 0:
    #         self.reactivate_complete_goals()
    #         self.default_plan = "Complete"

    # def get_dosage_rank_and_progression(self, goal, severity, tier):
    #
    #     if goal.goal_type == AthleteGoalType.pain or goal.goal_type == AthleteGoalType.sore:
    #         if 7 <= severity:
    #             if tier == 1:
    #                 return 1, DosageProgression.mod_max_super_max
    #             else:
    #                 return 2, DosageProgression.mod_max_super_max
    #         elif 4 <= severity < 7:
    #             if tier == 1:
    #                 return 1, DosageProgression.mod_max_super_max
    #             else:
    #                 return 2, DosageProgression.mod_max_super_max
    #         else:
    #             if tier == 1:
    #                 return 2, DosageProgression.min_mod_max
    #             else:
    #                 return 3, DosageProgression.min_mod_max
    #
    #     elif goal.goal_type == AthleteGoalType.high_load or goal.goal_type == AthleteGoalType.expected_high_load:
    #         if tier == 1:
    #             return 1, DosageProgression.min_mod_max
    #         elif tier == 2:
    #             return 2, DosageProgression.min_mod_max
    #         elif tier == 3:
    #             return 3, DosageProgression.min_mod_max
    #         elif tier == 4:
    #             return 4, DosageProgression.min_mod_max
    #         elif tier == 5:
    #             return 5, DosageProgression.min_mod_max
    #         else:
    #             return 0, None
    #
    #     elif goal.goal_type == AthleteGoalType.asymmetric_session or goal.goal_type == AthleteGoalType.on_request or goal.goal_type == AthleteGoalType.expected_asymmetric_session:
    #         if tier == 1:
    #             return 1, DosageProgression.min_mod_max
    #         elif tier == 2:
    #             return 2, DosageProgression.min_mod_max
    #         elif tier == 3:
    #             return 3, DosageProgression.min_mod_max
    #         elif tier == 4:
    #             return 4, DosageProgression.min_mod_max
    #         elif tier == 5:
    #             return 5, DosageProgression.min_mod_max
    #         else:
    #             return 0, None
    #
    #     elif goal.goal_type == AthleteGoalType.corrective:
    #         if tier == 1:
    #             return 2, DosageProgression.min_mod_max
    #         elif tier == 2:
    #             return 3, DosageProgression.min_mod_max
    #         else:
    #             return 0, None
    #     else:
    #         return 0, None

    # def add_goals(self, dosages):
    #
    #     for dosage in dosages:
    #         if dosage.goal.text not in self.goals:
    #             if ((dosage.efficient_reps_assigned > 0 and dosage.efficient_sets_assigned > 0) or
    #                     (dosage.complete_reps_assigned > 0 and dosage.complete_sets_assigned > 0) or
    #                     (dosage.comprehensive_reps_assigned > 0 and dosage.comprehensive_sets_assigned > 0)):
    #                 self.goals[dosage.goal.text] = ModalityGoal()
    #
    # def update_goals(self, dosage):
    #
    #     if dosage.goal.text not in self.goals:
    #         if ((dosage.efficient_reps_assigned > 0 and dosage.efficient_sets_assigned > 0) or
    #                 (dosage.complete_reps_assigned > 0 and dosage.complete_sets_assigned > 0) or
    #                 (dosage.comprehensive_reps_assigned > 0 and dosage.comprehensive_sets_assigned > 0)):
    #             self.goals[dosage.goal.text] = ModalityGoal()
    #
    #     if dosage.efficient_reps_assigned > 0 and dosage.efficient_sets_assigned > 0:
    #         self.goals[dosage.goal.text].efficient_active = True
    #     if dosage.complete_reps_assigned > 0 and dosage.complete_sets_assigned > 0:
    #         self.goals[dosage.goal.text].complete_active = True
    #     if dosage.comprehensive_reps_assigned > 0 and dosage.comprehensive_sets_assigned > 0:
    #         self.goals[dosage.goal.text].comprehensive_active = True

    # def set_plan_dosage(self):
    #     if 1 not in self.rankings and 2 not in self.rankings:
    #         self.default_plan = "Efficient"
    #     else:
    #         self.default_plan = "Complete"

    # def copy_exercises(self, source_collection, target_phase, goal, tier, severity, exercise_library,
    #                    sports=[]):
    #
    #     position_order = 0
    #
    #     try:
    #         target_collection = [phase.exercises for phase in self.exercise_phases if phase.type==target_phase][0]
    #     except IndexError:
    #         print("phase not initialized")
    #         phase = ExercisePhase(target_phase)
    #         self.exercise_phases.append(phase)
    #         target_collection = phase.exercises
    #     for s in source_collection:
    #
    #         if s.exercise.id not in target_collection:
    #             target_collection[s.exercise.id] = AssignedExercise(library_id=str(s.exercise.id))
    #             exercise_list = [ex for ex in exercise_library if ex.id == str(s.exercise.id)]
    #             target_collection[s.exercise.id].exercise = exercise_list[0]
    #             target_collection[s.exercise.id].equipment_required = target_collection[
    #                 s.exercise.id].exercise.equipment_required
    #             target_collection[s.exercise.id].position_order = position_order
    #
    #         ranking, progression = self.get_dosage_rank_and_progression(goal, severity, tier)
    #
    #         if ranking > 0:
    #             self.rankings.add(ranking)
    #         dosage = ExerciseDosage()
    #         dosage.dosage_progression = progression
    #         dosage.tier = tier
    #         dosage.last_severity = severity
    #         dosage.ranking = ranking
    #         dosage.sports = sports
    #         dosage.goal = goal
    #         #dosage = self.update_dosage(dosage, target_collection[s.exercise.id].exercise)
    #         #if dosage.get_total_dosage() > 0:
    #         target_collection[s.exercise.id].dosages.append(dosage)
    #         position_order += 1

    # def aggregate_dosages(self):
    #     for phase in self.exercise_phases:
    #         self.aggregate_dosage_by_severity_exercise_collection(phase.exercises)
    #
    # def reactivate_complete_goals(self):
    #     for phase in self.exercise_phases:
    #         self.reactivate_complete_corrective_goals_by_collection(phase.exercises)
    #
    # def reactivate_complete_corrective_goals_by_collection(self, assigned_exercises):
    #
    #     for ex, a in assigned_exercises.items():
    #         for d in a.dosages:
    #             if d.goal.goal_type == AthleteGoalType.corrective:
    #                 d.complete_reps_assigned = d.default_complete_reps_assigned
    #                 d.complete_sets_assigned = d.default_complete_sets_assigned
    #                 self.update_goals(d)

    # def aggregate_dosage_by_severity_exercise_collection(self, assigned_exercises):
    #
    #     for ex, a in assigned_exercises.items():
    #         a.dosages = [dosage for dosage in a.dosages if isinstance(dosage.priority, str)]
    #         if len(a.dosages) > 0:
    #             a.dosages = sorted(a.dosages, key=lambda x: (3 - int(x.priority),
    #                                                          x.default_efficient_sets_assigned,
    #                                                          x.default_efficient_reps_assigned,
    #                                                          x.default_complete_sets_assigned,
    #                                                          x.default_complete_reps_assigned,
    #                                                          x.default_comprehensive_sets_assigned,
    #                                                          x.default_comprehensive_reps_assigned), reverse=True)
    #
    #             self.add_goals(a.dosages)
    #             dosage = a.dosages[0]
    #             for goal_dosage in a.dosages:
    #                 self.update_goals(goal_dosage)
    #
    #             if dosage.priority == "1":
    #                 self.calc_dosage_durations(1, a, dosage)
    #             elif dosage.priority == "2" and dosage.severity() > 4:
    #                 self.calc_dosage_durations(2, a, dosage)
    #             elif dosage.priority == "2" and dosage.severity() <= 4:
    #                 self.calc_dosage_durations(3, a, dosage)
    #             elif dosage.priority == "3" and dosage.severity() > 4:
    #                 self.calc_dosage_durations(4, a, dosage)
    #             elif dosage.priority == "3" and dosage.severity() <= 4:
    #                 self.calc_dosage_durations(5, a, dosage)


    # def set_winners(self):
    #
    #     # key off efficient as the guide
    #     total_efficient = 0
    #     total_complete = 0
    #     total_comprehensive = 0
    #     benchmarks = [1, 2, 3, 4, 5]
    #
    #     for b in range(0, len(benchmarks) - 1):
    #         total_efficient += self.dosage_durations[benchmarks[b]].efficient_duration
    #         #proposed_efficient = total_efficient + self.dosage_durations[benchmarks[b + 1]].efficient_duration
    #         proposed_efficient = self.dosage_durations[benchmarks[b + 1]].efficient_duration
    #         if 0 < proposed_efficient < 720:
    #             continue
    #         elif abs(total_efficient - 720) < abs(proposed_efficient - 720):
    #             self.efficient_winner = benchmarks[b]
    #             break
    #         else:
    #             self.efficient_winner = benchmarks[b + 1]
    #             break

        '''later
        for b in range(0, len(benchmarks) - 1):
            total_complete += self.dosage_durations[benchmarks[b]].complete_duration
            proposed_complete = total_complete + self.dosage_durations[benchmarks[b + 1]].complete_duration
            if proposed_complete < 900:
                continue
            elif abs(total_complete - 900) < abs(proposed_complete - 900):
                complete_winner = benchmarks[b]
                break
            else:
                complete_winner = benchmarks[b + 1]
                break

        for b in range(0, len(benchmarks) - 1):
            total_comprehensive += self.dosage_durations[benchmarks[b]].comprehensive_duration
            proposed_comprehensive = total_comprehensive + self.dosage_durations[benchmarks[b + 1]].comprehensive_duration
            if proposed_comprehensive < 1800:
                continue
            elif abs(total_comprehensive - 1800) < abs(proposed_comprehensive - 1000):
                comprehensive_winner = benchmarks[b]
                break
            else:
                comprehensive_winner = benchmarks[b + 1]
                break

        '''

    # def scale_all_active_time(self):
    #     for phase in self.exercise_phases:
    #         self.scale_active_time(phase.exercises)
    #
    # def scale_active_time(self, assigned_exercises):
    #
    #     if self.efficient_winner is not None:  # if None, don't reduce
    #         for ex, a in assigned_exercises.items():
    #             if len(a.dosages) > 0:
    #
    #                 if self.efficient_winner == 1:
    #                     for d in a.dosages:
    #                         if d.priority != '1':
    #                             d.efficient_reps_assigned = 0
    #                             d.efficient_sets_assigned = 0
    #                 elif self.efficient_winner == 2:
    #                     for d in a.dosages:
    #                         if d.priority == '3' or (d.priority == '2' and d.severity() <= 4):
    #                             d.efficient_reps_assigned = 0
    #                             d.efficient_sets_assigned = 0
    #                 elif self.efficient_winner == 3:
    #                     for d in a.dosages:
    #                         if d.priority == '3':
    #                             d.efficient_reps_assigned = 0
    #                             d.efficient_sets_assigned = 0
    #                 elif self.efficient_winner == 4:
    #                     for d in a.dosages:
    #                         if d.priority == '3' and d.severity() <= 4:
    #                             d.efficient_reps_assigned = 0
    #                             d.efficient_sets_assigned = 0
    #                 elif self.efficient_winner == 5:
    #                     pass
    #                 elif self.efficient_winner == 0:
    #                     pass

    # def calc_dosage_durations(self, benchmark_value, assigned_exercise, dosage):
    #     if dosage.efficient_reps_assigned is not None and dosage.efficient_sets_assigned is not None:
    #         self.dosage_durations[benchmark_value].efficient_duration += assigned_exercise.duration(
    #             dosage.efficient_reps_assigned, dosage.efficient_sets_assigned)
    #     if dosage.complete_reps_assigned is not None and dosage.complete_sets_assigned is not None:
    #         self.dosage_durations[benchmark_value].complete_duration += assigned_exercise.duration(
    #             dosage.complete_reps_assigned, dosage.complete_sets_assigned)
    #     if dosage.comprehensive_reps_assigned is not None and dosage.comprehensive_sets_assigned is not None:
    #         self.dosage_durations[benchmark_value].comprehensive_duration += assigned_exercise.duration(
    #             dosage.comprehensive_reps_assigned, dosage.comprehensive_sets_assigned)

    # def update_dosage(self, dosage, exercise):
    #     if dosage.goal.goal_type == AthleteGoalType.high_load or dosage.goal.goal_type == AthleteGoalType.asymmetric_session:
    #         if self.relative_load_level == 3:
    #             if dosage.priority == "1":
    #                 dosage.efficient_reps_assigned = exercise.min_reps
    #                 dosage.efficient_sets_assigned = 1
    #                 dosage.default_efficient_reps_assigned = exercise.min_reps
    #                 dosage.default_efficient_sets_assigned = 1
    #
    #             if dosage.priority == "1" or dosage.priority == "2":
    #                 dosage.complete_reps_assigned = exercise.min_reps
    #                 dosage.complete_sets_assigned = 1
    #                 dosage.default_complete_reps_assigned = exercise.min_reps
    #                 dosage.default_complete_sets_assigned = 1
    #
    #             dosage.comprehensive_reps_assigned = exercise.max_reps
    #             dosage.comprehensive_sets_assigned = 1
    #             dosage.default_comprehensive_reps_assigned = exercise.max_reps
    #             dosage.default_comprehensive_sets_assigned = 1
    #
    #         elif self.relative_load_level == 2:
    #             if dosage.priority == "1":
    #                 dosage.efficient_reps_assigned = exercise.min_reps
    #                 dosage.efficient_sets_assigned = 1
    #                 dosage.default_efficient_reps_assigned = exercise.min_reps
    #                 dosage.default_efficient_sets_assigned = 1
    #
    #             if dosage.priority == "1" or dosage.priority == "2":
    #                 dosage.complete_reps_assigned = exercise.min_reps
    #                 dosage.complete_sets_assigned = 1
    #                 dosage.default_complete_reps_assigned = exercise.min_reps
    #                 dosage.default_complete_sets_assigned = 1
    #
    #             dosage.comprehensive_reps_assigned = exercise.min_reps
    #             dosage.comprehensive_sets_assigned = 1
    #             dosage.default_comprehensive_reps_assigned = exercise.min_reps
    #             dosage.default_comprehensive_sets_assigned = 1
    #
    #         elif self.relative_load_level == 1:
    #             if dosage.priority == "1":
    #                 dosage.efficient_reps_assigned = exercise.max_reps
    #                 dosage.efficient_sets_assigned = 1
    #                 dosage.default_efficient_reps_assigned = exercise.max_reps
    #                 dosage.default_efficient_sets_assigned = 1
    #
    #             if dosage.priority == "1" or dosage.priority == "2":
    #                 dosage.complete_reps_assigned = exercise.max_reps
    #                 dosage.complete_sets_assigned = 1
    #                 dosage.default_complete_reps_assigned = exercise.max_reps
    #                 dosage.default_complete_sets_assigned = 1
    #
    #             dosage.comprehensive_reps_assigned = exercise.max_reps
    #             dosage.comprehensive_sets_assigned = 1
    #             dosage.default_comprehensive_reps_assigned = exercise.max_reps
    #             dosage.default_comprehensive_sets_assigned = 1
    #
    #     if dosage.goal.goal_type == AthleteGoalType.corrective:
    #         if dosage.priority == "1":
    #             dosage.efficient_reps_assigned = exercise.max_reps
    #             dosage.efficient_sets_assigned = 1
    #             dosage.default_efficient_reps_assigned = exercise.max_reps
    #             dosage.default_efficient_sets_assigned = 1
    #
    #         if dosage.priority == "1" or dosage.priority == "2":
    #             dosage.complete_reps_assigned = exercise.max_reps
    #             dosage.complete_sets_assigned = 1
    #             dosage.default_complete_reps_assigned = exercise.max_reps
    #             dosage.default_complete_sets_assigned = 1
    #
    #         dosage.comprehensive_reps_assigned = exercise.max_reps
    #         dosage.comprehensive_sets_assigned = 2
    #         dosage.default_comprehensive_reps_assigned = exercise.max_reps
    #         dosage.default_comprehensive_sets_assigned = 2
    #
    #     if dosage.goal.goal_type == AthleteGoalType.pain or dosage.goal.goal_type == AthleteGoalType.sore:
    #         if dosage.last_severity < 1.0:
    #             if dosage.priority == "1":
    #                 dosage.efficient_reps_assigned = exercise.min_reps
    #                 dosage.efficient_sets_assigned = 1
    #                 dosage.default_efficient_reps_assigned = exercise.min_reps
    #                 dosage.default_efficient_sets_assigned = 1
    #
    #                 dosage.complete_reps_assigned = exercise.max_reps
    #                 dosage.complete_sets_assigned = 1
    #                 dosage.default_complete_reps_assigned = exercise.max_reps
    #                 dosage.default_complete_sets_assigned = 1
    #
    #             if dosage.priority == "1" or dosage.priority == "2":
    #                 dosage.comprehensive_reps_assigned = exercise.min_reps
    #                 dosage.comprehensive_sets_assigned = 1
    #                 dosage.default_comprehensive_reps_assigned = exercise.min_reps
    #                 dosage.default_comprehensive_sets_assigned = 1
    #
    #         elif 1.0 <= dosage.last_severity < 3.0:
    #             if dosage.priority == "1":
    #                 dosage.efficient_reps_assigned = exercise.min_reps
    #                 dosage.efficient_sets_assigned = 1
    #                 dosage.default_efficient_reps_assigned = exercise.min_reps
    #                 dosage.default_efficient_sets_assigned = 1
    #             if dosage.priority == "1" or dosage.priority == "2":
    #                 dosage.complete_reps_assigned = exercise.min_reps
    #                 dosage.complete_sets_assigned = 1
    #                 dosage.default_complete_reps_assigned = exercise.min_reps
    #                 dosage.default_complete_sets_assigned = 1
    #
    #                 dosage.comprehensive_reps_assigned = exercise.max_reps
    #                 dosage.comprehensive_sets_assigned = 1
    #                 dosage.default_comprehensive_reps_assigned = exercise.max_reps
    #                 dosage.default_comprehensive_sets_assigned = 1
    #         elif 3 <= dosage.last_severity < 5:
    #             if dosage.priority == "1":
    #                 dosage.efficient_reps_assigned = exercise.min_reps
    #                 dosage.efficient_sets_assigned = 1
    #                 dosage.default_efficient_reps_assigned = exercise.min_reps
    #                 dosage.default_efficient_sets_assigned = 1
    #             if dosage.priority == "1" or dosage.priority == "2":
    #                 dosage.complete_reps_assigned = exercise.min_reps
    #                 dosage.complete_sets_assigned = 1
    #                 dosage.default_complete_reps_assigned = exercise.min_reps
    #                 dosage.default_complete_sets_assigned = 1
    #
    #             dosage.comprehensive_reps_assigned = exercise.min_reps
    #             dosage.comprehensive_sets_assigned = 1
    #             dosage.default_comprehensive_reps_assigned = exercise.min_reps
    #             dosage.default_comprehensive_sets_assigned = 1
    #         elif 5 <= dosage.last_severity < 7:
    #             if dosage.priority == "1" or dosage.priority == "2":
    #                 dosage.efficient_reps_assigned = exercise.min_reps
    #                 dosage.efficient_sets_assigned = 1
    #                 dosage.default_efficient_reps_assigned = exercise.min_reps
    #                 dosage.default_efficient_sets_assigned = 1
    #             # trial
    #             dosage.complete_reps_assigned = exercise.min_reps
    #             dosage.complete_sets_assigned = 1
    #             dosage.default_complete_reps_assigned = exercise.min_reps
    #             dosage.default_complete_sets_assigned = 1
    #             dosage.comprehensive_reps_assigned = exercise.max_reps
    #             dosage.comprehensive_sets_assigned = 1
    #             dosage.default_comprehensive_reps_assigned = exercise.max_reps
    #             dosage.default_comprehensive_sets_assigned = 1
    #         elif 7 <= dosage.last_severity < 9:
    #             dosage.efficient_reps_assigned = exercise.min_reps
    #             dosage.efficient_sets_assigned = 1
    #             dosage.complete_reps_assigned = exercise.max_reps
    #             dosage.complete_sets_assigned = 1
    #             dosage.comprehensive_reps_assigned = exercise.max_reps
    #             dosage.comprehensive_sets_assigned = 2
    #             dosage.default_efficient_reps_assigned = exercise.min_reps
    #             dosage.default_efficient_sets_assigned = 1
    #             dosage.default_complete_reps_assigned = exercise.max_reps
    #             dosage.default_complete_sets_assigned = 1
    #             dosage.default_comprehensive_reps_assigned = exercise.max_reps
    #             dosage.default_comprehensive_sets_assigned = 2
    #         elif dosage.last_severity >= 9:
    #             dosage.efficient_reps_assigned = exercise.max_reps
    #             dosage.efficient_sets_assigned = 1
    #
    #             dosage.complete_reps_assigned = exercise.max_reps
    #             dosage.complete_sets_assigned = 2
    #             dosage.comprehensive_reps_assigned = exercise.max_reps
    #             dosage.comprehensive_sets_assigned = 3
    #             dosage.default_efficient_reps_assigned = exercise.max_reps
    #             dosage.default_efficient_sets_assigned = 1
    #
    #             dosage.default_complete_reps_assigned = exercise.max_reps
    #             dosage.default_complete_sets_assigned = 2
    #             dosage.default_comprehensive_reps_assigned = exercise.max_reps
    #             dosage.default_comprehensive_sets_assigned = 3
    #
    #     elif dosage.goal.goal_type == AthleteGoalType.on_request:
    #         if dosage.priority == "1":
    #             dosage.efficient_reps_assigned = exercise.min_reps
    #             dosage.efficient_sets_assigned = 1
    #             dosage.default_efficient_reps_assigned = exercise.min_reps
    #             dosage.default_efficient_sets_assigned = 1
    #
    #             dosage.complete_reps_assigned = exercise.max_reps
    #             dosage.complete_sets_assigned = 1
    #             dosage.default_complete_reps_assigned = exercise.max_reps
    #             dosage.default_complete_sets_assigned = 1
    #
    #         if dosage.priority == "1" or dosage.priority == "2":
    #
    #             dosage.comprehensive_reps_assigned = exercise.min_reps
    #             dosage.comprehensive_sets_assigned = 1
    #             dosage.default_comprehensive_reps_assigned = exercise.min_reps
    #             dosage.default_comprehensive_sets_assigned = 1
    #
    #     return dosage

    # @staticmethod
    # def rank_dosages(target_collections):
    #     for target_collection in target_collections:
    #         for ex in target_collection.values():
    #             ex.set_dosage_ranking()
    #
    # def prioritize_dosages(self, exercise_collection, target_ranking, priority):
    #     for exercise_int, assigned_exercise in exercise_collection.items():
    #         for dosage in assigned_exercise.dosages:
    #             if dosage.ranking == target_ranking:
    #                 dosage.priority = str(priority)
    #                 dosage.set_reps_and_sets(assigned_exercise.exercise)
    #
    # def set_exercise_dosage_ranking(self):
    #     ordered_ranks = sorted(self.rankings)
    #     rank_max = min(3, len(ordered_ranks))
    #     for r in range(0, rank_max):
    #         current_ranking = ordered_ranks[r]
    #         for phase in self.exercise_phases:
    #             self.prioritize_dosages(phase.exercises, current_ranking, r + 1)


# class ActiveRest(Modality):
#     def __init__(self, event_date_time, modality_type, force_data=False, relative_load_level=3, force_on_demand=False, sport_cardio_plyometrics=False):
#         super().__init__(event_date_time, modality_type, relative_load_level)
#         self.force_data = force_data
#         self.force_on_demand = force_on_demand
#         self.sport_cardio_plyometrics = sport_cardio_plyometrics
#
#     @abc.abstractmethod
#     def check_recovery(self, body_part_side, body_part_injury_risk, exercise_library, max_severity, sport_body_parts):
#         pass
#
#     @abc.abstractmethod
#     def check_care(self, body_part_side, body_part_injury_risk, exercise_library, max_severity):
#         pass
#
#     @abc.abstractmethod
#     def check_prevention(self, body_part_side, body_part_injury_risk, exercise_library, max_severity, sport_body_parts):
#         pass
#
#     def conditions_for_increased_sensitivity_met(self, soreness_list, muscular_strain_high):
#
#         if muscular_strain_high:
#             return True
#         else:
#             for s in soreness_list:
#                 if (s.first_reported_date_time is not None and
#                         (s.is_persistent_soreness() or
#                          s.historic_soreness_status == HistoricSorenessStatus.persistent_2_soreness)):
#                     days_sore = (self.event_date_time - s.first_reported_date_time).days
#                     if days_sore < 30:
#                         return True
#         return False
#
#     def is_body_part_overactive_short(self, body_part_injury_risk):
#
#         #is_short = self.is_body_part_short(body_part_injury_risk)
#
#         is_overactive_short = False
#
#         if body_part_injury_risk.overactive_short_count_last_0_20_days >= 3:
#             is_overactive_short = True
#
#         return is_overactive_short
#
#     def is_body_part_overactive_long(self, body_part_injury_risk):
#         is_overactive_long = False
#
#         if body_part_injury_risk.overactive_long_count_last_0_20_days >= 3:
#             is_overactive_long = True
#
#         return is_overactive_long
#
#     def is_body_part_underactive_long(self, body_part_injury_risk):
#         is_underactive_long = False
#
#         if body_part_injury_risk.underactive_long_count_last_0_20_days >= 3:
#             is_underactive_long = True
#
#         return is_underactive_long
#
#     def is_body_part_underactive_short(self, body_part_injury_risk):
#         is_underactive_short = False
#
#         if body_part_injury_risk.underactive_short_count_last_0_20_days >= 3:
#             is_underactive_short = True
#
#         return is_underactive_short
#
#     def is_body_part_long(self, body_part_injury_risk):
#
#         is_short = False
#
#         if body_part_injury_risk.long_count_last_0_20_days >= 3:
#             is_short = True
#         return is_short
#
#     def is_body_part_short(self, body_part_injury_risk):
#
#         is_short = False
#
#         if body_part_injury_risk.knots_count_last_0_20_days >= 3:
#             is_short = True
#         if body_part_injury_risk.tight_count_last_0_20_days >= 3:
#             is_short = True
#         if body_part_injury_risk.sharp_count_last_0_20_days >= 3:
#             is_short = True
#         if body_part_injury_risk.ache_count_last_0_20_days >= 4:
#             is_short = True
#         if body_part_injury_risk.short_count_last_0_20_days >= 3:
#             is_short = True
#         return is_short
#
#     def is_body_part_weak(self, body_part_injury_risk):
#
#         is_weak = False
#
#         if body_part_injury_risk.weak_count_last_0_20_days >= 3:
#             is_weak = True
#
#         return is_weak
#
#     def is_functional_overreaching(self, body_part_injury_risk):
#         if (body_part_injury_risk.last_functional_overreaching_date is not None and
#               body_part_injury_risk.last_functional_overreaching_date == self.event_date_time.date()):
#             return True
#         else:
#             return False
#
#     def is_non_functional_overreaching(self, body_part_injury_risk):
#
#         two_days_ago = self.event_date_time.date() - datetime.timedelta(days=1)
#
#         if (body_part_injury_risk.last_non_functional_overreaching_date is not None and
#               body_part_injury_risk.last_non_functional_overreaching_date >= two_days_ago):
#             return True
#         else:
#             return False
#
#     def is_excessive_strain(self, body_part_injury_risk):
#
#         two_days_ago = self.event_date_time.date() - datetime.timedelta(days=1)
#
#         if (body_part_injury_risk.last_excessive_strain_date is not None and
#                 body_part_injury_risk.last_excessive_strain_date == self.event_date_time.date()):
#             return True
#         elif (body_part_injury_risk.last_excessive_strain_date is not None and
#               body_part_injury_risk.last_non_functional_overreaching_date is not None and
#               body_part_injury_risk.last_non_functional_overreaching_date >= two_days_ago):
#             return True
#         else:
#             return False
#
#     def fill_exercises(self, exercise_library, injury_risk_dict, sport_body_parts=None, high_intensity_session=False):
#
#         max_severity = 0
#         for body_part, body_part_injury_risk in injury_risk_dict.items():
#             if (body_part_injury_risk.last_sharp_level > 0 and body_part_injury_risk.last_sharp_date is not None
#                     and body_part_injury_risk.last_sharp_date == self.event_date_time.date()):
#                 max_severity = max(max_severity, body_part_injury_risk.last_sharp_level)
#             if (body_part_injury_risk.last_ache_level > 0 and body_part_injury_risk.last_ache_date is not None
#                     and body_part_injury_risk.last_ache_date == self.event_date_time.date()):
#                 max_severity = max(max_severity, body_part_injury_risk.last_ache_level)
#
#         if self.force_data:
#             self.get_general_exercises(exercise_library, max_severity)
#         else:
#             if len(injury_risk_dict) > 0:
#                 for body_part, body_part_injury_risk in injury_risk_dict.items():
#                     self.check_recovery(body_part, body_part_injury_risk, exercise_library, max_severity, sport_body_parts)
#                     self.check_care(body_part, body_part_injury_risk, exercise_library, max_severity)
#                     self.check_prevention(body_part, body_part_injury_risk, exercise_library, max_severity, sport_body_parts)
#             else:
#                 if self.force_on_demand:
#                     self.get_general_exercises(exercise_library, max_severity)
#
#     def get_last_severity(self, body_part_injury_risk):
#
#         last_severity = 0
#
#         if (body_part_injury_risk.last_sharp_level > 0 and body_part_injury_risk.last_sharp_date is not None
#                 and body_part_injury_risk.last_sharp_date == self.event_date_time.date()):
#             last_severity = max(last_severity, body_part_injury_risk.last_sharp_level)
#         if (body_part_injury_risk.last_ache_level > 0 and body_part_injury_risk.last_ache_date is not None
#                 and body_part_injury_risk.last_ache_date == self.event_date_time.date()):
#             last_severity = max(last_severity, body_part_injury_risk.last_ache_level)
#         if (body_part_injury_risk.last_tight_level > 0 and body_part_injury_risk.last_tight_date is not None
#                 and body_part_injury_risk.last_tight_date == self.event_date_time.date()):
#             last_severity = max(last_severity, body_part_injury_risk.last_tight_level)
#         if (body_part_injury_risk.last_knots_level > 0 and body_part_injury_risk.last_knots_date is not None
#                 and body_part_injury_risk.last_knots_date == self.event_date_time.date()):
#             last_severity = max(last_severity, body_part_injury_risk.last_knots_level)
#
#         return last_severity
#
#     def get_general_exercises(self, exercise_library, max_severity):
#
#         pass
#
#     def check_reactive_recover_from_sport_general(self, sports, exercise_library, goal, max_severity):
#
#         pass
#
#     def check_reactive_recover_from_sport(self, trigger_list, exercise_library, sports, max_severity):
#
#
#         for t in range(0, len(trigger_list)):
#             if trigger_list[t].trigger_type == TriggerType.high_volume_intensity:  # 0
#                 goal = AthleteGoal("High Load", 1, AthleteGoalType.high_load)
#                 body_part_factory = BodyPartFactory()
#
#                 body_part = body_part_factory.get_body_part_for_sports(sports)
#
#                 # Note: this is just returning the primary mover related exercises for sport
#                 if body_part is not None:  # and not prohibiting_soreness:
#                     self.copy_exercises(body_part.inhibit_exercises,
#                                         ExercisePhaseType.inhibit, goal, "1", trigger_list[t], exercise_library)
#                     # if not prohibiting_soreness:
#                     if max_severity < 7:
#                         self.copy_exercises(body_part.static_stretch_exercises,
#                                             ExercisePhaseType.static_stretch, goal, "1", trigger_list[t], exercise_library,
#                                             sports)
#                     if max_severity < 5:
#                         self.copy_exercises(body_part.isolated_activate_exercises,
#                                             ExercisePhaseType.isolated_activate, goal, "1", trigger_list[t],
#                                             exercise_library, sports)
#
#                 self.check_reactive_recover_from_sport_general(sports, exercise_library, goal, max_severity)


class ActiveRestBeforeTraining(ActiveRestBase, Modality):
    def __init__(self, event_date_time, force_data=False, relative_load_level=3, force_on_demand=False):
        super().__init__(event_date_time, ModalityType.pre_active_rest, force_data, relative_load_level, force_on_demand, possible_benchmarks=63)
        self.exercise_phases = [ExercisePhase(ExercisePhaseType.inhibit),
                                ExercisePhase(ExercisePhaseType.static_stretch),
                                ExercisePhase(ExercisePhaseType.active_stretch),
                                ExercisePhase(ExercisePhaseType.isolated_activate),
                                ExercisePhase(ExercisePhaseType.static_integrate)]
        self.when = "before training"
        self.when_card = "before training"
        self.display_image = "inhibit"  # do not include .png or _activity or _tab
        self.locked_text = "Sorry, you missed the optimal window for Mobilize today."

        self.proposed_efficient_limit = 300
        self.proposed_complete_limit = 600
        self.proposed_comprehensive_limit = 900
        self.ranked_exercise_phases = {
                'isolated_activate': 0,
                'static_stretch': 1,
                'active_stretch': 2,
                'dynamic_stretch': 3,
                'inhibit': 4,
                'static_integrate': 5,
                'dynamic_integrate': 6
            }
        self.ranked_goals = {
                "care": 0,
                "prevention": 1,
                "recovery": 2
            }

    def check_reactive_recover_from_sport_general(self, sports, exercise_library, goal, max_severity):

        body_part_factory = BodyPartFactory()

        body_part = body_part_factory.get_body_part_for_sports(sports)

        for a in body_part.agonists:
            agonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(a), None))
            if agonist is not None:
                self.copy_exercises(agonist.inhibit_exercises, ExercisePhaseType.inhibit, goal, "1", None,
                                    exercise_library)
                # self.copy_exercises(agonist.static_stretch_exercises, ExercisePhaseType.static_stretch, goal, "1",
                #                    None, exercise_library)
                if max_severity < 7:
                    self.copy_exercises(agonist.active_stretch_exercises, ExercisePhaseType.active_stretch, goal, "1",
                                        None, exercise_library)

        if max_severity < 5:
            for t in body_part.antagonists:
                antagonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(t), None))
                if antagonist is not None:
                    self.copy_exercises(antagonist.isolated_activate_exercises, ExercisePhaseType.isolated_activate, goal,
                                        "1",
                                        None, exercise_library)

        if max_severity < 5:
            self.copy_exercises(body_part.static_integrate_exercises, ExercisePhaseType.static_integrate, goal, "1", None,
                                exercise_library)

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

        '''
        for g in body_part.antagonists:
                antagonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(g), None))
                if antagonist is not None:
                    self.copy_exercises(antagonist.inhibit_exercises, ExercisePhaseType.inhibit, goal, "1", None,
                                        exercise_library)
                    self.copy_exercises(antagonist.static_stretch_exercises, ExercisePhaseType.static_stretch, goal,
                                        "1", None, exercise_library)
                    self.copy_exercises(antagonist.active_stretch_exercises, ExercisePhaseType.active_stretch, goal,
                                        "1", None, exercise_library)
        '''

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

    def check_recovery(self, body_part, body_part_injury_risk, exercise_library, max_severity, sport_body_parts):
        compensating = False
        high_load = False

        if body_part is not None:

            if 0 < body_part_injury_risk.total_volume_percent_tier < 6:
                high_load = True

            if (body_part_injury_risk.last_movement_dysfunction_stress_date is not None and
                    body_part_injury_risk.last_movement_dysfunction_stress_date == self.event_date_time.date()):

                compensating = True
                body_part_injury_risk.total_compensation_percent_tier = 1
            elif (body_part_injury_risk.last_compensation_date is not None
                  and body_part_injury_risk.last_compensation_date == self.event_date_time.date() and
                  0 < body_part_injury_risk.total_compensation_percent_tier < 6):

                compensating = True

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
                        self.copy_exercises(body_part.active_stretch_exercises, ExercisePhaseType.active_stretch, goal,
                                            tier, 0, exercise_library)

            if high_load:

                if max_severity < 5.0:
                    self.copy_exercises(body_part.isolated_activate_exercises, ExercisePhaseType.isolated_activate, goal,
                                        body_part_injury_risk.total_volume_percent_tier,
                                        0, exercise_library)

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

            body_part_factory = BodyPartFactory()

            for s in body_part.synergists:
                synergist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(s), None))
                self.copy_exercises(synergist.inhibit_exercises, ExercisePhaseType.inhibit, goal, 2, last_severity,
                                    exercise_library)

                if max_severity < 7.0:
                    self.copy_exercises(synergist.active_stretch_exercises, ExercisePhaseType.active_stretch, goal, 2,
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
        if body_part is not None:

            is_short = self.is_body_part_short(body_part_injury_risk)
            is_overactive_short = self.is_body_part_overactive_short(body_part_injury_risk)
            is_overactive_long = self.is_body_part_overactive_long(body_part_injury_risk)
            is_underactive_long = self.is_body_part_underactive_long(body_part_injury_risk)
            is_underactive_short = self.is_body_part_underactive_short(body_part_injury_risk)
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
                    self.copy_exercises(body_part.active_stretch_exercises, ExercisePhaseType.active_stretch, goal, 1, 0, exercise_library)
                if max_severity < 5.0:
                    self.copy_exercises(body_part.isolated_activate_exercises, ExercisePhaseType.isolated_activate, goal, 1, 0, exercise_library)

            elif is_short:
                goal = AthleteGoal("Reduce injury risks", 1, AthleteGoalType.corrective)
                tier_one = True
                self.copy_exercises(body_part.inhibit_exercises, ExercisePhaseType.inhibit, goal, 2, 0, exercise_library)

                if max_severity < 7.0:
                    self.copy_exercises(body_part.static_stretch_exercises, ExercisePhaseType.static_stretch, goal, 2,
                                        0, exercise_library)

            if not tier_one and body_part_injury_risk.limited_mobility_tier == 2:
                goal = AthleteGoal("Reduce injury risks", 1, AthleteGoalType.corrective)

                self.copy_exercises(body_part.inhibit_exercises, ExercisePhaseType.inhibit, goal, 2,
                                    0, exercise_library)

                if max_severity < 7.0:
                    self.copy_exercises(body_part.static_stretch_exercises, ExercisePhaseType.static_stretch, goal, 2, 0, exercise_library)
            if not tier_one and body_part_injury_risk.underactive_weak_tier == 2:

                goal = AthleteGoal("Reduce injury risks", 1, AthleteGoalType.corrective)

                if max_severity < 5.0:
                    self.copy_exercises(body_part.isolated_activate_exercises, ExercisePhaseType.isolated_activate, goal,
                                        2, 0, exercise_library)

    def set_exercise_dosage_ranking(self):
        ordered_ranks = sorted(self.rankings)
        rank_max = min(3, len(ordered_ranks))
        for r in range(0, rank_max):
            current_ranking = ordered_ranks[r]
            for phase in self.exercise_phases:
                self.prioritize_dosages(phase.exercises, current_ranking, r + 1)


class ActiveRestAfterTraining(ActiveRest, Modality):
    def __init__(self, event_date_time, force_data=False, relative_load_level=3, force_on_demand=False):
        # super().__init__(event_date_time, ModalityType.post_active_rest, force_data, relative_load_level,
        #                  force_on_demand)
        super().__init__(event_date_time, force_data, relative_load_level, force_on_demand)
        self.when = "anytime, up to 3 per day"
        self.when_card = "anytime"
        self.display_image = "static_stretch"   # do not include .png or _activity or _tab
        self.locked_text = "Mobility Workout missed. Tap + to create another."
        self.ranked_exercise_phases = {
                'inhibit': 0,
                'static_stretch': 1,
                'isolated_activate': 2,
                'static_integrate': 3
            }
        self.ranked_goals = {
                "care": 0,
                "recovery": 1,
                "prevention": 2
            }

#
# class ActiveRestAfterTraining(ActiveRestBase, Modality):
#     def __init__(self, event_date_time, force_data=False, relative_load_level=3, force_on_demand=False):
#         super().__init__(event_date_time, ModalityType.post_active_rest, force_data, relative_load_level, force_on_demand)
#         self.exercise_phases = [ExercisePhase(ExercisePhaseType.inhibit),
#                                 ExercisePhase(ExercisePhaseType.static_stretch),
#                                 ExercisePhase(ExercisePhaseType.isolated_activate),
#                                 ExercisePhase(ExercisePhaseType.static_integrate)]
#         self.when = "anytime, up to 3 per day"
#         self.when_card = "anytime"
#         self.display_image = "static_stretch"   # do not include .png or _activity or _tab
#         self.locked_text = "You skipped this Mobility Workout. Tap + to create another."
#
#     def check_reactive_recover_from_sport_general(self, sports, exercise_library, goal, max_severity):
#
#         goal = AthleteGoal("High Load", 1, AthleteGoalType.high_load)
#
#         body_part_factory = BodyPartFactory()
#
#         body_part = body_part_factory.get_body_part_for_sports(sports)
#
#         for a in body_part.agonists:
#             agonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(a), None))
#             if agonist is not None:
#                 if max_severity < 7.0:
#                     self.copy_exercises(agonist.inhibit_exercises, ExercisePhaseType.inhibit, goal, "1", None,
#                                         exercise_library)
#                     self.copy_exercises(agonist.static_stretch_exercises, ExercisePhaseType.static_stretch, goal, "1",
#                                         None, exercise_library)
#
#         for t in body_part.antagonists:
#             antagonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(t), None))
#             if antagonist is not None:
#                 if max_severity < 5.0:
#                     self.copy_exercises(antagonist.isolated_activate_exercises, ExercisePhaseType.isolated_activate, goal,
#                                         "1",
#                                         None, exercise_library)
#
#         if max_severity < 5.0:
#             self.copy_exercises(body_part.static_integrate_exercises, ExercisePhaseType.static_integrate, goal, "1", None,
#                                 exercise_library)
#
#     def get_general_exercises(self, exercise_library, max_severity):
#
#         body_part_factory = BodyPartFactory()
#
#         body_part = body_part_factory.get_general()
#
#         goal = AthleteGoal("Improve mobility", 1, AthleteGoalType.on_request)
#
#         for a in body_part.agonists:
#             agonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(a), None))
#             if agonist is not None:
#                 self.copy_exercises(agonist.inhibit_exercises, ExercisePhaseType.inhibit, goal, 1, 0,
#                                     exercise_library)
#                 if max_severity < 7:
#                     self.copy_exercises(agonist.static_stretch_exercises, ExercisePhaseType.static_stretch, goal, 1,
#                                         0, exercise_library)
#                 if max_severity < 5:
#                     self.copy_exercises(agonist.isolated_activate_exercises, ExercisePhaseType.isolated_activate, goal,
#                                         1, 0, exercise_library)
#
#         for y in body_part.synergists:
#             synergist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(y), None))
#             if synergist is not None:
#                 self.copy_exercises(synergist.inhibit_exercises, ExercisePhaseType.inhibit, goal, 2, 0,
#                                     exercise_library)
#                 if max_severity < 7.0:
#                     self.copy_exercises(synergist.static_stretch_exercises, ExercisePhaseType.static_stretch, goal, 2,
#                                         0, exercise_library)
#                 if max_severity < 5.0:
#                     self.copy_exercises(synergist.isolated_activate_exercises, ExercisePhaseType.isolated_activate, goal,
#                                         2, 0, exercise_library)
#
#         for t in body_part.stabilizers:
#             stabilizer = body_part_factory.get_body_part(BodyPart(BodyPartLocation(t), None))
#             if stabilizer is not None:
#                 self.copy_exercises(stabilizer.inhibit_exercises, ExercisePhaseType.inhibit, goal, 3, 0,
#                                     exercise_library)
#                 if max_severity < 7.0:
#                     self.copy_exercises(stabilizer.static_stretch_exercises, ExercisePhaseType.static_stretch, goal, 3,
#                                         0, exercise_library)
#                 if max_severity < 5.0:
#                     self.copy_exercises(stabilizer.isolated_activate_exercises, ExercisePhaseType.isolated_activate, goal,
#                                         3, 0, exercise_library)
#
#         if max_severity < 5.0:
#             self.copy_exercises(body_part.static_integrate_exercises, ExercisePhaseType.static_integrate, goal, 1, 0,
#                                 exercise_library)
#
#     def check_recovery(self, body_part, body_part_injury_risk, exercise_library, max_severity, sport_body_parts):
#         compensating = False
#         high_load = False
#
#         if body_part is not None:
#
#             if 0 < body_part_injury_risk.total_volume_percent_tier < 6:
#                 high_load = True
#
#             if (body_part_injury_risk.last_movement_dysfunction_stress_date is not None and
#                     body_part_injury_risk.last_movement_dysfunction_stress_date == self.event_date_time.date()):
#
#                 compensating = True
#                 body_part_injury_risk.total_compensation_percent_tier = 1
#             elif (body_part_injury_risk.last_compensation_date is not None
#                   and body_part_injury_risk.last_compensation_date == self.event_date_time.date() and
#                   0 < body_part_injury_risk.total_compensation_percent_tier < 6):
#
#                 compensating = True
#
#             goal = AthleteGoal("Recover from training", 1, AthleteGoalType.high_load)
#
#             if high_load or compensating:
#
#                 high_load_tier = 0
#                 comp_tier = 0
#                 tier = 0
#
#                 if high_load:
#                     high_load_tier = body_part_injury_risk.total_volume_percent_tier
#                 if compensating:
#                     comp_tier = body_part_injury_risk.total_compensation_percent_tier
#
#                 if high_load_tier > 0 and comp_tier > 0:
#                     tier = min(high_load_tier, comp_tier)
#                 elif high_load_tier > 0:
#                     tier = high_load_tier
#                 elif comp_tier > 0:
#                     tier = comp_tier
#
#                 if tier > 0:
#                     self.copy_exercises(body_part.inhibit_exercises, ExercisePhaseType.inhibit, goal,
#                                         tier, 0, exercise_library)
#
#                     if max_severity < 7.0:
#                         self.copy_exercises(body_part.static_stretch_exercises, ExercisePhaseType.static_stretch, goal,
#                                             tier, 0, exercise_library)
#
#             if high_load:
#
#                 if max_severity < 5.0:
#                     self.copy_exercises(body_part.isolated_activate_exercises, ExercisePhaseType.isolated_activate, goal,
#                                         body_part_injury_risk.total_volume_percent_tier,
#                                         0, exercise_library)
#
#     def check_care(self, body_part, body_part_injury_risk, exercise_library, max_severity):
#         muscle_spasm = False
#         knots = False
#         inflammation = False
#
#         if (body_part_injury_risk.last_inflammation_date is not None and
#                 body_part_injury_risk.last_inflammation_date == self.event_date_time.date()):
#             inflammation = True
#
#         if (body_part_injury_risk.last_muscle_spasm_date is not None and
#                 body_part_injury_risk.last_muscle_spasm_date == self.event_date_time.date()):
#             muscle_spasm = True
#
#         if (body_part_injury_risk.last_knots_date is not None and
#                 body_part_injury_risk.last_knots_date == self.event_date_time.date()):
#             knots = True
#
#         goal = AthleteGoal("Care for symptoms", 1, AthleteGoalType.sore)
#
#         if muscle_spasm or knots or inflammation:
#
#             last_severity = 0
#
#             if muscle_spasm:
#                 last_severity = max(last_severity, body_part_injury_risk.get_muscle_spasm_severity(self.event_date_time.date()))
#             if knots:
#                 last_severity = max(last_severity, body_part_injury_risk.get_knots_severity(self.event_date_time.date()))
#             if inflammation:
#                 last_severity = max(last_severity, body_part_injury_risk.get_inflammation_severity(self.event_date_time.date()))
#
#             self.copy_exercises(body_part.inhibit_exercises, ExercisePhaseType.inhibit, goal, 1, last_severity,
#                                 exercise_library)
#
#             if max_severity < 7.0:
#                 self.copy_exercises(body_part.static_stretch_exercises, ExercisePhaseType.static_stretch, goal, 1,
#                                     last_severity, exercise_library)
#
#             body_part_factory = BodyPartFactory()
#
#             for s in body_part.synergists:
#                 synergist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(s), None))
#                 self.copy_exercises(synergist.inhibit_exercises, ExercisePhaseType.inhibit, goal, 2, last_severity,
#                                     exercise_library)
#
#                 if max_severity < 7.0:
#                     self.copy_exercises(synergist.static_stretch_exercises, ExercisePhaseType.static_stretch, goal, 2,
#                                         last_severity, exercise_library)
#
#     def check_prevention(self, body_part, body_part_injury_risk, exercise_library, max_severity, sport_body_parts):
#
#         if body_part is not None:
#
#             is_short = self.is_body_part_short(body_part_injury_risk)
#             is_overactive_short = self.is_body_part_overactive_short(body_part_injury_risk)
#             is_overactive_long = self.is_body_part_overactive_long(body_part_injury_risk)
#             is_underactive_short = self.is_body_part_underactive_short(body_part_injury_risk)
#             is_underactive_long = self.is_body_part_underactive_long(body_part_injury_risk)
#             is_weak = self.is_body_part_weak(body_part_injury_risk)
#             tier_one = False
#
#             if is_overactive_short:
#
#                 goal = AthleteGoal("Reduce injury risks", 1, AthleteGoalType.corrective)
#                 tier_one = True
#                 self.copy_exercises(body_part.inhibit_exercises, ExercisePhaseType.inhibit, goal, 1, 0, exercise_library)
#
#                 if max_severity < 7.0:
#                     self.copy_exercises(body_part.static_stretch_exercises, ExercisePhaseType.static_stretch, goal, 1,
#                                         0, exercise_library)
#
#             elif is_underactive_long or is_weak:
#
#                 goal = AthleteGoal("Reduce injury risks", 1, AthleteGoalType.corrective)
#                 tier_one = True
#                 if max_severity < 5.0:
#                     self.copy_exercises(body_part.isolated_activate_exercises, ExercisePhaseType.isolated_activate, goal, 1,
#                                         0, exercise_library)
#
#             elif is_overactive_long:
#
#                 goal = AthleteGoal("Reduce injury risks", 1, AthleteGoalType.corrective)
#                 tier_one = True
#                 self.copy_exercises(body_part.inhibit_exercises, ExercisePhaseType.inhibit, goal, 1, 0, exercise_library)
#
#             elif is_underactive_short:
#
#                 goal = AthleteGoal("Reduce injury risks", 1, AthleteGoalType.corrective)
#                 tier_one = True
#                 self.copy_exercises(body_part.inhibit_exercises, ExercisePhaseType.inhibit, goal, 1, 0, exercise_library)
#
#                 if max_severity < 7.0:
#                     self.copy_exercises(body_part.static_stretch_exercises, ExercisePhaseType.static_stretch, goal, 1, 0, exercise_library)
#
#                 if max_severity < 5.0:
#                     self.copy_exercises(body_part.isolated_activate_exercises, ExercisePhaseType.isolated_activate, goal,
#                                         1, 0, exercise_library)
#
#             elif is_short:
#
#                 goal = AthleteGoal("Reduce injury risks", 1, AthleteGoalType.corrective)
#                 tier_one = True
#                 self.copy_exercises(body_part.inhibit_exercises, ExercisePhaseType.inhibit, goal, 2, 0, exercise_library)
#
#                 if max_severity < 7.0:
#                     self.copy_exercises(body_part.static_stretch_exercises, ExercisePhaseType.static_stretch, goal, 2,
#                                         0, exercise_library)
#
#             if not tier_one and body_part_injury_risk.limited_mobility_tier == 2:
#
#                 goal = AthleteGoal("Reduce injury risks", 1, AthleteGoalType.corrective)
#
#                 self.copy_exercises(body_part.inhibit_exercises, ExercisePhaseType.inhibit, goal, 2, 0, exercise_library)
#
#                 if max_severity < 7.0:
#                     self.copy_exercises(body_part.static_stretch_exercises, ExercisePhaseType.static_stretch, goal, 2,
#                                         0, exercise_library)
#
#             if not tier_one and body_part_injury_risk.underactive_weak_tier == 2:
#
#                 goal = AthleteGoal("Reduce injury risks", 1, AthleteGoalType.corrective)
#
#                 if max_severity < 5.0:
#                     self.copy_exercises(body_part.isolated_activate_exercises, ExercisePhaseType.isolated_activate, goal,
#                                         2, 0, exercise_library)


class MovementIntegrationPrepModality(MovementIntegrationPrep, Modality):
    def __init__(self, event_date_time, force_data=False, relative_load_level=3, force_on_demand=True, sport_cardio_plyometrics=False):
        super().__init__(event_date_time, force_data, relative_load_level, force_on_demand, sport_cardio_plyometrics=sport_cardio_plyometrics)
        self.exercise_phases = [ExercisePhase(ExercisePhaseType.inhibit),
                                ExercisePhase(ExercisePhaseType.static_stretch),
                                ExercisePhase(ExercisePhaseType.active_stretch),
                                ExercisePhase(ExercisePhaseType.dynamic_stretch),
                                ExercisePhase(ExercisePhaseType.isolated_activate),
                                ExercisePhase(ExercisePhaseType.static_integrate),
                                ExercisePhase(ExercisePhaseType.dynamic_integrate)]
        self.when = "before training"
        self.when_card = "before training"
        self.display_image = "dynamic_flexibility"   # do not include .png or _activity or _tab
        self.locked_text = "You skipped this Movement Prep before your Workout."


# class MovementIntegrationPrepModality(ActiveRestBase, Modality):
#     def __init__(self, event_date_time, force_data=False, relative_load_level=3, force_on_demand=True, sport_cardio_plyometrics=False):
#         super().__init__(event_date_time, ModalityType.movement_integration_prep, force_data, relative_load_level, force_on_demand, sport_cardio_plyometrics=sport_cardio_plyometrics)
#         self.exercise_phases = [ExercisePhase(ExercisePhaseType.inhibit),
#                                 ExercisePhase(ExercisePhaseType.static_stretch),
#                                 ExercisePhase(ExercisePhaseType.active_stretch),
#                                 ExercisePhase(ExercisePhaseType.dynamic_stretch),
#                                 ExercisePhase(ExercisePhaseType.isolated_activate),
#                                 ExercisePhase(ExercisePhaseType.static_integrate),
#                                 ExercisePhase(ExercisePhaseType.dynamic_integrate)]
#         self.when = "before training"
#         self.when_card = "before training"
#         self.display_image = "dynamic_flexibility"   # do not include .png or _activity or _tab
#         self.locked_text = "You skipped this Movement Prep before your Workout today."
#
#     def get_general_exercises(self, exercise_library, max_severity):
#
#         body_part_factory = BodyPartFactory()
#
#         body_part = body_part_factory.get_general()
#
#         goal = AthleteGoal("Improve mobility", 1, AthleteGoalType.on_request)
#
#         for a in body_part.agonists:
#             agonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(a), None))
#             if agonist is not None:
#                 self.copy_exercises(agonist.inhibit_exercises, ExercisePhaseType.inhibit, goal, 2, 0,
#                                     exercise_library)
#                 if max_severity < 7:
#                     #self.copy_exercises(agonist.static_stretch_exercises, ExercisePhaseType.static_stretch, goal, 1, 0, exercise_library)
#                     self.copy_exercises(agonist.active_stretch_exercises, ExercisePhaseType.active_stretch, goal, 1, 0, exercise_library)
#                 if max_severity < 5:
#                     self.copy_exercises(agonist.isolated_activate_exercises, ExercisePhaseType.isolated_activate, goal,
#                                         1, 0, exercise_library)
#
#         for y in body_part.synergists:
#             synergist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(y), None))
#             if synergist is not None:
#                 self.copy_exercises(synergist.inhibit_exercises, ExercisePhaseType.inhibit, goal, 3, 0,
#                                     exercise_library)
#                 if max_severity < 7:
#                     self.copy_exercises(synergist.active_stretch_exercises, ExercisePhaseType.active_stretch, goal, 2, 0, exercise_library)
#                 if max_severity < 5:
#                     self.copy_exercises(synergist.isolated_activate_exercises, ExercisePhaseType.isolated_activate, goal,
#                                         2, 0, exercise_library)
#
#         for t in body_part.stabilizers:
#             stabilizer = body_part_factory.get_body_part(BodyPart(BodyPartLocation(t), None))
#             if stabilizer is not None:
#                 self.copy_exercises(stabilizer.inhibit_exercises, ExercisePhaseType.inhibit, goal, 4, 0,
#                                     exercise_library)
#                 if max_severity < 5:
#                     self.copy_exercises(stabilizer.isolated_activate_exercises, ExercisePhaseType.isolated_activate, goal,
#                                         3, 0, exercise_library)
#
#         if max_severity < 5:
#             self.copy_exercises(body_part.static_integrate_exercises, ExercisePhaseType.static_integrate, goal, 1, 0,
#                                 exercise_library)
#
#     def check_recovery(self, body_part, body_part_injury_risk, exercise_library, max_severity, sport_body_parts):
#         compensating = False
#         excessive_strain = False
#
#         if body_part is not None and body_part.location in sport_body_parts:
#             if 0 < body_part_injury_risk.total_volume_percent_tier < 4:
#                 excessive_strain = True
#
#             if (body_part_injury_risk.last_movement_dysfunction_stress_date is not None and
#                     body_part_injury_risk.last_movement_dysfunction_stress_date == self.event_date_time.date()):
#                 compensating = True
#                 body_part_injury_risk.total_compensation_percent_tier = 1
#             elif (body_part_injury_risk.last_compensation_date is not None
#                   and body_part_injury_risk.last_compensation_date == self.event_date_time.date() and
#                   0 < body_part_injury_risk.total_compensation_percent_tier < 4):
#                 compensating = True
#
#             if excessive_strain or compensating:
#                 high_load_tier = 0
#                 comp_tier = 0
#                 tier = 0
#
#                 if excessive_strain:
#                     high_load_tier = body_part_injury_risk.total_volume_percent_tier
#                 if compensating:
#                     comp_tier = body_part_injury_risk.total_compensation_percent_tier
#
#                 if high_load_tier > 0 and comp_tier > 0:
#                     tier = min(high_load_tier, comp_tier)
#                 elif high_load_tier > 0:
#                     tier = high_load_tier
#                 elif comp_tier > 0:
#                     tier = comp_tier
#
#                 if tier > 0:
#
#                     if tier == high_load_tier:
#                         goal = AthleteGoal("Expected Load - Elevated Stress", 1, AthleteGoalType.expected_high_load)
#                     else:
#                         goal = AthleteGoal("Expected Load - Compensation", 1, AthleteGoalType.expected_asymmetric_session)
#
#                     self.copy_exercises(body_part.inhibit_exercises, ExercisePhaseType.inhibit, goal,
#                                         tier + 1, 0, exercise_library)
#                     if max_severity < 7.0:
#                         if self.sport_cardio_plyometrics:
#                             self.copy_exercises(body_part.dynamic_stretch_exercises, ExercisePhaseType.dynamic_stretch, goal,
#                                                 tier, 0, exercise_library)
#                         else:
#                             self.copy_exercises(body_part.active_stretch_exercises, ExercisePhaseType.active_stretch, goal,
#                                                 tier, 0, exercise_library)
#
#             if excessive_strain:
#
#                 goal = AthleteGoal("Expected Load - Compensation", 1, AthleteGoalType.expected_asymmetric_session)
#
#                 if max_severity < 5.0:
#                     if sport_body_parts[body_part.location] in [BodyPartFunction.prime_mover]:
#                         self.copy_exercises(body_part.isolated_activate_exercises, ExercisePhaseType.isolated_activate, goal,
#                                             body_part_injury_risk.total_volume_percent_tier,
#                                             0, exercise_library)
#                     # self.copy_exercises(body_part.static_integrate_exercises, ExercisePhaseType.static_integrate, goal,
#                     #                     body_part_injury_risk.total_volume_percent_tier,
#                     #                     0, exercise_library)
#                 # if max_severity < 4.0:
#                 #     # TODO: What does "match upcoming sport and intensity mean"
#                 #     if body_part.location in sport_body_parts.keys():
#                 #         self.copy_exercises(body_part.dynamic_integrate_exercises, ExercisePhaseType.dynamic_integrate, goal,
#                 #                             body_part_injury_risk.total_volume_percent_tier,
#                 #                             0, exercise_library)
#
#     def check_care(self, body_part, body_part_injury_risk, exercise_library, max_severity):
#         muscle_spasm = False
#         knots = False
#         inflammation = False
#
#         if (body_part_injury_risk.last_inflammation_date is not None and
#                 body_part_injury_risk.last_inflammation_date == self.event_date_time.date()):
#             inflammation = True
#
#         if (body_part_injury_risk.last_muscle_spasm_date is not None and
#                 body_part_injury_risk.last_muscle_spasm_date == self.event_date_time.date()):
#             muscle_spasm = True
#
#         if (body_part_injury_risk.last_knots_date is not None and
#                 body_part_injury_risk.last_knots_date == self.event_date_time.date()):
#             knots = True
#
#         goal = AthleteGoal("Care for symptoms", 1, AthleteGoalType.sore)
#
#         if muscle_spasm or knots or inflammation:
#
#             last_severity = 0
#
#             if muscle_spasm:
#                 last_severity = max(last_severity, body_part_injury_risk.get_muscle_spasm_severity(self.event_date_time.date()))
#             if knots:
#                 last_severity = max(last_severity, body_part_injury_risk.get_knots_severity(self.event_date_time.date()))
#             if inflammation:
#                 last_severity = max(last_severity, body_part_injury_risk.get_inflammation_severity(self.event_date_time.date()))
#
#             self.copy_exercises(body_part.inhibit_exercises, ExercisePhaseType.inhibit, goal, 2, last_severity,
#                                 exercise_library)
#
#             if max_severity < 7.0:
#                 if self.sport_cardio_plyometrics:
#                     self.copy_exercises(body_part.dynamic_stretch_exercises, ExercisePhaseType.dynamic_stretch, goal, 1,
#                                         last_severity, exercise_library)
#                 else:
#                     self.copy_exercises(body_part.active_stretch_exercises, ExercisePhaseType.active_stretch, goal, 1,
#                                         last_severity, exercise_library)
#
#             #     self.copy_exercises(body_part.active_stretch_exercises, ExercisePhaseType.active_stretch, goal, 1,
#             #                         last_severity, exercise_library)
#             # if max_severity < 5.0:  # TODO: this threshold needs to be updated
#             #     self.copy_exercises(body_part.dynamic_stretch_exercises, ExercisePhaseType.dynamic_stretch, goal, 1,
#             #                         last_severity, exercise_library)
#
#             body_part_factory = BodyPartFactory()
#
#             for s in body_part.synergists:
#                 synergist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(s), None))
#                 self.copy_exercises(synergist.inhibit_exercises, ExercisePhaseType.inhibit, goal, 3, last_severity,
#                                     exercise_library)
#
#                 if max_severity < 7.0:
#                     if self.sport_cardio_plyometrics:
#                         self.copy_exercises(synergist.dynamic_stretch_exercises, ExercisePhaseType.dynamic_stretch, goal, 2,
#                                             last_severity, exercise_library)
#                     else:
#                         self.copy_exercises(synergist.active_stretch_exercises, ExercisePhaseType.active_stretch, goal, 2,
#                                             last_severity, exercise_library)
#
#                 # if max_severity < 7.0:
#                 #     self.copy_exercises(synergist.active_stretch_exercises, ExercisePhaseType.active_stretch, goal, 2,
#                 #                         last_severity, exercise_library)
#                 # if max_severity < 5.0:  # TODO: this threshold needs to be updated
#                 #     self.copy_exercises(synergist.dynamic_stretch_exercises, ExercisePhaseType.dynamic_stretch, goal, 2,
#                 #                         last_severity, exercise_library)
#
#         if muscle_spasm or knots:
#
#             last_severity = 0
#
#             if muscle_spasm:
#                 last_severity = max(last_severity,
#                                     body_part_injury_risk.get_muscle_spasm_severity(self.event_date_time.date()))
#             if knots:
#                 last_severity = max(last_severity,
#                                     body_part_injury_risk.get_knots_severity(self.event_date_time.date()))
#
#             if max_severity < 7.0:
#                 self.copy_exercises(body_part.static_stretch_exercises, ExercisePhaseType.static_stretch, goal, 1,
#                                     last_severity, exercise_library)
#
#             # body_part_factory = BodyPartFactory()
#             #
#             # for s in body_part.synergists:
#             #     synergist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(s), None))
#             #
#             #     if max_severity < 7.0:
#             #         self.copy_exercises(synergist.static_stretch_exercises, ExercisePhaseType.static_stretch, goal, 2,
#             #                             last_severity, exercise_library)
#
#     def check_prevention(self, body_part, body_part_injury_risk, exercise_library, max_severity, sport_body_parts):
#         if body_part is not None and body_part.location in sport_body_parts:
#
#             # is_short = self.is_body_part_short(body_part_injury_risk)
#             is_overactive_short = self.is_body_part_overactive_short(body_part_injury_risk)
#             is_overactive_long = self.is_body_part_overactive_long(body_part_injury_risk)
#             is_underactive_long = self.is_body_part_underactive_long(body_part_injury_risk)
#             is_underactive_short = self.is_body_part_underactive_short(body_part_injury_risk)
#             is_weak = self.is_body_part_weak(body_part_injury_risk)
#             # tier_one = False
#
#             if is_overactive_short:
#                 goal = AthleteGoal("Reduce injury risks", 1, AthleteGoalType.corrective)
#                 # tier_one = True
#                 self.copy_exercises(body_part.inhibit_exercises, ExercisePhaseType.inhibit, goal, 2, 0, exercise_library)
#                 if max_severity < 7.0:
#                     self.copy_exercises(body_part.static_stretch_exercises, ExercisePhaseType.static_stretch, goal, 1,
#                                         0, exercise_library)
#
#             elif is_underactive_long or is_weak:
#
#                 goal = AthleteGoal("Reduce injury risks", 1, AthleteGoalType.corrective)
#                 # tier_one = True
#                 if max_severity < 5.0:
#                     self.copy_exercises(body_part.isolated_activate_exercises, ExercisePhaseType.isolated_activate, goal, 1,
#                                         0, exercise_library)
#
#             elif is_overactive_long:
#                 goal = AthleteGoal("Reduce injury risks", 1, AthleteGoalType.corrective)
#                 # tier_one = True
#                 self.copy_exercises(body_part.inhibit_exercises, ExercisePhaseType.inhibit, goal, 2, 0, exercise_library)
#
#             elif is_underactive_short:
#
#                 goal = AthleteGoal("Reduce injury risks", 1, AthleteGoalType.corrective)
#                 # tier_one = True
#                 self.copy_exercises(body_part.inhibit_exercises, ExercisePhaseType.inhibit, goal, 2, 0, exercise_library)
#                 if max_severity < 7.0:
#                     self.copy_exercises(body_part.static_stretch_exercises, ExercisePhaseType.static_stretch, goal, 1, 0, exercise_library)
#                     #self.copy_exercises(body_part.active_stretch_exercises, ExercisePhaseType.active_stretch, goal, 1, 0, exercise_library)
#                     if self.sport_cardio_plyometrics:
#                         self.copy_exercises(body_part.dynamic_stretch_exercises, ExercisePhaseType.dynamic_stretch, goal, 1, 0, exercise_library)
#                     else:
#                         self.copy_exercises(body_part.active_stretch_exercises, ExercisePhaseType.active_stretch, goal, 1, 0, exercise_library)
#                 if max_severity < 5.0:
#                     self.copy_exercises(body_part.isolated_activate_exercises, ExercisePhaseType.isolated_activate, goal, 1, 0, exercise_library)
#                 # if max_severity < 5.0:  # TODO: this threshold might need to change
#                 #     self.copy_exercises(body_part.dynamic_stretch_exercises, ExercisePhaseType.dynamic_stretch, goal, 1, 0, exercise_library)


class ActiveRecoveryModality(ActiveRecovery, Modality):
    def __init__(self, event_date_time):
        #super().__init__(event_date_time, ModalityType.active_recovery)
        super().__init__(event_date_time)
        self.when = "after training"
        self.when_card = "after training"
        self.display_image = "dynamic_stretch"   # do not include .png or _activity or _tab
        self.locked_text = "You missed the optimal window for Active Recovery."

    # def fill_exercises(self, exercise_library, injury_risk_dict, sport_body_parts=None, high_intensity_session=False):
    #
    #     max_severity = 0
    #     for body_part, body_part_injury_risk in injury_risk_dict.items():
    #         if (body_part_injury_risk.last_sharp_level > 0 and body_part_injury_risk.last_sharp_date is not None
    #                 and body_part_injury_risk.last_sharp_date == self.event_date_time.date()):
    #             max_severity = max(max_severity, body_part_injury_risk.last_sharp_level)
    #         if (body_part_injury_risk.last_ache_level > 0 and body_part_injury_risk.last_ache_date is not None
    #                 and body_part_injury_risk.last_ache_date == self.event_date_time.date()):
    #             max_severity = max(max_severity, body_part_injury_risk.last_ache_level)
    #
    #     if max_severity < 4.0 and len(injury_risk_dict) > 0 and high_intensity_session:
    #         for body_part, body_part_injury_risk in injury_risk_dict.items():
    #             self.check_recovery(body_part, body_part_injury_risk, exercise_library, max_severity)
    #
    # def conditions_for_increased_sensitivity_met(self, soreness_list, muscular_strain_high):
    #     return False
    #
    # def check_recovery(self, body_part, body_part_injury_risk, exercise_library, max_severity):
    #
    #     compensating = False
    #     high_load = False
    #
    #     if body_part is not None:
    #
    #         if 0 < body_part_injury_risk.total_volume_percent_tier < 4:
    #             high_load = True
    #
    #         if (body_part_injury_risk.last_movement_dysfunction_stress_date is not None and
    #                 body_part_injury_risk.last_movement_dysfunction_stress_date == self.event_date_time.date()):
    #
    #             compensating = True
    #             body_part_injury_risk.total_compensation_percent_tier = 1
    #         elif (body_part_injury_risk.last_compensation_date is not None
    #               and body_part_injury_risk.last_compensation_date == self.event_date_time.date() and
    #               0 < body_part_injury_risk.total_compensation_percent_tier < 4):
    #
    #             compensating = True
    #
    #         goal = AthleteGoal("Recover from training", 1, AthleteGoalType.high_load)
    #
    #         if high_load or compensating:
    #
    #             high_load_tier = 0
    #             comp_tier = 0
    #             tier = 0
    #
    #             if high_load:
    #                 high_load_tier = body_part_injury_risk.total_volume_percent_tier
    #             if compensating:
    #                 comp_tier = body_part_injury_risk.total_compensation_percent_tier
    #
    #             if high_load_tier > 0 and comp_tier > 0:
    #                 tier = min(high_load_tier, comp_tier)
    #             elif high_load_tier > 0:
    #                 tier = high_load_tier
    #             elif comp_tier > 0:
    #                 tier = comp_tier
    #
    #             if tier > 0:
    #
    #                 self.copy_exercises(body_part.dynamic_integrate_2_exercises, ExercisePhaseType.dynamic_integrate, goal,
    #                                     tier, 0, exercise_library)


class WarmUp(Modality):
    def __init__(self, event_date_time):
        super().__init__(event_date_time, ModalityType.warm_up)
        self.when = "before training"
        self.when_card = "before training"
        self.display_image = "inhibit"   # do not include .png or _activity or _tab
        self.locked_text = "Sorry, you missed the optimal window for Warm up today."


    @abc.abstractmethod
    def fill_exercises(self, exercise_library, injury_risk_dict):
        pass


class CoolDown(Modality):
    def __init__(self, event_date_time):
        super().__init__(event_date_time, ModalityType.cool_down)
        self.when = "after training"
        self.when_card = "after training"
        self.display_image = "inhibit"   # do not include .png or _activity or _tab
        self.locked_text = "Sorry, you missed the optimal window for Cool Down today. "


    @abc.abstractmethod
    def fill_exercises(self, exercise_library, injury_risk_dict):
        pass


class FunctionalStrength(Modality):
    def __init__(self, event_date_time):
        super().__init__(event_date_time, ModalityType.functional_strength)
        self.when = "anytime"
        self.when_card = "anytime"
        self.display_image = "inhibit"   # do not include .png or _activity or _tab
        self.locked_text = "Sorry, you missed the optimal window for Functional Strength today."


    @abc.abstractmethod
    def fill_exercises(self, exercise_library, injury_risk_dict):
        pass


class IceSessionModalities(Serialisable):
    def __init__(self, event_date_time, minutes=0):
        self.minutes = minutes
        self.start_date_time = None
        self.completed_date_time = None
        self.event_date_time = event_date_time
        self.completed = False
        self.active = True
        self.body_parts = []
        self.alerts = []

    def json_serialise(self):

        ret = {
            'minutes': self.minutes,
            'start_date_time': format_datetime(self.start_date_time) if self.start_date_time is not None else None,
            'completed_date_time': format_datetime(
                self.completed_date_time) if self.completed_date_time is not None else None,
            'event_date_time': format_datetime(self.event_date_time) if self.event_date_time is not None else None,
            'completed': self.completed,
            'active': self.active,
            'body_parts': [ice.json_serialise() for ice in self.body_parts],
            'alerts': [alert.json_serialise() for alert in self.alerts]
        }

        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        ice_session = cls(input_dict.get('event_date_time'), input_dict.get('minutes', 0))
        ice_session.start_date_time = input_dict.get('start_date_time', None)
        ice_session.completed_date_time = input_dict.get('completed_date_time', None)
        # ice_session.event_date_time = input_dict.get('event_date_time', None)
        ice_session.completed = input_dict.get('completed', False)
        ice_session.active = input_dict.get('active', True)
        ice_session.body_parts = [IceModality.json_deserialise(body_part) for body_part in input_dict.get('body_parts', [])]
        ice_session.alerts = [Alert.json_deserialise(alert) for alert in input_dict.get('alerts', [])]
        if len(ice_session.body_parts) > 0:
            return ice_session
        else:
            return None

    def __setattr__(self, name, value):
        if name in ['event_date_time', 'start_date_time', 'completed_date_time']:
            if value is not None and not isinstance(value, datetime.datetime):
                value = parse_datetime(value)
        super().__setattr__(name, value)


class IceModality(Serialisable):
    def __init__(self, body_part_location=None, side=0):
        self.body_part_location = body_part_location
        self.side = side
        self.after_training = True
        self.immediately_after_training = False
        self.repeat_every_3hrs_for_24hrs = False
        self.completed = False
        self.active = True
        self.goals = set()

    def json_serialise(self):
        ret = {
            'body_part_location': self.body_part_location.value,
            'goals': [goal.json_serialise() for goal in self.goals],
            'after_training': self.after_training,
            'immediately_after_training': self.immediately_after_training,
            'repeat_every_3hrs_for_24hrs': self.repeat_every_3hrs_for_24hrs,
            'side': self.side,
            'completed': self.completed,
            'active': self.active
        }

        return ret

    def __eq__(self, other):
        return self.body_part_location == other.body_part_location and self.side == other.side

    @classmethod
    def json_deserialise(cls, input_dict):
        ice = cls(body_part_location=BodyPartLocation(input_dict['body_part_location']),
                  side=input_dict['side'])
        ice.after_training = input_dict.get('after_training', False)
        ice.immediately_after_training = input_dict.get('immediately_after_training', False)
        ice.repeat_every_3hrs_for_24hrs = input_dict.get('repeat_every_3hrs_for_24hrs', False)
        ice.completed = input_dict.get('completed', False)
        ice.active = input_dict.get('active', True)
        ice.goals = set([AthleteGoal.json_deserialise(goal) for goal in input_dict.get('goals', [])])

        return ice


class ColdWaterImmersionModality(Serialisable):
    def __init__(self, event_date_time, minutes=10):
        self.minutes = minutes
        self.after_training = True
        self.start_date_time = None
        self.completed_date_time = None
        self.event_date_time = event_date_time
        self.completed = False
        self.active = True
        self.goals = set()
        self.alerts = []

    def json_serialise(self):
        ret = {
            'minutes': self.minutes,
            'after_training': self.after_training,
            'goals': [goal.json_serialise() for goal in self.goals],
            'start_date_time': format_datetime(self.start_date_time) if self.start_date_time is not None else None,
            'completed_date_time': format_datetime(
                self.completed_date_time) if self.completed_date_time is not None else None,
            'event_date_time': format_datetime(self.event_date_time) if self.event_date_time is not None else None,
            'completed': self.completed,
            'active': self.active,
            'alerts': [alert.json_serialise() for alert in self.alerts]
        }

        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        cold_water_immersion = cls(input_dict.get('event_date_time'), minutes=input_dict['minutes'])
        cold_water_immersion.after_training = input_dict.get('after_training', True)
        cold_water_immersion.start_date_time = input_dict.get('start_date_time', None)
        cold_water_immersion.completed_date_time = input_dict.get('completed_date_time', None)
        # cold_water_immersion.event_date_time = input_dict.get('event_date_time', None)
        cold_water_immersion.completed = input_dict.get('completed', False)
        cold_water_immersion.active = input_dict.get('active', True)
        cold_water_immersion.goals = set([AthleteGoal.json_deserialise(goal) for goal in input_dict.get('goals', [])])
        cold_water_immersion.alerts = [Alert.json_deserialise(alert) for alert in input_dict.get('alerts', [])]

        return cold_water_immersion

    def __setattr__(self, name, value):
        if name in ['event_date_time', 'start_date_time', 'completed_date_time']:
            if value is not None and not isinstance(value, datetime.datetime):
                value = parse_datetime(value)
        super().__setattr__(name, value)


class HeatSession(Serialisable):
    def __init__(self, minutes=0):
        self.minutes = minutes
        self.start_date_time = None
        self.completed_date_time = None
        self.event_date_time = None
        self.completed = False
        self.active = True
        self.body_parts = []
        self.alerts = []

    def json_serialise(self):

        ret = {
            'minutes': self.minutes,
            'start_date_time': format_datetime(self.start_date_time) if self.start_date_time is not None else None,
            'completed_date_time': format_datetime(
                self.completed_date_time) if self.completed_date_time is not None else None,
            'event_date_time': format_datetime(self.event_date_time) if self.event_date_time is not None else None,
            'completed': self.completed,
            'active': self.active,
            'body_parts': [heat.json_serialise() for heat in self.body_parts],
            'alerts': [alert.json_serialise() for alert in self.alerts]
        }

        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        heat_session = cls(input_dict.get('minutes', 0))
        heat_session.start_date_time = input_dict.get('start_date_time', None)
        heat_session.completed_date_time = input_dict.get('completed_date_time', None)
        heat_session.event_date_time = input_dict.get('event_date_time', None)
        heat_session.completed = input_dict.get('completed', False)
        heat_session.active = input_dict.get('active', True)
        heat_session.body_parts = [Heat.json_deserialise(body_part) for body_part in input_dict.get('body_parts', [])]
        heat_session.alerts = [Alert.json_deserialise(alert) for alert in input_dict.get('alerts', [])]
        if len(heat_session.body_parts) > 0:
            return heat_session
        else:
            return None

    def __setattr__(self, name, value):
        if name in ['event_date_time', 'start_date_time', 'completed_date_time']:
            if value is not None and not isinstance(value, datetime.datetime):
                value = parse_datetime(value)

        super().__setattr__(name, value)


class Heat(Serialisable):
    def __init__(self, body_part_location=None, side=0):
        self.body_part_location = body_part_location
        self.side = side
        self.before_training = True
        self.goals = set()
        self.completed = False
        self.active = True

    def json_serialise(self):
        ret = {
            'body_part_location': self.body_part_location.value,
            'side': self.side,
            'before_training': self.before_training,
            'goals': [goal.json_serialise() for goal in self.goals],
            'completed': self.completed,
            'active': self.active
        }

        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        heat = cls(body_part_location=BodyPartLocation(input_dict['body_part_location']),
                   side=input_dict['side'])
        heat.before_training = input_dict.get('before_training', True)
        heat.goals = set([AthleteGoal.json_deserialise(goal) for goal in input_dict.get('goals', [])])
        heat.completed = input_dict.get('completed', False)
        heat.active = input_dict.get('active', True)

        return heat    
