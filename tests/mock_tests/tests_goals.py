from aws_xray_sdk.core import xray_recorder
xray_recorder.configure(sampling=False)
xray_recorder.begin_segment(name="test")

from models.exercise import AssignedExercise
from models.goal import AthleteGoalType, AthleteGoal
from models.dosage import ExerciseDosage
from models.modalities import ModalityBase
from datetime import datetime


def test_low_priority_goal_count():

    exercise_1 = AssignedExercise("1")
    dosage_1 = ExerciseDosage()
    dosage_1.goal = AthleteGoal("1", 1, AthleteGoalType.pain)
    dosage_2 = ExerciseDosage()
    dosage_2.goal = AthleteGoal("2", 2, AthleteGoalType.sport)
    dosage_3 = ExerciseDosage()
    dosage_3.goal = AthleteGoal("3", 3, AthleteGoalType.sore)
    exercise_1.dosages.append(dosage_1)
    exercise_1.dosages.append(dosage_2)
    exercise_1.dosages.append(dosage_3)

    modality_base = ModalityBase(datetime.now())
    modality_base.add_goals(exercise_1.dosages)

    assert len(modality_base.goals) == 3

