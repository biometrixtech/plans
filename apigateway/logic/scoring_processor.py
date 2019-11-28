from models.scoring import MovementVariableScores


class ScoringProcessor(object):
    def __init__(self):
        pass

    def get_apt_scores(self, asymmetry, movement_patterns):

        left_apt_ankle_pitch = movement_patterns.apt_ankle_pitch.left
        right_apt_ankle_pitch = movement_patterns.apt_ankle_pitch.right
        combined_equations = [left_apt_ankle_pitch, right_apt_ankle_pitch]

        scores = MovementVariableScores()
        scores.asymmetry_regression_coefficient_score = self.get_left_right_elasticity_difference_score([left_apt_ankle_pitch], [right_apt_ankle_pitch])
        scores.asymmetry_medians_score = self.get_median_scoring(asymmetry.anterior_pelvic_tilt.left, asymmetry.anterior_pelvic_tilt.right)
        scores.asymmetry_fatigue_score = self.get_left_right_adf_difference_score([left_apt_ankle_pitch], [right_apt_ankle_pitch])
        scores.movement_dysfunction_score = self.get_elasticity_dysfunction_score(combined_equations)
        scores.fatigue_score = self.get_adf_score(combined_equations)

        scores.asymmetry_score = (scores.asymmetry_regression_coefficient_score * .5) + (scores.asymmetry_medians_score * .3) + (scores.asymmetry_fatigue_score * .2)

        scores.overall_score = (scores.asymmetry_score * .5) + (scores.movement_dysfunction_score * .3) + (scores.fatigue_score * .2)

        return scores

    def get_hip_drop_scores(self, asymmetry, movement_patterns):

        left_hip_drop_apt = movement_patterns.hip_drop_apt.left
        left_hip_drop_pva = movement_patterns.hip_drop_pva.left
        right_hip_drop_apt = movement_patterns.hip_drop_apt.right
        right_hip_drop_pva = movement_patterns.hip_drop_pva.right
        combined_equations = [left_hip_drop_apt, right_hip_drop_apt, left_hip_drop_pva, right_hip_drop_pva]

        scores = MovementVariableScores()
        scores.asymmetry_regression_coefficient_score = self.get_left_right_elasticity_difference_score([left_hip_drop_apt, left_hip_drop_pva], [right_hip_drop_apt, right_hip_drop_pva])
        scores.asymmetry_medians_score = self.get_median_scoring(asymmetry.hip_drop.left, asymmetry.hip_drop.right)
        scores.asymmetry_fatigue_score = self.get_left_right_adf_difference_score([left_hip_drop_apt, left_hip_drop_pva], [right_hip_drop_apt, right_hip_drop_pva])
        scores.movement_dysfunction_score = self.get_elasticity_dysfunction_score(combined_equations)
        scores.fatigue_score = self.get_adf_score(combined_equations)

        scores.asymmetry_score = (scores.asymmetry_regression_coefficient_score * .5) + (scores.asymmetry_medians_score * .3) + (scores.asymmetry_fatigue_score * .2)

        scores.overall_score = (scores.asymmetry_score * .5) + (scores.movement_dysfunction_score * .3) + (scores.fatigue_score * .2)

        return scores

    def get_ankle_pitch_scores(self, movement_patterns):

        left_apt_ankle_pitch = movement_patterns.apt_ankle_pitch.left
        left_hip_rotation_ankle_pitch = movement_patterns.hip_rotation_ankle_pitch.left
        right_apt_ankle_pitch = movement_patterns.apt_ankle_pitch.right
        right_hip_rotation_ankle_pitch = movement_patterns.hip_rotation_ankle_pitch.right
        combined_equations = [left_apt_ankle_pitch, right_apt_ankle_pitch, left_hip_rotation_ankle_pitch, right_hip_rotation_ankle_pitch]

        scores = MovementVariableScores()
        scores.asymmetry_regression_coefficient_score = self.get_left_right_elasticity_difference_score([left_apt_ankle_pitch, left_hip_rotation_ankle_pitch], [right_apt_ankle_pitch, right_hip_rotation_ankle_pitch])
        scores.asymmetry_medians_score = 0
        scores.asymmetry_fatigue_score = 0
        scores.movement_dysfunction_score = self.get_elasticity_dysfunction_score(combined_equations)
        scores.fatigue_score = self.get_adf_score(combined_equations)

        scores.asymmetry_score = scores.asymmetry_regression_coefficient_score

        scores.overall_score = (scores.asymmetry_score * .6) + (scores.movement_dysfunction_score * .5)

        return scores

    def get_knee_valgus_scores(self, asymmetry, movement_patterns):

        left_knee_valgus_hip_drop = movement_patterns.knee_valgus_hip_drop.left
        left_knee_valgus_pva = movement_patterns.knee_valgus_pva.left
        left_knee_valgus_apt = movement_patterns.knee_valgus_apt.left
        right_knee_valgus_hip_drop = movement_patterns.knee_valgus_hip_drop.right
        right_knee_valgus_pva = movement_patterns.knee_valgus_pva.right
        right_knee_valgus_apt = movement_patterns.knee_valgus_apt.right
        combined_equations = [left_knee_valgus_hip_drop, right_knee_valgus_hip_drop, left_knee_valgus_pva, right_knee_valgus_pva, left_knee_valgus_apt, right_knee_valgus_apt]

        scores = MovementVariableScores()
        scores.asymmetry_regression_coefficient_score = self.get_left_right_elasticity_difference_score([left_knee_valgus_hip_drop, left_knee_valgus_pva, left_knee_valgus_apt], [right_knee_valgus_hip_drop, right_knee_valgus_pva, right_knee_valgus_apt])
        scores.asymmetry_medians_score = self.get_median_scoring(asymmetry.knee_valgus.left, asymmetry.knee_valgus.right)
        scores.asymmetry_fatigue_score = self.get_left_right_adf_difference_score([left_knee_valgus_hip_drop, left_knee_valgus_pva, left_knee_valgus_apt], [right_knee_valgus_hip_drop, right_knee_valgus_pva, right_knee_valgus_apt])
        scores.movement_dysfunction_score = self.get_elasticity_dysfunction_score(combined_equations)
        scores.fatigue_score = self.get_adf_score(combined_equations)

        scores.asymmetry_score = (scores.asymmetry_regression_coefficient_score * .5) + (scores.asymmetry_medians_score * .3) + (scores.asymmetry_fatigue_score * .2)

        scores.overall_score = (scores.asymmetry_score * .5) + (scores.movement_dysfunction_score * .3) + (scores.fatigue_score * .2)

        return scores

    def get_hip_rotation_scores(self, asymmetry, movement_patterns):

        left_hip_rotation_apt = movement_patterns.hip_rotation_apt.left
        left_hip_rotation_ankle_pitch = movement_patterns.hip_rotation_ankle_pitch.left
        right_hip_rotation_apt = movement_patterns.hip_rotation_apt.right
        right_hip_rotation_ankle_pitch = movement_patterns.hip_rotation_ankle_pitch.right
        combined_equations = [left_hip_rotation_apt, right_hip_rotation_apt, left_hip_rotation_ankle_pitch, right_hip_rotation_ankle_pitch]

        scores = MovementVariableScores()
        scores.asymmetry_regression_coefficient_score = self.get_left_right_elasticity_difference_score([left_hip_rotation_apt, right_hip_rotation_apt], [left_hip_rotation_ankle_pitch, right_hip_rotation_ankle_pitch])
        scores.asymmetry_medians_score = self.get_median_scoring(asymmetry.hip_rotation.left, asymmetry.hip_rotation.right)
        scores.asymmetry_fatigue_score = self.get_left_right_adf_difference_score([left_hip_rotation_apt, right_hip_rotation_apt], [left_hip_rotation_ankle_pitch, right_hip_rotation_ankle_pitch])
        scores.movement_dysfunction_score = self.get_elasticity_dysfunction_score(combined_equations)
        scores.fatigue_score = self.get_adf_score(combined_equations)

        scores.asymmetry_score = (scores.asymmetry_regression_coefficient_score * .5) + (scores.asymmetry_medians_score * .3) + (scores.asymmetry_fatigue_score * .2)

        scores.overall_score = (scores.asymmetry_score * .5) + (scores.movement_dysfunction_score * .3) + (scores.fatigue_score * .2)

        return scores

    def get_left_right_elasticity_difference_score(self, left_equation_list, right_equation_list):

        score = 100
        if len(left_equation_list) > 0:
            ratio = 1 / float(len(left_equation_list))
        else:
            return score

        for coefficient_count in range(0, len(left_equation_list)):
            left_coefficient = max(0, left_equation_list[coefficient_count].elasticity)
            right_coefficient = max(0, right_equation_list[coefficient_count].elasticity)

            coefficient_diff = abs(right_coefficient - left_coefficient)

            score = score - (coefficient_diff * 30 * ratio)

        return score

    def get_median_scoring(self, left, right):

        score = 100

        if left >= right > 0:
            percent_diff = ((left - right) / left) * 100
        elif right >= left > 0:
            percent_diff = ((right - left) / right) * 100
        else:
            percent_diff = 100

        score = score - (percent_diff * .9)

        return score

    def get_left_right_adf_difference_score(self, left_equation_list, right_equation_list):

        score = 100
        if len(left_equation_list) > 0:
            ratio = 1 / float(len(left_equation_list))
        else:
            return score

        for coefficient_count in range(0, len(left_equation_list)):
            if ((left_equation_list[coefficient_count].y_adf != 0 and right_equation_list[coefficient_count].y_adf == 0) or
                    (left_equation_list[coefficient_count].y_adf == 0 and right_equation_list[coefficient_count].y_adf != 0)):
                score = score - (25 * ratio)

        return score

    def get_elasticity_dysfunction_score(self, equation_list):

        score = 100
        if len(equation_list) > 0:
            ratio = 1 / float(len(equation_list))
        else:
            return score

        for coefficient_count in range(0, len(equation_list)):
            if equation_list[coefficient_count].elasticity >= 0:
                score = score - (equation_list[coefficient_count].elasticity * 50 * ratio)

        return score

    def get_adf_score(self, equation_list):

        score = 100
        if len(equation_list) > 0:
            ratio = 1 / float(len(equation_list))
        else:
            return score

        for coefficient_count in range(0, len(equation_list)):
            if equation_list[coefficient_count].y_adf != 0:
                score = score - (25 * ratio)

        return score

