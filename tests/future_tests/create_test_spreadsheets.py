from models.soreness import BodyPart, BodyPartLocation, Soreness, HistoricSorenessStatus
from models.stats import AthleteStats
from logic.exercise_mapping import ExerciseAssignmentCalculator
from tests.mocks.mock_exercise_datastore import ExerciseLibraryDatastore
from tests.mocks.mock_completed_exercise_datastore import CompletedExerciseDatastore
from datetime import datetime, timedelta
from logic.trigger_processing import TriggerFactory
from models.historic_soreness import HistoricSoreness
from math import ceil
from models.sport import SportName
import pandas as pd

unreportable_parts = [BodyPartLocation.upper_body, BodyPartLocation.lower_body,
                      BodyPartLocation.full_body, BodyPartLocation.general, BodyPartLocation.head,
                      BodyPartLocation.biceps, BodyPartLocation.triceps, BodyPartLocation.core_stabilizers,
                      BodyPartLocation.erector_spinae, BodyPartLocation.forearm]
joints = [BodyPartLocation.wrist, BodyPartLocation.elbow, BodyPartLocation.hip, BodyPartLocation.knee,
          BodyPartLocation.ankle, BodyPartLocation.foot, BodyPartLocation.lower_back, BodyPartLocation.shoulder]
no_side_parts = [BodyPartLocation.abdominals, BodyPartLocation.upper_back_neck, BodyPartLocation.lower_back]
lower_body_parts = [BodyPartLocation.achilles, BodyPartLocation.ankle, BodyPartLocation.hip,
                    BodyPartLocation.calves, BodyPartLocation.foot, BodyPartLocation.glutes, BodyPartLocation.groin,
                    BodyPartLocation.hamstrings, BodyPartLocation.knee, BodyPartLocation.it_band,
                    BodyPartLocation.quads, BodyPartLocation.shin]
relevant_body_parts = [bpl for bpl in BodyPartLocation if bpl not in unreportable_parts]

historic_enum = [hss for hss in HistoricSorenessStatus if hss not in [HistoricSorenessStatus.almost_persistent_pain,
                                                                      HistoricSorenessStatus.almost_acute_pain,
                                                                      HistoricSorenessStatus.almost_persistent_soreness,
                                                                      HistoricSorenessStatus.almost_persistent_2_pain,
                                                                      HistoricSorenessStatus.almost_persistent_2_soreness,
                                                                      HistoricSorenessStatus.almost_persistent_2_pain_acute]]
persistent_status = [HistoricSorenessStatus.persistent_soreness, HistoricSorenessStatus.persistent_2_soreness,
                     HistoricSorenessStatus.persistent_pain, HistoricSorenessStatus.persistent_2_pain]
pain_status = [HistoricSorenessStatus.acute_pain, HistoricSorenessStatus.persistent_pain,
               HistoricSorenessStatus.persistent_2_pain]

body_part_choice_list = []
day_list = []
side_list = []
history_list = []
severity_list = []
daily_list = []
high_load_list = []

pre_mobilize_list = []
post_mobilize_list = []
cool_down_list = []

pre_inhibit_exercises_list = []
pre_static_stretch_exercises_list = []
pre_active_stretch_exercises_list = []
pre_isolated_activate_exercises_list = []
pre_static_integrate_exercises_list = []

post_inhibit_exercises_list = []
post_static_stretch_exercises_list = []
post_isolated_activate_exercises_list = []
post_static_integrate_exercises_list = []

dynamic_integrate_exercises_list = []
dynamic_stretch_exercises_list = []


def create_load_session_spreadsheet_comprehensive():
    get_sessions("comprehensive")
    write_sessions("comprehensive")


def create_load_session_spreadsheet_complete():
    get_sessions("complete")
    write_sessions("complete")


def create_load_session_spreadsheet_efficient():
    get_sessions("efficient")
    write_sessions("efficient")


# def test_pre_mobilize_comprehensive():
#     read_spreadsheet("comprehensive")
#     # check_pre_all_mobilize_present()
#     # check_pre_all_inhibit_agonist_exercise_numbers()
#     # check_pre_all_inhibit_antagonist_exercise_numbers()
#     # check_pre_all_inhibit_prime_mover_exercise_numbers()
#     # check_pre_non_efficient_inhibit_synergist_exercise_numbers()
#     # check_pre_comprehensive_inhibit_stabilizer_exercise_numbers()
#     # check_pre_all_static_stretch_agonist_exercise_numbers()
#     # check_pre_all_static_stretch_antagonist_exercise_numbers()
#     # check_pre_all_active_stretch_agonist_exercise_numbers()
#     # check_pre_all_active_stretch_antagonist_exercise_numbers()
#     # check_pre_non_efficient_active_stretch_synergist_exercise_numbers()
#     # check_pre_comprehensive_active_stretch_stabilizer_exercise_numbers()
#     # check_pre_all_active_stretch_prime_mover_exercise_numbers()
#     check_pre_all_isolated_activation_antagonist_exercise_numbers()
#     # check_pre_non_efficient_isolated_activation_synergist_exercise_numbers()


# def test_post_mobilize():
#     read_spreadsheet()


# def test_cool_down():
#     read_spreadsheet()
#     check_cool_down_pain_severity()
#     check_cool_down_high_load()


#    check_cool_down_soreness_severity()


exercise_library = ExerciseLibraryDatastore()
exercise_library.side_load_exericse_list_from_csv()


def write_sessions(active_time):
    df = pd.DataFrame({'body_part': body_part_choice_list,
                       'days': day_list,
                       'side': side_list,
                       'historic_status': history_list,
                       'severity': severity_list,
                       'daily': daily_list,
                       'high_load': high_load_list,

                       'pre_mobilize': pre_mobilize_list,
                       'pre_inhibit_exercises': pre_inhibit_exercises_list,
                       'pre_static_stretch_exercises': pre_static_stretch_exercises_list,
                       'pre_active_stretch_exercises': pre_active_stretch_exercises_list,
                       'pre_isolated_activate_exercises': pre_isolated_activate_exercises_list,
                       'pre_static_integrate_exercises': pre_static_integrate_exercises_list,

                       'post_mobilize': post_mobilize_list,
                       'post_inhibit_exercises': post_inhibit_exercises_list,
                       'post_static_stretch_exercises': post_static_stretch_exercises_list,
                       'post_isolated_activate_exercises': post_isolated_activate_exercises_list,
                       'post_static_integrate_exercises': post_static_integrate_exercises_list,

                       'cool_down': cool_down_list,
                       'dynamic_integrate_exercises': dynamic_integrate_exercises_list,
                       'dynamic_stretch_exercises': dynamic_stretch_exercises_list,

                       })
    if active_time == "comprehensive":
        df.to_csv("sessions_comprehensive.csv")
    elif active_time == "complete":
        df.to_csv("sessions_complete.csv")
    elif active_time == "efficient":
        df.to_csv("sessions_efficient.csv")


def read_spreadsheet(active_time):
    if active_time == "comprehensive":
        df = pd.read_csv("sessions_comprehensive.csv")
    elif active_time == "complete":
        df = pd.read_csv("sessions_complete.csv")
    elif active_time == "efficient":
        df = pd.read_csv("sessions_efficient.csv")

    for a in range(0, 15040):
        body_part_choice_list.append(BodyPart(BodyPartLocation(df['body_part'][a]), None))
    for a in range(0, 15040):
        day_list.append(df['days'][a])
    for a in range(0, 15040):
        side_list.append(df['side'][a])
    for a in range(0, 15040):
        history_list.append(df['historic_status'][a])
    for a in range(0, 15040):
        severity_list.append(df['severity'][a])
    for a in range(0, 15040):
        daily_list.append(df['daily'][a])
    for a in range(0, 15040):
        high_load_list.append(df['high_load'][a])

    for a in range(0, 15040):
        pre_mobilize_list.append(df['pre_mobilize'][a])
    for a in range(0, 15040):
        if type(df['pre_inhibit_exercises'][a]) is str:
            pre_inhibit_exercises_list.append([int(s) for s in df['pre_inhibit_exercises'][a].split(',')])
        else:
            pre_inhibit_exercises_list.append(None)
    for a in range(0, 15040):
        if type(df['pre_static_stretch_exercises'][a]) is str:
            pre_static_stretch_exercises_list.append([int(s) for s in df['pre_static_stretch_exercises'][a].split(',')])
        else:
            pre_static_stretch_exercises_list.append(None)
    for a in range(0, 15040):
        if type(df['pre_active_stretch_exercises'][a]) is str:
            pre_active_stretch_exercises_list.append([int(s) for s in df['pre_active_stretch_exercises'][a].split(',')])
        else:
            pre_active_stretch_exercises_list.append(None)
    for a in range(0, 15040):
        if type(df['pre_isolated_activate_exercises'][a]) is str:
            pre_isolated_activate_exercises_list.append(
                [int(s) for s in df['pre_isolated_activate_exercises'][a].split(',')])
        else:
            pre_isolated_activate_exercises_list.append(None)
    for a in range(0, 15040):
        if type(df['pre_static_integrate_exercises'][a]) is str:
            pre_static_integrate_exercises_list.append(
                [int(s) for s in df['pre_static_integrate_exercises'][a].split(',')])
        else:
            pre_static_integrate_exercises_list.append(None)

    for a in range(0, 15040):
        post_mobilize_list.append(df['post_mobilize'][a])
    for a in range(0, 15040):
        if type(df['post_inhibit_exercises'][a]) is str:
            post_inhibit_exercises_list.append([int(s) for s in df['post_inhibit_exercises'][a].split(',')])
        else:
            post_inhibit_exercises_list.append(None)
    for a in range(0, 15040):
        if type(df['post_static_stretch_exercises'][a]) is str:
            post_static_stretch_exercises_list.append(
                [int(s) for s in df['post_static_stretch_exercises'][a].split(',')])
        else:
            post_static_stretch_exercises_list.append(None)
    for a in range(0, 15040):
        if type(df['post_isolated_activate_exercises'][a]) is str:
            post_isolated_activate_exercises_list.append(
                [int(s) for s in df['post_isolated_activate_exercises'][a].split(',')])
        else:
            post_isolated_activate_exercises_list.append(None)
    for a in range(0, 15040):
        if type(df['post_static_integrate_exercises'][a]) is str:
            post_static_integrate_exercises_list.append(
                [int(s) for s in df['post_static_integrate_exercises'][a].split(',')])
        else:
            post_static_integrate_exercises_list.append(None)

    for a in range(0, 15040):
        cool_down_list.append(df['cool_down'][a])
    for a in range(0, 15040):
        if type(df['dynamic_integrate_exercises'][a]) is str:
            dynamic_integrate_exercises_list.append([int(s) for s in df['dynamic_integrate_exercises'][a].split(',')])
        else:
            dynamic_integrate_exercises_list.append(None)
    for a in range(0, 15040):
        if type(df['dynamic_stretch_exercises'][a]) is str:
            dynamic_stretch_exercises_list.append([int(s) for s in df['dynamic_stretch_exercises'][a].split(',')])
        else:
            dynamic_stretch_exercises_list.append(None)


def single_session(current_body_part, days, side, history, severity, daily, high_load):
    soreness = Soreness()
    soreness.body_part = BodyPart(current_body_part, None)
    soreness.severity = severity / 2
    soreness.max_severity = ceil(soreness.severity)
    if daily == 1:
        soreness.daily = True
    else:
        soreness.daily = False
    soreness.side = side
    soreness.historic_soreness_status = history
    if history in pain_status:
        soreness.pain = True
    else:
        soreness.pain = False
    if history is HistoricSorenessStatus.doms:
        soreness.first_reported_date_time = datetime.today() - timedelta(days=days / 10)
    else:
        soreness.first_reported_date_time = datetime.today() - timedelta(days=(25 + days))

    historic_soreness = HistoricSoreness(soreness.body_part.location, soreness.side,
                                         soreness.pain)
    historic_soreness.historic_soreness_status = soreness.historic_soreness_status
    historic_soreness.first_reported_date_time = soreness.first_reported_date_time
    historic_soreness.max_severity = ceil(soreness.severity)

    AthleteStats("tester").historic_soreness = [soreness]

    trigger_factory = TriggerFactory(datetime.today(), AthleteStats("tester"),
                                     [soreness], [])
    if high_load is 1:
        trigger_factory.high_relative_load_session = True
        trigger_factory.eligible_for_high_load_trigger = True
        trigger_factory.high_relative_load_session_sport_names = [SportName.barre]
    else:
        trigger_factory.high_relative_load_session = False

    trigger_factory.load_triggers()

    calc = ExerciseAssignmentCalculator(trigger_factory,
                                        exercise_library,
                                        CompletedExerciseDatastore(), [],
                                        [soreness], datetime.today(),
                                        [historic_soreness])

    return calc.get_pre_active_rest(), calc.get_post_active_rest(), calc.get_cool_down()


def get_sessions_helper(pre_active_rest, post_active_rest, cool_down, active_time):
    if cool_down == []:
        cool_down_list.append(0)
    else:
        cool_down_list.append(1)
        if active_time == "comprehensive":    
            dynamic_integrate_exercises_list.append(','.join(str(a) for a in
                                                             cool_down[0].dynamic_integrate_exercises if
                                                             cool_down[0].dynamic_integrate_exercises[
                                                             a].dosages[0].comprehensive_sets_assigned > 0))
            dynamic_stretch_exercises_list.append(','.join(str(a) for a in
                                                           cool_down[0].dynamic_stretch_exercises if
                                                           cool_down[0].dynamic_stretch_exercises[
                                                           a].dosages[0].comprehensive_sets_assigned > 0))
        elif active_time == "complete":
            dynamic_integrate_exercises_list.append(','.join(str(a) for a in
                                                             cool_down[0].dynamic_integrate_exercises if
                                                             cool_down[0].dynamic_integrate_exercises[
                                                                 a].dosages[0].complete_sets_assigned > 0))
            dynamic_stretch_exercises_list.append(','.join(str(a) for a in
                                                           cool_down[0].dynamic_stretch_exercises if
                                                           cool_down[0].dynamic_stretch_exercises[
                                                               a].dosages[0].complete_sets_assigned > 0))
        elif active_time == "efficient":
            dynamic_integrate_exercises_list.append(','.join(str(a) for a in
                                                             cool_down[0].dynamic_integrate_exercises if
                                                             cool_down[0].dynamic_integrate_exercises[
                                                                 a].dosages[0].efficient_sets_assigned > 0))
            dynamic_stretch_exercises_list.append(','.join(str(a) for a in
                                                           cool_down[0].dynamic_stretch_exercises if
                                                           cool_down[0].dynamic_stretch_exercises[
                                                               a].dosages[0].efficient_sets_assigned > 0))
    if pre_active_rest == []:
        pre_mobilize_list.append(0)
    else:
        pre_mobilize_list.append(1)
        if active_time == "comprehensive":
            pre_inhibit_exercises_list.append(
                (','.join(str(a) for a in pre_active_rest[0].inhibit_exercises
                          if pre_active_rest[0].inhibit_exercises[
                              a].dosages[0].comprehensive_sets_assigned)))
            pre_static_stretch_exercises_list.append(
                (','.join(str(a) for a in pre_active_rest[0].static_stretch_exercises
                          if pre_active_rest[0].static_stretch_exercises[
                              a].dosages[0].comprehensive_sets_assigned)))
            pre_active_stretch_exercises_list.append(
                (','.join(str(a) for a in pre_active_rest[0].active_stretch_exercises
                          if pre_active_rest[0].active_stretch_exercises[
                              a].dosages[0].comprehensive_sets_assigned)))
            pre_isolated_activate_exercises_list.append(
                (','.join(
                    str(a) for a in pre_active_rest[0].isolated_activate_exercises
                    if pre_active_rest[0].isolated_activate_exercises[
                        a].dosages[0].comprehensive_sets_assigned)))
            pre_static_integrate_exercises_list.append(
                (','.join(
                    str(a) for a in pre_active_rest[0].static_integrate_exercises
                    if pre_active_rest[0].static_integrate_exercises[
                        a].dosages[0].comprehensive_sets_assigned)))
        elif active_time == "complete":
            pre_inhibit_exercises_list.append(
                (','.join(str(a) for a in pre_active_rest[0].inhibit_exercises
                          if pre_active_rest[0].inhibit_exercises[
                              a].dosages[0].complete_sets_assigned)))
            pre_static_stretch_exercises_list.append(
                (','.join(str(a) for a in pre_active_rest[0].static_stretch_exercises
                          if pre_active_rest[0].static_stretch_exercises[
                              a].dosages[0].complete_sets_assigned)))
            pre_active_stretch_exercises_list.append(
                (','.join(str(a) for a in pre_active_rest[0].active_stretch_exercises
                          if pre_active_rest[0].active_stretch_exercises[
                              a].dosages[0].complete_sets_assigned)))
            pre_isolated_activate_exercises_list.append(
                (','.join(
                    str(a) for a in pre_active_rest[0].isolated_activate_exercises
                    if pre_active_rest[0].isolated_activate_exercises[
                        a].dosages[0].complete_sets_assigned)))
            pre_static_integrate_exercises_list.append(
                (','.join(
                    str(a) for a in pre_active_rest[0].static_integrate_exercises
                    if pre_active_rest[0].static_integrate_exercises[
                        a].dosages[0].complete_sets_assigned)))
        elif active_time == "efficient":
            pre_inhibit_exercises_list.append(
                (','.join(str(a) for a in pre_active_rest[0].inhibit_exercises
                          if pre_active_rest[0].inhibit_exercises[
                              a].dosages[0].efficient_sets_assigned)))
            pre_static_stretch_exercises_list.append(
                (','.join(str(a) for a in pre_active_rest[0].static_stretch_exercises
                          if pre_active_rest[0].static_stretch_exercises[
                              a].dosages[0].efficient_sets_assigned)))
            pre_active_stretch_exercises_list.append(
                (','.join(str(a) for a in pre_active_rest[0].active_stretch_exercises
                          if pre_active_rest[0].active_stretch_exercises[
                              a].dosages[0].efficient_sets_assigned)))
            pre_isolated_activate_exercises_list.append(
                (','.join(
                    str(a) for a in pre_active_rest[0].isolated_activate_exercises
                    if pre_active_rest[0].isolated_activate_exercises[
                        a].dosages[0].efficient_sets_assigned)))
            pre_static_integrate_exercises_list.append(
                (','.join(
                    str(a) for a in pre_active_rest[0].static_integrate_exercises
                    if pre_active_rest[0].static_integrate_exercises[
                        a].dosages[0].efficient_sets_assigned)))
    if post_active_rest == []:
        post_mobilize_list.append(0)
    else:
        post_mobilize_list.append(1)
        if active_time == "comprehensive":
            post_inhibit_exercises_list.append(
                (','.join(str(a) for a in post_active_rest[0].inhibit_exercises
                          if post_active_rest[0].inhibit_exercises[
                              a].dosages[0].comprehensive_sets_assigned)))
            post_static_stretch_exercises_list.append(
                (','.join(
                    str(a) for a in post_active_rest[0].static_stretch_exercises
                    if post_active_rest[0].static_stretch_exercises[
                        a].dosages[0].comprehensive_sets_assigned)))
            post_isolated_activate_exercises_list.append(
                (','.join(
                    str(a) for a in post_active_rest[0].isolated_activate_exercises
                    if post_active_rest[0].isolated_activate_exercises[
                        a].dosages[0].comprehensive_sets_assigned)))
            post_static_integrate_exercises_list.append(
                (','.join(
                    str(a) for a in post_active_rest[0].static_integrate_exercises
                    if post_active_rest[0].static_integrate_exercises[
                        a].dosages[0].comprehensive_sets_assigned)))
        elif active_time == "complete":
            post_inhibit_exercises_list.append(
                (','.join(str(a) for a in post_active_rest[0].inhibit_exercises
                          if post_active_rest[0].inhibit_exercises[
                              a].dosages[0].complete_sets_assigned)))
            post_static_stretch_exercises_list.append(
                (','.join(str(a) for a in post_active_rest[0].static_stretch_exercises
                          if post_active_rest[0].static_stretch_exercises[
                              a].dosages[0].complete_sets_assigned)))
            post_isolated_activate_exercises_list.append(
                (','.join(
                    str(a) for a in post_active_rest[0].isolated_activate_exercises
                    if post_active_rest[0].isolated_activate_exercises[
                        a].dosages[0].complete_sets_assigned)))
            post_static_integrate_exercises_list.append(
                (','.join(
                    str(a) for a in post_active_rest[0].static_integrate_exercises
                    if post_active_rest[0].static_integrate_exercises[
                        a].dosages[0].complete_sets_assigned)))
        elif active_time == "efficient":
            post_inhibit_exercises_list.append(
                (','.join(str(a) for a in post_active_rest[0].inhibit_exercises
                          if post_active_rest[0].inhibit_exercises[
                              a].dosages[0].efficient_sets_assigned)))
            post_static_stretch_exercises_list.append(
                (','.join(str(a) for a in post_active_rest[0].static_stretch_exercises
                          if post_active_rest[0].static_stretch_exercises[
                              a].dosages[0].efficient_sets_assigned)))
            post_isolated_activate_exercises_list.append(
                (','.join(
                    str(a) for a in post_active_rest[0].isolated_activate_exercises
                    if post_active_rest[0].isolated_activate_exercises[
                        a].dosages[0].efficient_sets_assigned)))
            post_static_integrate_exercises_list.append(
                (','.join(
                    str(a) for a in post_active_rest[0].static_integrate_exercises
                    if post_active_rest[0].static_integrate_exercises[
                        a].dosages[0].efficient_sets_assigned)))
    max_length = max([len(cool_down_list), len(pre_mobilize_list), len(post_mobilize_list),
                     len(dynamic_integrate_exercises_list), len(dynamic_integrate_exercises_list),
                     len(pre_inhibit_exercises_list), len(pre_static_stretch_exercises_list),
                     len(pre_active_stretch_exercises_list), len(pre_isolated_activate_exercises_list),
                     len(pre_static_integrate_exercises_list),
                     len(post_inhibit_exercises_list), len(post_static_stretch_exercises_list),
                     len(post_isolated_activate_exercises_list), len(post_static_integrate_exercises_list)])
    if len(cool_down_list) < max_length:
        cool_down_list.append(0)
    if len(pre_mobilize_list) < max_length:
        pre_mobilize_list.append(0)
    if len(post_mobilize_list) < max_length:
        post_mobilize_list.append(0)
    
    if len(dynamic_integrate_exercises_list) < max_length:
        dynamic_integrate_exercises_list.append(0)
    if len(dynamic_stretch_exercises_list) < max_length:
        dynamic_stretch_exercises_list.append(0)
    
    if len(pre_inhibit_exercises_list) < max_length:
        pre_inhibit_exercises_list.append(0)
    if len(pre_static_stretch_exercises_list) < max_length:
        pre_static_stretch_exercises_list.append(0)
    if len(pre_active_stretch_exercises_list) < max_length:
        pre_active_stretch_exercises_list.append(0)
    if len(pre_isolated_activate_exercises_list) < max_length:
        pre_isolated_activate_exercises_list.append(0)
    if len(pre_static_integrate_exercises_list) < max_length:
        pre_static_integrate_exercises_list.append(0)
    
    if len(post_inhibit_exercises_list) < max_length:
        post_inhibit_exercises_list.append(0)
    if len(post_static_stretch_exercises_list) < max_length:
        post_static_stretch_exercises_list.append(0)
    if len(post_isolated_activate_exercises_list) < max_length:
        post_isolated_activate_exercises_list.append(0)
    if len(post_static_integrate_exercises_list) < max_length:
        post_static_integrate_exercises_list.append(0)


def get_sessions(active_time):
    for rbp in relevant_body_parts:
        for dy in [0, 10]:
            for sv in range(1, 11):
                for hl in [1, 0]:
                    if rbp not in no_side_parts:
                        for sd in [1, 2]:
                            if rbp in joints:
                                for h in pain_status:
                                    for di in [1, 0]:
                                        pre_active_rest, post_active_rest, cool_down = single_session(rbp, dy, sd,
                                                                                                      h, sv, di, hl)
                                        body_part_choice_list.append(rbp.value)
                                        day_list.append(dy)
                                        side_list.append(sd)
                                        history_list.append(h)
                                        severity_list.append(sv / 2)
                                        daily_list.append(di)
                                        high_load_list.append(hl)
                                        get_sessions_helper(pre_active_rest, post_active_rest, cool_down, active_time)

                            else:
                                for h in historic_enum:
                                    if h is not HistoricSorenessStatus.doms:
                                        for di in [1, 0]:
                                            pre_active_rest, post_active_rest, cool_down = single_session(rbp, dy, sd,
                                                                                                          h, sv, di, hl)
                                            body_part_choice_list.append(rbp.value)
                                            day_list.append(dy)
                                            side_list.append(sd)
                                            history_list.append(h)
                                            severity_list.append(sv / 2)
                                            daily_list.append(di)
                                            high_load_list.append(hl)
                                            get_sessions_helper(pre_active_rest, post_active_rest, cool_down, active_time)
                                    else:
                                        di = 1
                                        pre_active_rest, post_active_rest, cool_down = single_session(rbp, dy, sd,
                                                                                                      h, sv, di, hl)
                                        body_part_choice_list.append(rbp.value)
                                        day_list.append(dy)
                                        side_list.append(sd)
                                        history_list.append(h)
                                        severity_list.append(sv / 2)
                                        daily_list.append(di)
                                        high_load_list.append(hl)
                                        get_sessions_helper(pre_active_rest, post_active_rest, cool_down, active_time)
                    else:
                        sd = 0
                        if rbp in joints:
                            for h in pain_status:
                                for di in [1, 0]:
                                    pre_active_rest, post_active_rest, cool_down = single_session(rbp, dy, sd,
                                                                                                  h, sv, di, hl)
                                    body_part_choice_list.append(rbp.value)
                                    day_list.append(dy)
                                    side_list.append(sd)
                                    history_list.append(h)
                                    severity_list.append(sv / 2)
                                    daily_list.append(di)
                                    high_load_list.append(hl)
                                    get_sessions_helper(pre_active_rest, post_active_rest, cool_down, active_time)
                        else:
                            for h in historic_enum:
                                if h is not HistoricSorenessStatus.doms:
                                    for di in [1, 0]:
                                        pre_active_rest, post_active_rest, cool_down = single_session(rbp, dy, sd,
                                                                                                      h, sv, di, hl)
                                        body_part_choice_list.append(rbp.value)
                                        day_list.append(dy)
                                        side_list.append(sd)
                                        history_list.append(h)
                                        severity_list.append(sv / 2)
                                        daily_list.append(di)
                                        high_load_list.append(hl)
                                        get_sessions_helper(pre_active_rest, post_active_rest, cool_down, active_time)
                                else:
                                    di = 1
                                    pre_active_rest, post_active_rest, cool_down = single_session(rbp, dy, sd,
                                                                                                  h, sv, di, hl)
                                    body_part_choice_list.append(rbp.value)
                                    day_list.append(dy)
                                    side_list.append(sd)
                                    history_list.append(h)
                                    severity_list.append(sv / 2)
                                    daily_list.append(di)
                                    high_load_list.append(hl)
                                    get_sessions_helper(pre_active_rest, post_active_rest, cool_down, active_time)


if __name__ == '__main__':
    create_load_session_spreadsheet_comprehensive()


# def check_cool_down_high_load():
#     b_index = 0
#     for b in cool_down_list:
#         if b == 1:
#             assert high_load_list[b_index] == 1
#         b_index += 1
#
#
# def check_cool_down_pain_severity():
#     b_index = 0
#     for b in cool_down_list:
#         if b == 1 and history_list[b_index] in pain_status:
#             assert severity_list[b_index] < 2.5
#         b_index += 1
#
#
# def check_cool_down_soreness_severity():
#     b_index = 0
#     for b in cool_down_list:
#         if b == 1 and history_list[b_index] not in pain_status:
#             assert severity_list[b_index] < 3.5
#         b_index += 1


# def body_part_info(body_part, part_or_exercise):
#     df = pd.read_csv("body_part_collection.csv")
#     if part_or_exercise == "agonist":
#         if df[body_part][0] != 0:
#             return [int(s) for s in str(df[body_part][0]).split(',')]
#         else:
#             return None
#     elif part_or_exercise == "synergist":
#         if df[body_part][1] != 0:
#             return [int(s) for s in str(df[body_part][1]).split(',')]
#         else:
#             return None
#     elif part_or_exercise == "stabilizer":
#         if df[body_part][2] != 0:
#             return [int(s) for s in str(df[body_part][2]).split(',')]
#         else:
#             return None
#     elif part_or_exercise == "antagonist":
#         if str(df[body_part][3]) != '0':
#             return [int(s) for s in str(df[body_part][3]).split(',')]
#         else:
#             return None
#     elif part_or_exercise == "inhibit":
#         if df[body_part][4] != 0:
#             return [int(s) for s in str(df[body_part][4]).split(',')]
#         else:
#             return None
#     elif part_or_exercise == "static_stretch":
#         if df[body_part][5] != 0:
#             return [int(s) for s in str(df[body_part][5]).split(',')]
#         else:
#             return None
#     elif part_or_exercise == "active_stretch":
#         if df[body_part][6] != 0:
#             return [int(s) for s in str(df[body_part][6]).split(',')]
#         else:
#             return None
#     elif part_or_exercise == "isolated_activate":
#         if df[body_part][7] != 0:
#             return [int(s) for s in str(df[body_part][7]).split(',')]
#         else:
#             return None
#
#
# def check_pre_all_mobilize_present():
#     b_index = 0
#     for b in pre_mobilize_list:
#         sore_greater_30 = (history_list[b_index] in [6, 7] and day_list[b_index] == 10)
#         if (daily_list[b_index] == 0 and history_list[b_index] not in [1, 2, 10]
#                 and sore_greater_30 == False and high_load_list[b_index] == 0):
#             assert b == 0
#         elif daily_list[b_index] == 0 and high_load_list[b_index] == 0 and severity_list[b_index] >= 3:
#             assert b == 0
#         else:
#             assert b == 1
#         b_index += 1
#
#
# def check_pre_all_inhibit_agonist_exercise_numbers():
#     b_index = 0
#     for b in pre_mobilize_list:
#         sore_greater_30 = (history_list[b_index] in [6, 7] and day_list[b_index] == 10)
#         if (b == 1 and
#                 not (daily_list[b_index] == 0 and history_list[b_index] not in [1, 2, 10] and sore_greater_30 == False)
#                 and not (daily_list[b_index] == 0 and severity_list[b_index] >= 2.5)):
#             agonists = body_part_info(str(body_part_choice_list[b_index].location), "agonist")
#             for agonist in agonists:
#                 agonist_exercises = set(body_part_info(str(BodyPart(BodyPartLocation(agonist), None).location), "inhibit"))
#                 assigned_exercises = set(pre_inhibit_exercises_list[b_index])
#                 if len(agonist_exercises.intersection(assigned_exercises)) > 0:
#                     assert len(agonist_exercises.intersection(assigned_exercises)) > 0
#                 else:
#                     assert body_part_choice_list[b_index].location in joints and daily_list[b_index] == 0
#                     print(body_part_choice_list[b_index].location)
#         b_index += 1
#
#
# def check_pre_all_inhibit_antagonist_exercise_numbers():
#     b_index = 0
#     for b in pre_mobilize_list:
#         if (b == 1 and body_part_choice_list[b_index].location in joints and daily_list[b_index] == 1 and
#                 history_list[b_index] in [1, 2, 10]):
#             antagonists = body_part_info(str(body_part_choice_list[b_index].location), "antagonist")
#             if antagonists is not None:
#                 for antagonist in antagonists:
#                     antagonist_exercises = set(body_part_info(str(BodyPart(BodyPartLocation(antagonist), None).location), "inhibit"))
#                     assigned_exercises = set(pre_inhibit_exercises_list[b_index])
#                     assert len(antagonist_exercises.intersection(assigned_exercises)) > 0
#         b_index += 1
#
#
# def check_pre_all_inhibit_prime_mover_exercise_numbers():
#     b_index = 0
#     for b in pre_mobilize_list:
#         if b == 1 and high_load_list[b_index] == 1:
#             prime_mover_exercises = {44, 48, 54}
#             assigned_exercises = set(pre_inhibit_exercises_list[b_index])
#             assert len(prime_mover_exercises.intersection(assigned_exercises)) > 0
#         b_index += 1
#
#
# def check_pre_non_efficient_inhibit_synergist_exercise_numbers():
#     b_index = 0
#     for b in pre_mobilize_list:
#         sore_greater_30 = (history_list[b_index] in [6, 7] and day_list[b_index] == 10)
#         if (b == 1 and ((history_list[b_index] in [1, 2, 6, 7, 10] and severity_list[b_index] >= 0.5)
#                        or (history_list in [0, 12] and severity_list[b_index] >= 1.5))
#                        and not (daily_list[b_index] == 0 and history_list[b_index] not in[1, 2, 10] and sore_greater_30 == False)
#                        and not (daily_list[b_index] == 0 and severity_list[b_index] >= 2.5)):
#             synergists = body_part_info(str(body_part_choice_list[b_index].location), "synergist")
#             if synergists is not None:
#                 for synergist in synergists:
#                     synergist_exercises = set(body_part_info(str(BodyPart(BodyPartLocation(synergist), None).location), "inhibit"))
#                     assigned_exercises = set(pre_inhibit_exercises_list[b_index])
#                     assert len(synergist_exercises.intersection(assigned_exercises)) > 0
#         b_index += 1
#
#
# def check_pre_comprehensive_inhibit_stabilizer_exercise_numbers():
#     b_index = 0
#     for b in pre_mobilize_list:
#         if (b == 1 and ((history_list[b_index] in [1, 2, 6, 7, 10] and severity_list[b_index] >= 0.5)
#                         or (history_list in [0, 12] and severity_list[b_index] >= 1.5))
#                 and daily_list[b_index] == 1):
#             stabilizers = body_part_info(str(body_part_choice_list[b_index].location), "stabilizer")
#             if stabilizers is not None:
#                 for stabilizer in stabilizers:
#                     stabilizer_exercises = set(body_part_info(str(BodyPart(BodyPartLocation(stabilizer), None).location), "inhibit"))
#                     assigned_exercises = set(pre_inhibit_exercises_list[b_index])
#                     assert len(stabilizer_exercises.intersection(assigned_exercises)) > 0
#         b_index += 1
#
#
# def check_pre_all_static_stretch_agonist_exercise_numbers():
#     b_index = 0
#     for b in pre_mobilize_list:
#         sore_greater_30 = (history_list[b_index] in [6, 7] and day_list[b_index] == 10)
#         if (b == 1 and
#                 not (daily_list[b_index] == 0 and history_list[b_index] not in [1, 2, 10] and sore_greater_30 == False)
#                 and not (daily_list[b_index] == 0 and severity_list[b_index] >= 2.5)
#                 and severity_list[b_index] < 3.5):
#             agonists = body_part_info(str(body_part_choice_list[b_index].location), "agonist")
#             for agonist in agonists:
#                 agonist_exercises = set(
#                     body_part_info(str(BodyPart(BodyPartLocation(agonist), None).location), "static_stretch"))
#                 if pre_static_stretch_exercises_list[b_index] is not None:
#                     assigned_exercises = set(pre_static_stretch_exercises_list[b_index])
#                 else:
#                     assigned_exercises = {0}
#                 if len(agonist_exercises.intersection(assigned_exercises)) > 0:
#                     assert len(agonist_exercises.intersection(assigned_exercises)) > 0
#                 else:
#                     assert body_part_choice_list[b_index].location in joints and daily_list[b_index] == 0
#                     print(body_part_choice_list[b_index].location)
#         b_index += 1
#
#
# def check_pre_all_static_stretch_antagonist_exercise_numbers():
#     b_index = 0
#     for b in pre_mobilize_list:
#         if (b == 1 and body_part_choice_list[b_index].location in joints and daily_list[b_index] == 1 and
#                 history_list[b_index] in [1, 2, 10] and severity_list[b_index] < 3.5):
#             antagonists = body_part_info(str(body_part_choice_list[b_index].location), "antagonist")
#             if antagonists is not None:
#                 for antagonist in antagonists:
#                     antagonist_exercises = set(
#                         body_part_info(str(BodyPart(BodyPartLocation(antagonist), None).location), "static_stretch"))
#                     assigned_exercises = set(pre_static_stretch_exercises_list[b_index])
#                     assert len(antagonist_exercises.intersection(assigned_exercises)) > 0
#         b_index += 1
#
#
# def check_pre_all_active_stretch_agonist_exercise_numbers():
#     b_index = 0
#     for b in pre_mobilize_list:
#         if b == 1 and daily_list[b_index] == 1 and severity_list[b_index] < 3.5:
#             agonists = body_part_info(str(body_part_choice_list[b_index].location), "agonist")
#             for agonist in agonists:
#                 agonist_exercises = set(
#                     body_part_info(str(BodyPart(BodyPartLocation(agonist), None).location), "active_stretch"))
#                 assigned_exercises = set(pre_active_stretch_exercises_list[b_index])
#                 # if len(agonist_exercises.intersection(assigned_exercises)) > 0:
#                 assert len(agonist_exercises.intersection(assigned_exercises)) > 0
#                 # else:
#                 #     assert body_part_choice_list[b_index].location in joints and daily_list[b_index] == 0
#                 #     print(body_part_choice_list[b_index].location)
#         b_index += 1
#
#
# def check_pre_all_active_stretch_antagonist_exercise_numbers():
#     b_index = 0
#     for b in pre_mobilize_list:
#         if (b == 1 and body_part_choice_list[b_index].location in joints and daily_list[b_index] == 1 and
#                 history_list[b_index] in [1, 2, 10] and severity_list[b_index] < 3.5):
#             antagonists = body_part_info(str(body_part_choice_list[b_index].location), "antagonist")
#             if antagonists is not None:
#                 for antagonist in antagonists:
#                     antagonist_exercises = set(
#                         body_part_info(str(BodyPart(BodyPartLocation(antagonist), None).location), "active_stretch"))
#                     assigned_exercises = set(pre_active_stretch_exercises_list[b_index])
#                     assert len(antagonist_exercises.intersection(assigned_exercises)) > 0
#         b_index += 1
#
#
# def check_pre_non_efficient_active_stretch_synergist_exercise_numbers():
#     b_index = 0
#     for b in pre_mobilize_list:
#         if (b == 1 and ((history_list[b_index] in [1, 2, 6, 7, 10] and severity_list[b_index] >= 0.5)
#                         or (history_list in [0, 12] and severity_list[b_index] >= 1.5))
#                 and daily_list[b_index] == 1 and severity_list[b_index] < 3.5):
#             synergists = body_part_info(str(body_part_choice_list[b_index].location), "synergist")
#             if synergists is not None:
#                 for synergist in synergists:
#                     synergist_exercises = set(
#                         body_part_info(str(BodyPart(BodyPartLocation(synergist), None).location), "active_stretch"))
#                     assigned_exercises = set(pre_active_stretch_exercises_list[b_index])
#                     assert len(synergist_exercises.intersection(assigned_exercises)) > 0
#         b_index += 1
#
#
# def check_pre_comprehensive_active_stretch_stabilizer_exercise_numbers():
#     b_index = 0
#     for b in pre_mobilize_list:
#         if (b == 1 and ((history_list[b_index] in [1, 2, 6, 7, 10] and severity_list[b_index] >= 0.5)
#                         or (history_list in [0, 12] and severity_list[b_index] >= 1.5))
#                 and daily_list[b_index] == 1 and severity_list[b_index] < 3.5):
#             stabilizers = body_part_info(str(body_part_choice_list[b_index].location), "stabilizer")
#             if stabilizers is not None:
#                 for stabilizer in stabilizers:
#                     stabilizer_exercises = set(
#                         body_part_info(str(BodyPart(BodyPartLocation(stabilizer), None).location), "active_stretch"))
#                     assigned_exercises = set(pre_active_stretch_exercises_list[b_index])
#                     assert len(stabilizer_exercises.intersection(assigned_exercises)) > 0
#         b_index += 1
#
#
# def check_pre_all_active_stretch_prime_mover_exercise_numbers():
#     b_index = 0
#     for b in pre_mobilize_list:
#         if b == 1 and high_load_list[b_index] == 1 and severity_list[b_index] < 3.5:
#             prime_mover_exercises = {266, 275, 277}
#             assigned_exercises = set(pre_active_stretch_exercises_list[b_index])
#             assert len(prime_mover_exercises.intersection(assigned_exercises)) > 0
#         b_index += 1
#
#
# def check_pre_all_isolated_activation_antagonist_exercise_numbers():
#     b_index = 0
#     for b in pre_mobilize_list:
#         sore_greater_30 = (history_list[b_index] in [6, 7] and day_list[b_index] == 10)
#         if (b == 1 and (sore_greater_30 is True or history_list[b_index] in [1, 2, 10] or high_load_list[b_index] == 1)
#                 and severity_list[b_index] < 2.5):
#             antagonists = body_part_info(str(body_part_choice_list[b_index].location), "antagonist")
#             if antagonists is not None:
#                 for antagonist in antagonists:
#                     antagonist_exercises = set(body_part_info(str(BodyPart(BodyPartLocation(antagonist), None).location), "isolated_activate"))
#                     assigned_exercises = set(pre_isolated_activate_exercises_list[b_index])
#                     if len(antagonist_exercises.intersection(assigned_exercises)) > 0:
#                         assert len(antagonist_exercises.intersection(assigned_exercises)) > 0
#                     else:
#                         print("Compensated Error.")
#         b_index += 1
#
#
# def check_pre_non_efficient_isolated_activation_synergist_exercise_numbers():
#     b_index = 0
#     for b in pre_mobilize_list:
#         sore_greater_30 = (history_list[b_index] in [6, 7] and day_list[b_index] == 10)
#         if b == 1 and (sore_greater_30 is True or history_list[b_index] in [1, 2, 10]) and severity_list[b_index] < 2.5:
#             synergists = body_part_info(str(body_part_choice_list[b_index].location), "synergist")
#             if synergists is not None:
#                 for synergist in synergists:
#                     synergist_exercises = set(
#                         body_part_info(str(BodyPart(BodyPartLocation(synergist), None).location), "isolated_activate"))
#                     assigned_exercises = set(pre_isolated_activate_exercises_list[b_index])
#                     assert len(synergist_exercises.intersection(assigned_exercises)) > 0
#         b_index += 1
