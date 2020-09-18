from logic.workout_processing import WorkoutProcessor


def test_get_rpe_from_rep_max_1_1():

    workout_processor = WorkoutProcessor()
    rpe = workout_processor.get_rpe_from_rep_max(1, 1)

    assert 10 == rpe

def test_get_rpe_from_rep_max_2_1():

    workout_processor = WorkoutProcessor()
    rpe = workout_processor.get_rpe_from_rep_max(2, 1)

    assert 9.0 == rpe

def test_get_rpe_from_rep_max_3_1():

    workout_processor = WorkoutProcessor()
    rpe = workout_processor.get_rpe_from_rep_max(3, 1)

    assert 8.0 == rpe

def test_get_rpe_from_rep_max_5_3():

    workout_processor = WorkoutProcessor()
    rpe = workout_processor.get_rpe_from_rep_max(5, 3)

    assert 8.0 == rpe

def test_get_rpe_from_rep_max_2_2():

    workout_processor = WorkoutProcessor()
    rpe = workout_processor.get_rpe_from_rep_max(2, 2)

    assert 10 == rpe

def test_get_rpe_from_rep_max_15_13():

    workout_processor = WorkoutProcessor()
    rpe = workout_processor.get_rpe_from_rep_max(15, 13)

    assert 8.3 == rpe


def test_get_rpe_from_rep_max_15_5():

    workout_processor = WorkoutProcessor()
    rpe = workout_processor.get_rpe_from_rep_max(15, 5)

    assert 1.0 == rpe

def test_get_rpe_from_rep_max_5_1():

    workout_processor = WorkoutProcessor()
    rpe = workout_processor.get_rpe_from_rep_max(5, 1)

    assert 6.0 == rpe

def test_get_rpe_from_rep_max_6_1():

    workout_processor = WorkoutProcessor()
    rpe = workout_processor.get_rpe_from_rep_max(6, 1)

    assert 5.0 == rpe

def test_get_rpe_from_rep_max_7_1():

    workout_processor = WorkoutProcessor()
    rpe = workout_processor.get_rpe_from_rep_max(7, 1)

    assert 4.0 == rpe

def test_get_rpe_from_rep_max_5_5():

    workout_processor = WorkoutProcessor()
    rpe = workout_processor.get_rpe_from_rep_max(5, 5)

    assert 10.0 == rpe

def test_get_rpe_from_rep_max_10_1():

    workout_processor = WorkoutProcessor()
    rpe = workout_processor.get_rpe_from_rep_max(10, 1)

    assert 1.0 == rpe

def test_get_rpe_from_rep_max_11_1():

    workout_processor = WorkoutProcessor()
    rpe = workout_processor.get_rpe_from_rep_max(11, 1)

    assert 1.0 == rpe

def test_get_reps_for_percent_rep_max_100():

    workout_processor = WorkoutProcessor()
    reps = workout_processor.get_reps_for_percent_rep_max(100)

    assert 1 == reps

def test_get_reps_for_percent_rep_max_94():

    workout_processor = WorkoutProcessor()
    reps = workout_processor.get_reps_for_percent_rep_max(94)

    assert 2 == reps

def test_get_reps_for_percent_rep_max_91():

    workout_processor = WorkoutProcessor()
    reps = workout_processor.get_reps_for_percent_rep_max(91)

    assert 3 == reps

def test_get_reps_for_percent_rep_max_89():

    workout_processor = WorkoutProcessor()
    reps = workout_processor.get_reps_for_percent_rep_max(89)

    assert 4 == reps

def test_get_reps_for_percent_rep_max_86():

    workout_processor = WorkoutProcessor()
    reps = workout_processor.get_reps_for_percent_rep_max(86)

    assert 5 == reps

def test_get_reps_for_percent_rep_max_83():

    workout_processor = WorkoutProcessor()
    reps = workout_processor.get_reps_for_percent_rep_max(83)

    assert 6 == reps

def test_get_reps_for_percent_rep_max_81():

    workout_processor = WorkoutProcessor()
    reps = workout_processor.get_reps_for_percent_rep_max(81)

    assert 7 == reps

def test_get_reps_for_percent_rep_max_79():

    workout_processor = WorkoutProcessor()
    reps = workout_processor.get_reps_for_percent_rep_max(79)

    assert 8 == reps

def test_get_reps_for_percent_rep_max_77():

    workout_processor = WorkoutProcessor()
    reps = workout_processor.get_reps_for_percent_rep_max(77)

    assert 9 == reps

def test_get_reps_for_percent_rep_max_75():

    workout_processor = WorkoutProcessor()
    reps = workout_processor.get_reps_for_percent_rep_max(75)

    assert 10 == reps


def test_get_reps_for_percent_rep_max_73():

    workout_processor = WorkoutProcessor()
    reps = workout_processor.get_reps_for_percent_rep_max(73)

    assert 11 == reps


def test_get_reps_for_percent_rep_max_72():

    workout_processor = WorkoutProcessor()
    reps = workout_processor.get_reps_for_percent_rep_max(72)

    assert 12 == reps


def test_get_reps_for_percent_rep_max_71():

    workout_processor = WorkoutProcessor()
    reps = workout_processor.get_reps_for_percent_rep_max(71)

    assert 12 == reps


def test_get_reps_for_percent_rep_max_70():

    workout_processor = WorkoutProcessor()
    reps = workout_processor.get_reps_for_percent_rep_max(70)

    assert 13 == reps

def test_get_reps_for_percent_rep_max_69():

    workout_processor = WorkoutProcessor()
    reps = workout_processor.get_reps_for_percent_rep_max(69)

    assert 14 == reps

def test_get_reps_for_percent_rep_max_68():

    workout_processor = WorkoutProcessor()
    reps = workout_processor.get_reps_for_percent_rep_max(68)

    assert 14 == reps


def test_get_reps_for_bodyweight_ex_98():
    workout_processor = WorkoutProcessor()
    reps = workout_processor.get_max_reps_for_bodyweight_exercises(.98)
    assert reps == 1


def test_get_reps_for_bodyweight_ex_149():
    workout_processor = WorkoutProcessor()
    reps = workout_processor.get_max_reps_for_bodyweight_exercises(1.49)
    assert reps == 14


def test_get_reps_for_bodyweight_ex_460():
    workout_processor = WorkoutProcessor()
    reps = workout_processor.get_max_reps_for_bodyweight_exercises(4.6)
    assert reps == 109


# def test_get_rpe_ranges():
#
#     workout_processor = WorkoutProcessor()
#     intensities ={'strength_endurance': {'intensity': (50, 70), 'reps': (20, 12)},
#                     'hypertrophy': {'intensity': (75, 85), 'reps': (12, 6)},
#                     'max_strength': {'intensity': (85, 100), 'reps': (5, 1) }
#                   }
#     for int_name, values in intensities.items():
#         all_rep_maxes = []
#         percentages = values['intensity']
#         reps = values['reps']
#         all_rpes = []
#         for perc in percentages:
#             for rep in range(1, reps[0] + 1):
#                 n_rep_max = workout_processor.get_reps_for_percent_rep_max(perc)
#                 rpe =  workout_processor.get_rpe_from_rep_max(n_rep_max, rep)
#                 all_rpes.append((int_name, perc, n_rep_max, rep, rpe))
#         print(all_rpes)
#     print('here')
#     # reps = workout_processor.get_reps_for_percent_rep_max(77)
#     print(workout_processor.get_reps_for_percent_rep_max(55))
#     print(workout_processor.get_rpe_from_rep_max(25, 20))