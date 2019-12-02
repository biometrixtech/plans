from logic.scoring_processor import ScoringProcessor
from models.scoring import MovementVariableScores
import movement_pattern_history as mph
from models.functional_movement import MovementPatterns
from models.asymmetry import Asymmetry, AnteriorPelvicTilt, HipDrop, KneeValgus, HipRotation


def test_get_apt_scores():

    proc = ScoringProcessor()
    history, session_details = mph.run_a_regressions()
    days = len(history)
    for i in range(days):
        if history[i] is not None:
            movement_patterns_response = mph.create_elastticity_adf(history[i])
            movement_patterns = MovementPatterns.json_deserialise(movement_patterns_response)
            asymmetry = Asymmetry()
            apt = AnteriorPelvicTilt(6, 8)
            hip_drop = HipDrop(7, 8.5)
            asymmetry.anterior_pelvic_tilt = apt
            asymmetry.hip_drop = hip_drop
            knee_valgus = KneeValgus(6,7)
            asymmetry.knee_valgus = knee_valgus
            hip_rotation = HipRotation(7,9)
            asymmetry.hip_rotation = hip_rotation
            apt_scores = proc.get_apt_scores(asymmetry, movement_patterns)
            ankle_pitch_scores = proc.get_ankle_pitch_scores(movement_patterns)
            hip_drop_scores= proc.get_hip_drop_scores(asymmetry, movement_patterns)
            knee_valgus_scores = proc.get_knee_valgus_scores(asymmetry, movement_patterns)
            hip_rotation_scores = proc.get_hip_rotation_scores(asymmetry, movement_patterns)
            j=0
    j=0