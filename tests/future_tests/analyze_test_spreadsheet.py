from models.body_parts import BodyPart, BodyPartLocation, BodyPartFactory
import pandas as pd
from models.historic_soreness import HistoricSorenessStatus

unreportable_parts = [BodyPartLocation.upper_body, BodyPartLocation.lower_body,
                      BodyPartLocation.full_body, BodyPartLocation.general, BodyPartLocation.head,
                      BodyPartLocation.biceps, BodyPartLocation.triceps, BodyPartLocation.core_stabilizers,
                      BodyPartLocation.erector_spinea, BodyPartLocation.forearm]
joints = [BodyPartLocation.wrist, BodyPartLocation.elbow, BodyPartLocation.hip_flexor, BodyPartLocation.knee,
          BodyPartLocation.ankle, BodyPartLocation.foot, BodyPartLocation.lower_back, BodyPartLocation.shoulder]
no_side_parts = [BodyPartLocation.abdominals, BodyPartLocation.upper_back_neck, BodyPartLocation.lower_back]
lower_body_parts = [BodyPartLocation.achilles, BodyPartLocation.ankle, BodyPartLocation.hip_flexor,
                    BodyPartLocation.calves, BodyPartLocation.foot, BodyPartLocation.glutes, BodyPartLocation.groin,
                    BodyPartLocation.hamstrings, BodyPartLocation.knee, BodyPartLocation.outer_thigh,
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


def check_pre_mobilize_present():
    b_index = 0
    for b in pre_mobilize_list:
        sore_greater_30 = (history_list[b_index] in [6, 7] and day_list[b_index] == 10)
        if (daily_list[b_index] == 0 and history_list[b_index] not in [1, 2, 10]
                and sore_greater_30 == False and high_load_list[b_index] == 0):
            assert b == 0
        elif daily_list[b_index] == 0 and high_load_list[b_index] == 0 and severity_list[b_index] >= 2.5:
            assert b == 0
        else:
            if b == 1:
                assert b == 1
            else:
                j = 0
        b_index += 1


def check_pre_all_inhibit_agonist_exercise_numbers():
    b_index = 0

    body_part_factory = BodyPartFactory()

    for b in pre_mobilize_list:
        sore_greater_30 = (history_list[b_index] in [6, 7] and day_list[b_index] == 10)
        if (b == 1 and
                not (daily_list[b_index] == 0 and history_list[b_index] not in [1, 2, 10] and sore_greater_30 == False)
                and not (daily_list[b_index] == 0 and severity_list[b_index] >= 2.5)):
            body_part_full = body_part_factory.get_body_part(body_part_choice_list[b_index])
            agonists = body_part_full.agonists
            for agonist in agonists:
                agonist_body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation(agonist), None), False)
                agonist_exercises = set(convert_assigned_exercises(agonist_body_part.inhibit_exercises))
                assigned_exercises = set(pre_inhibit_exercises_list[b_index])
                if len(agonist_exercises.intersection(assigned_exercises)) > 0:
                    assert len(agonist_exercises.intersection(assigned_exercises)) > 0
                else:
                    assert body_part_choice_list[b_index].location in joints and daily_list[b_index] == 0
                    print(body_part_choice_list[b_index].location)
        b_index += 1


def check_pre_all_inhibit_antagonist_exercise_numbers():
    b_index = 0

    body_part_factory = BodyPartFactory()

    for b in pre_mobilize_list:
        if (b == 1 and body_part_choice_list[b_index].location in joints and daily_list[b_index] == 1 and
                history_list[b_index] in [1, 2, 10]):
            body_part_full = body_part_factory.get_body_part(body_part_choice_list[b_index])
            antagonists = body_part_full.antagonists
            if antagonists is not None:
                for antagonist in antagonists:
                    antagonist_body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation(antagonist), None), False)
                    antagonist_exercises = set(convert_assigned_exercises(antagonist_body_part.inhibit_exercises))
                    assigned_exercises = set(pre_inhibit_exercises_list[b_index])
                    assert len(antagonist_exercises.intersection(assigned_exercises)) > 0
        b_index += 1


def check_pre_all_inhibit_prime_mover_exercise_numbers():
    b_index = 0

    body_part_factory = BodyPartFactory()

    for b in pre_mobilize_list:
        if b == 1 and high_load_list[b_index] == 1:
            body_part_full = body_part_factory.get_body_part(BodyPartLocation.general)
            prime_movers = body_part_full.agonists
            prime_mover_exercises = []
            for prime_mover in prime_movers:
                prime_mover_body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation(prime_mover), None), False)
                prime_mover_exercises.extend(convert_assigned_exercises(prime_mover_body_part.inhibit_exercises))
            assigned_exercises = set(pre_inhibit_exercises_list[b_index])
            prime_mover_exercises = set(prime_mover_exercises)
            assert len(prime_mover_exercises.intersection(assigned_exercises)) > 0
        b_index += 1


def check_pre_non_efficient_inhibit_synergist_exercise_numbers():
    b_index = 0

    body_part_factory = BodyPartFactory()

    for b in pre_mobilize_list:
        sore_greater_30 = (history_list[b_index] in [6, 7] and day_list[b_index] == 10)
        if (b == 1 and ((history_list[b_index] in [1, 2, 6, 7, 10] and severity_list[b_index] >= 0.5)
                        or (history_list in [0, 12] and severity_list[b_index] >= 1.5))
                and not (daily_list[b_index] == 0 and history_list[b_index] not in[1, 2, 10] and sore_greater_30 == False)
                and not (daily_list[b_index] == 0 and severity_list[b_index] >= 2.5)):
            body_part_full = body_part_factory.get_body_part(body_part_choice_list[b_index])
            synergists = body_part_full.synergists
            if synergists is not None:
                for synergist in synergists:
                    synergist_body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation(synergist), None), False)
                    synergist_exercises = set(
                        convert_assigned_exercises(synergist_body_part.inhibit_exercises))
                    assigned_exercises = set(pre_inhibit_exercises_list[b_index])
                    assert len(synergist_exercises.intersection(assigned_exercises)) > 0
        b_index += 1


def check_pre_comprehensive_inhibit_stabilizer_exercise_numbers():
    b_index = 0

    body_part_factory = BodyPartFactory()

    for b in pre_mobilize_list:
        if (b == 1 and ((history_list[b_index] in [1, 2, 6, 7, 10] and severity_list[b_index] >= 0.5)
                        or (history_list in [0, 12] and severity_list[b_index] >= 1.5))
                and daily_list[b_index] == 1):
            body_part_full = body_part_factory.get_body_part(body_part_choice_list[b_index])
            stabilizers = body_part_full.stabilizers
            if stabilizers is not None:
                for stabilizer in stabilizers:
                    stabilizer_body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation(stabilizer), None), False)
                    stabilizer_exercises = set(
                        convert_assigned_exercises(stabilizer_body_part.inhibit_exercises))
                    assigned_exercises = set(pre_inhibit_exercises_list[b_index])
                    assert len(stabilizer_exercises.intersection(assigned_exercises)) > 0
        b_index += 1


def check_pre_all_static_stretch_agonist_exercise_numbers():
    b_index = 0

    body_part_factory = BodyPartFactory()

    for b in pre_mobilize_list:
        sore_greater_30 = (history_list[b_index] in [6, 7] and day_list[b_index] == 10)
        if (b == 1 and
                not (daily_list[b_index] == 0 and history_list[b_index] not in [1, 2, 10] and sore_greater_30 == False)
                and not (daily_list[b_index] == 0 and severity_list[b_index] >= 2.5)
                and severity_list[b_index] < 3.5):
            body_part_full = body_part_factory.get_body_part(body_part_choice_list[b_index])
            agonists = body_part_full.agonists
            for agonist in agonists:
                agonist_body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation(agonist), None), False)
                agonist_exercises = set(convert_assigned_exercises(agonist_body_part.static_stretch_exercises))
                if pre_static_stretch_exercises_list[b_index] is not None:
                    assigned_exercises = set(pre_static_stretch_exercises_list[b_index])
                else:
                    assigned_exercises = {0}
                if len(agonist_exercises.intersection(assigned_exercises)) > 0:
                    assert len(agonist_exercises.intersection(assigned_exercises)) > 0
                else:
                    assert body_part_choice_list[b_index].location in joints and daily_list[b_index] == 0
                    print(body_part_choice_list[b_index].location)
        b_index += 1


def check_pre_all_static_stretch_antagonist_exercise_numbers():
    b_index = 0

    body_part_factory = BodyPartFactory()

    for b in pre_mobilize_list:
        if (b == 1 and body_part_choice_list[b_index].location in joints and daily_list[b_index] == 1 and
                history_list[b_index] in [1, 2, 10] and severity_list[b_index] < 3.5):
            body_part_full = body_part_factory.get_body_part(body_part_choice_list[b_index])
            antagonists = body_part_full.antagonists
            if antagonists is not None:
                for antagonist in antagonists:
                    antagonist_body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation(antagonist), None), False)
                    antagonist_exercises = set(
                        convert_assigned_exercises(antagonist_body_part.static_stretch_exercises))
                    assigned_exercises = set(pre_static_stretch_exercises_list[b_index])
                    assert len(antagonist_exercises.intersection(assigned_exercises)) > 0
        b_index += 1


def check_pre_all_active_stretch_agonist_exercise_numbers():
    b_index = 0

    body_part_factory = BodyPartFactory()

    for b in pre_mobilize_list:
        if b == 1 and daily_list[b_index] == 1 and severity_list[b_index] < 3.5:
            body_part_full = body_part_factory.get_body_part(body_part_choice_list[b_index])
            agonists = body_part_full.agonists
            for agonist in agonists:
                agonist_body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation(agonist), None), False)
                agonist_exercises = set(convert_assigned_exercises(agonist_body_part.active_stretch_exercises))
                assigned_exercises = set(pre_active_stretch_exercises_list[b_index])
                assert len(agonist_exercises.intersection(assigned_exercises)) > 0
        b_index += 1


def check_pre_all_active_stretch_antagonist_exercise_numbers():
    b_index = 0

    body_part_factory = BodyPartFactory()

    for b in pre_mobilize_list:
        if (b == 1 and body_part_choice_list[b_index].location in joints and daily_list[b_index] == 1 and
                history_list[b_index] in [1, 2, 10] and severity_list[b_index] < 3.5):
            body_part_full = body_part_factory.get_body_part(body_part_choice_list[b_index])
            antagonists = body_part_full.antagonists
            if antagonists is not None:
                for antagonist in antagonists:
                    antagonist_body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation(antagonist), None), False)
                    antagonist_exercises = set(
                        convert_assigned_exercises(antagonist_body_part.active_stretch_exercises))
                    assigned_exercises = set(pre_active_stretch_exercises_list[b_index])
                    assert len(antagonist_exercises.intersection(assigned_exercises)) > 0
        b_index += 1


def check_pre_non_efficient_active_stretch_synergist_exercise_numbers():
    b_index = 0

    body_part_factory = BodyPartFactory()

    for b in pre_mobilize_list:
        if (b == 1 and ((history_list[b_index] in [1, 2, 6, 7, 10] and severity_list[b_index] >= 0.5)
                        or (history_list in [0, 12] and severity_list[b_index] >= 1.5))
                and daily_list[b_index] == 1 and severity_list[b_index] < 3.5):
            body_part_full = body_part_factory.get_body_part(body_part_choice_list[b_index])
            synergists = body_part_full.synergists
            if synergists is not None:
                for synergist in synergists:
                    synergist_body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation(synergist), None), False)
                    synergist_exercises = set(
                        convert_assigned_exercises(synergist_body_part.active_stretch_exercises))
                    assigned_exercises = set(pre_active_stretch_exercises_list[b_index])
                    assert len(synergist_exercises.intersection(assigned_exercises)) > 0
        b_index += 1


def check_pre_comprehensive_active_stretch_stabilizer_exercise_numbers():
    b_index = 0

    body_part_factory = BodyPartFactory()

    for b in pre_mobilize_list:
        if (b == 1 and ((history_list[b_index] in [1, 2, 6, 7, 10] and severity_list[b_index] >= 0.5)
                        or (history_list in [0, 12] and severity_list[b_index] >= 1.5))
                and daily_list[b_index] == 1 and severity_list[b_index] < 3.5):
            body_part_full = body_part_factory.get_body_part(body_part_choice_list[b_index])
            stabilizers = body_part_full.stabilizers
            if stabilizers is not None:
                for stabilizer in stabilizers:
                    stabilizer_body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation(stabilizer), None), False)
                    stabilizer_exercises = set(
                        convert_assigned_exercises(stabilizer_body_part.active_stretch_exercises))
                    assigned_exercises = set(pre_active_stretch_exercises_list[b_index])
                    assert len(stabilizer_exercises.intersection(assigned_exercises)) > 0
        b_index += 1


def check_pre_all_active_stretch_prime_mover_exercise_numbers():
    b_index = 0

    body_part_factory = BodyPartFactory()

    for b in pre_mobilize_list:
        if b == 1 and high_load_list[b_index] == 1 and severity_list[b_index] < 3.5:
            body_part_full = body_part_factory.get_body_part(BodyPartLocation.general)
            prime_movers = body_part_full.agonists
            prime_mover_exercises = []
            for prime_mover in prime_movers:
                prime_mover_body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation(prime_mover), None), False)
                prime_mover_exercises.extend(convert_assigned_exercises(prime_mover_body_part.active_stretch_exercises))
            assigned_exercises = set(pre_active_stretch_exercises_list[b_index])
            prime_mover_exercises = set(prime_mover_exercises)
            assert len(prime_mover_exercises.intersection(assigned_exercises)) > 0
        b_index += 1


def check_pre_all_isolated_activation_antagonist_exercise_numbers():
    b_index = 0

    body_part_factory = BodyPartFactory()

    for b in pre_mobilize_list:
        sore_greater_30 = (history_list[b_index] in [6, 7] and day_list[b_index] == 10)
        if (b == 1 and (sore_greater_30 is True or history_list[b_index] in [1, 2, 10])
                and severity_list[b_index] < 2.5):
            body_part_full = body_part_factory.get_body_part(body_part_choice_list[b_index])
            antagonists = body_part_full.antagonists
            if antagonists is not None and antagonists != []:
                antagonist_exercises = []
                for antagonist in antagonists:
                    antagonist_body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation(antagonist), None), False)
                    antagonist_exercises.extend(
                        convert_assigned_exercises(antagonist_body_part.isolated_activate_exercises))
                assigned_exercises = set(pre_isolated_activate_exercises_list[b_index])
                antagonist_exercises = set(antagonist_exercises)
                assert len(antagonist_exercises.intersection(assigned_exercises)) > 0
        b_index += 1


def check_pre_all_isolated_activate_sport_antagonist_exercise_numbers():
    b_index = 0

    body_part_factory = BodyPartFactory()

    for b in pre_mobilize_list:
        if b == 1 and high_load_list[b_index] == 1 and severity_list[b_index] < 2.5:
            body_part_full = body_part_factory.get_body_part(BodyPartLocation.general)
            antagonists = body_part_full.antagonists
            if antagonists is not None:
                for antagonist in antagonists:
                    antagonist_body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation(antagonist), None), False)
                    antagonist_exercises = set(convert_assigned_exercises(antagonist_body_part.isolated_activate_exercises))
                    assigned_exercises = set(pre_isolated_activate_exercises_list[b_index])
                    assert len(antagonist_exercises.intersection(assigned_exercises)) > 0
        b_index += 1


def check_pre_non_efficient_isolated_activation_synergist_exercise_numbers():
    b_index = 0

    body_part_factory = BodyPartFactory()

    for b in pre_mobilize_list:
        sore_greater_30 = (history_list[b_index] in [6, 7] and day_list[b_index] == 10)
        if b == 1 and (sore_greater_30 is True or history_list[b_index] in [1, 2, 10]) and severity_list[b_index] < 2.5:
            body_part_full = body_part_factory.get_body_part(body_part_choice_list[b_index])
            synergists = body_part_full.synergists
            if synergists is not None:
                for synergist in synergists:
                    synergist_body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation(synergist), None), False)
                    synergist_exercises = set(convert_assigned_exercises(synergist_body_part.isolated_activate_exercises))
                    assigned_exercises = set(pre_isolated_activate_exercises_list[b_index])
                    assert len(synergist_exercises.intersection(assigned_exercises)) > 0
        b_index += 1


def check_pre_all_static_integrate_general_set_exercise_numbers():
    b_index = 0

    body_part_factory = BodyPartFactory()

    for b in pre_mobilize_list:
        sore_greater_30 = (history_list[b_index] in [6, 7] and day_list[b_index] == 10)
        if (b == 1 and (sore_greater_30 is True or history_list[b_index] in [1, 2, 10] or high_load_list[b_index] == 1)
                and severity_list[b_index] < 2.5):
            body_part_full = body_part_factory.get_body_part(BodyPartLocation.general, None)
            general_set_exercises = set(convert_assigned_exercises(body_part_full.static_integrate_exercises))
            assigned_exercises = set(pre_static_integrate_exercises_list[b_index])
            assert len(general_set_exercises.intersection(assigned_exercises)) == len(assigned_exercises)
        b_index += 1


def check_cool_down_present():
    b_index = 0
    for b in cool_down_list:
        if (high_load_list[b_index] == 1 and ((history_list[b_index] in [1, 2, 10] and severity_list[b_index] < 2.5)
                                              or (history_list[b_index] in [0, 6, 7, 12] and
                                                  severity_list[b_index] < 3.5))):
            assert b == 1
        else:
            if b == 0:
                assert b == 0
            else:
                assert history_list[b_index] in [0, 6, 7, 12] and severity_list[b_index] >= 3.5
                print("Compensated Error")
        b_index += 1


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


def convert_assigned_exercises(assigned_exercises):

    exercise_list = []

    for a in assigned_exercises:
        exercise_list.append(a.exercise.id)

    return exercise_list


def test_pre_mobilize_comprehensive():
    read_spreadsheet("comprehensive")
    check_pre_mobilize_present()
    check_pre_all_inhibit_agonist_exercise_numbers()
    check_pre_all_inhibit_antagonist_exercise_numbers()
    check_pre_all_inhibit_prime_mover_exercise_numbers()
    check_pre_non_efficient_inhibit_synergist_exercise_numbers()
    check_pre_comprehensive_inhibit_stabilizer_exercise_numbers()
    check_pre_all_static_stretch_agonist_exercise_numbers()
    check_pre_all_static_stretch_antagonist_exercise_numbers()
    check_pre_all_active_stretch_agonist_exercise_numbers()
    check_pre_all_active_stretch_antagonist_exercise_numbers()
    check_pre_non_efficient_active_stretch_synergist_exercise_numbers()
    check_pre_comprehensive_active_stretch_stabilizer_exercise_numbers()
    check_pre_all_active_stretch_prime_mover_exercise_numbers()
    check_pre_all_isolated_activation_antagonist_exercise_numbers()
    check_pre_all_isolated_activate_sport_antagonist_exercise_numbers()
    check_pre_non_efficient_isolated_activation_synergist_exercise_numbers()
    check_pre_all_static_integrate_general_set_exercise_numbers()


def test_cool_down_comprehensive():
    read_spreadsheet("comprehensive")
    check_cool_down_present()
