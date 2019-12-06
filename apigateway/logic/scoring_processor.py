from models.scoring import MovementVariableScore, MovementVariableScores, MovementVariableSummary, DataCard, SessionScoringSummary, MovementVariableSummaryData, RecoveryQuality, DataCardType
import statistics


class ScoringSummaryProcessor(object):
    def __init__(self):
        pass

    def get_recovery_quality(self, session_summaries, recovery_date):

        recovery_quality_list = []

        scoring_processor = ScoringProcessor()

        for s in session_summaries:
            if s.event_date_time.date() == recovery_date:
                recovery_quality_list.append(s.score.value)

        recovery_quality = RecoveryQuality()

        if len(recovery_quality_list) > 0:
            recovery_quality.date = recovery_date
            recovery_quality.score = scoring_processor.get_score(statistics.mean(recovery_quality_list))

        return recovery_quality

    def get_session_summary(self, session):

        scoring_processor = ScoringProcessor()

        apt_scores = scoring_processor.get_apt_scores(session.asymmetry, session.movement_patterns)
        apt_scores.overall_score.color = 11
        ankle_pitch_scores = scoring_processor.get_ankle_pitch_scores(session.movement_patterns)
        ankle_pitch_scores.overall_score.color = 11
        hip_drop_scores = scoring_processor.get_hip_drop_scores(session.asymmetry, session.movement_patterns)
        hip_drop_scores.overall_score.color = 11
        knee_valgus_scores = scoring_processor.get_knee_valgus_scores(session.asymmetry, session.movement_patterns)
        knee_valgus_scores.overall_score.color = 11
        hip_rotation_scores = scoring_processor.get_hip_rotation_scores(session.asymmetry, session.movement_patterns)
        hip_rotation_scores.overall_score.color = 11

        session_scoring_summary = SessionScoringSummary()
        session_scoring_summary.event_date_time = session.event_date

        total_score = (apt_scores.overall_score.value * .35) + (hip_drop_scores.overall_score.value * .25) + (
                    knee_valgus_scores.overall_score.value * .20) + (hip_rotation_scores.overall_score.value * .20)

        session_scoring_summary.score = scoring_processor.get_score(total_score)
        session_scoring_summary.score.text = 'total movement efficiency score'
        session_scoring_summary.apt = self.get_apt_moving_variable_summary(apt_scores, session)
        session_scoring_summary.ankle_pitch = self.get_ankle_pitch_moving_variable_summary(ankle_pitch_scores, session)
        session_scoring_summary.hip_drop = self.get_hip_drop_moving_variable_summary(hip_drop_scores, session)
        session_scoring_summary.knee_valgus = self.get_knee_valgus_moving_variable_summary(knee_valgus_scores, session)
        session_scoring_summary.hip_rotation = self.get_hip_rotation_moving_variable_summary(hip_rotation_scores, session)
        session_scoring_summary.get_data_points()
        all_scores = [apt_scores, ankle_pitch_scores, hip_drop_scores, knee_valgus_scores, hip_rotation_scores]
        session_scoring_summary.get_summary_pills(all_scores)

        return session_scoring_summary

    def get_apt_moving_variable_summary(self, apt_movement_scores, session):

        apt_movement_variable_summary = MovementVariableSummary()
        apt_movement_variable_summary.score = apt_movement_scores.overall_score
        apt_movement_variable_summary.data_cards = self.get_data_cards(apt_movement_scores)
        apt_movement_variable_summary.dashboard_title = "Pelvic Tilt Efficiency"
        apt_movement_variable_summary.child_title = "Pelvic Tilt"
        apt_movement_variable_summary.summary_text.text = "movement efficiency"
        apt_movement_variable_summary.description.text = "Anterior pelvic motion asymmetry can be caused by uneven terrain or by imbalance in the lats, hip flexors, and a nearly a dozen other muscles."

        if session.asymmetry is not None and session.asymmetry.anterior_pelvic_tilt is not None:
            apt_movement_variable_summary.summary_data = self.get_movement_variable_summary_data(session, session.asymmetry.anterior_pelvic_tilt)

            apt_movement_variable_summary.body_side = self.get_body_side(session, session.asymmetry.anterior_pelvic_tilt)

        return apt_movement_variable_summary

    def get_movement_variable_summary_data(self, session, movement_variable_object):

        viz = MovementVariableSummaryData()
        viz.left_start_angle = 0
        viz.right_start_angle = 0
        viz.multiplier = 1.0
        if session.asymmetry is not None and movement_variable_object is not None:

            if movement_variable_object.percent_events_asymmetric > 0:
                viz.left_y = movement_variable_object.left
                viz.right_y = movement_variable_object.right

            else:
                average_symmetry = round(
                    (
                            movement_variable_object.left + movement_variable_object.right) / float(
                        2), 0)

                viz.left_y = average_symmetry
                viz.right_y = average_symmetry
        return viz

    def get_ankle_pitch_moving_variable_summary(self, ankle_pitch_movement_scores, session):

        ankle_pitch_movement_variable_summary = MovementVariableSummary()
        ankle_pitch_movement_variable_summary.score = ankle_pitch_movement_scores.overall_score
        ankle_pitch_movement_variable_summary.data_cards = self.get_data_cards(ankle_pitch_movement_scores)
        ankle_pitch_movement_variable_summary.dashboard_title = "Leg Extension Efficiency"
        ankle_pitch_movement_variable_summary.child_title = "Leg Extension"
        ankle_pitch_movement_variable_summary.summary_text.text = "movement efficiency"
        ankle_pitch_movement_variable_summary.description.text = "Leg extention motion asymmetry can be caused by something, I don't really know what"

        if session.asymmetry is not None and session.asymmetry.ankle_pitch is not None:
            ankle_pitch_movement_variable_summary.summary_data = self.get_movement_variable_summary_data(session, session.asymmetry.ankle_pitch)

            ankle_pitch_movement_variable_summary.body_side = self.get_body_side(session, session.asymmetry.ankle_pitch)

        return ankle_pitch_movement_variable_summary

    def get_body_side(self, session, movement_variable_object):

        body_side = 0

        if session.asymmetry is not None and movement_variable_object is not None:
            if movement_variable_object.percent_events_asymmetric > 0:
                if movement_variable_object.left > movement_variable_object.right:
                    body_side = 1
                else:
                    body_side = 2
        return body_side

    def get_hip_drop_moving_variable_summary(self, hip_drop_movement_scores, session):

        hip_drop_movement_variable_summary = MovementVariableSummary()
        hip_drop_movement_variable_summary.score = hip_drop_movement_scores.overall_score
        hip_drop_movement_variable_summary.data_cards = self.get_data_cards(hip_drop_movement_scores)
        hip_drop_movement_variable_summary.dashboard_title = "Hip Drop Efficiency"
        hip_drop_movement_variable_summary.child_title = "Hip Drop"
        hip_drop_movement_variable_summary.summary_text.text = "movement efficiency"
        hip_drop_movement_variable_summary.description.text = "Hip Drop motion asymmetry can be caused by something, I don't really know what"

        if session.asymmetry is not None and session.asymmetry.hip_drop is not None:
            hip_drop_movement_variable_summary.summary_data = self.get_movement_variable_summary_data(session,
                                                                                                      session.asymmetry.hip_drop)

            hip_drop_movement_variable_summary.body_side = self.get_body_side(session, session.asymmetry.hip_drop)

        return hip_drop_movement_variable_summary

    def get_knee_valgus_moving_variable_summary(self, knee_valgus_movement_scores, session):

        knee_valgus_movement_variable_summary = MovementVariableSummary()
        knee_valgus_movement_variable_summary.score = knee_valgus_movement_scores.overall_score
        knee_valgus_movement_variable_summary.data_cards = self.get_data_cards(knee_valgus_movement_scores)
        knee_valgus_movement_variable_summary.dashboard_title = "Knee Valgus Efficiency"
        knee_valgus_movement_variable_summary.child_title = "Knee Valgus"
        knee_valgus_movement_variable_summary.summary_text.text = "movement efficiency"
        knee_valgus_movement_variable_summary.description.text = "Knee Valgus motion asymmetry can be caused by something, I don't really know what"

        if session.asymmetry is not None and session.asymmetry.knee_valgus is not None:
            knee_valgus_movement_variable_summary.summary_data = self.get_movement_variable_summary_data(session,
                                                                                                         session.asymmetry.knee_valgus)

            knee_valgus_movement_variable_summary.body_side = self.get_body_side(session, session.asymmetry.knee_valgus)

        return knee_valgus_movement_variable_summary

    def get_hip_rotation_moving_variable_summary(self, hip_rotation_movement_scores, session):

        hip_rotation_movement_variable_summary = MovementVariableSummary()
        hip_rotation_movement_variable_summary.score = hip_rotation_movement_scores.overall_score
        hip_rotation_movement_variable_summary.data_cards = self.get_data_cards(hip_rotation_movement_scores)
        hip_rotation_movement_variable_summary.dashboard_title = "Hip Rotation Efficiency"
        hip_rotation_movement_variable_summary.child_title = "Hip Rotation"
        hip_rotation_movement_variable_summary.summary_text.text = "movement efficiency"
        hip_rotation_movement_variable_summary.description.text = "Hip Rotation motion asymmetry can be caused by something, I don't really know what"

        if session.asymmetry is not None and session.asymmetry.hip_rotation is not None:
            hip_rotation_movement_variable_summary.summary_data = self.get_movement_variable_summary_data(session,
                                                                                                          session.asymmetry.hip_rotation)

            hip_rotation_movement_variable_summary.body_side = self.get_body_side(session, session.asymmetry.hip_rotation)

        return hip_rotation_movement_variable_summary

    def get_data_cards(self, movement_scores):

        asymmetry_card = DataCard(DataCardType.categorical)
        movement_dysfunction_card = DataCard(DataCardType.magnitude)
        fatigue_card = DataCard(DataCardType.boolean)

        asymmetry_card.assign_score_value(movement_scores.asymmetry_score.value)
        movement_dysfunction_card.assign_score_value(movement_scores.movement_dysfunction_score.value)
        fatigue_card.assign_score_value(movement_scores.fatigue_score.value)

        cards = [asymmetry_card, movement_dysfunction_card, fatigue_card]

        return cards


class ScoringProcessor(object):
    def __init__(self):
        pass

    def get_apt_scores(self, asymmetry, movement_patterns):
        combined_equations = []
        left_equation_list = []
        right_equation_list = []

        if movement_patterns is not None:
            if movement_patterns.apt_ankle_pitch is not None:
                left_apt_ankle_pitch = movement_patterns.apt_ankle_pitch.left
                right_apt_ankle_pitch = movement_patterns.apt_ankle_pitch.right
                combined_equations = [left_apt_ankle_pitch, right_apt_ankle_pitch]
                left_equation_list = [left_apt_ankle_pitch]
                right_equation_list = [right_apt_ankle_pitch]

        scores = MovementVariableScores()
        scores.asymmetry_regression_coefficient_score = self.get_left_right_elasticity_difference_score(left_equation_list, right_equation_list)
        if asymmetry is not None and asymmetry.anterior_pelvic_tilt is not None:
            scores.asymmetry_medians_score = self.get_median_scoring(asymmetry.anterior_pelvic_tilt.left, asymmetry.anterior_pelvic_tilt.right)
        scores.asymmetry_fatigue_score = self.get_left_right_adf_difference_score(left_equation_list, right_equation_list)
        scores.movement_dysfunction_score = self.get_score(self.get_elasticity_dysfunction_score(combined_equations))
        scores.fatigue_score = self.get_score(self.get_adf_score(combined_equations))

        scores.asymmetry_score = self.get_score((scores.asymmetry_regression_coefficient_score * .5) + (scores.asymmetry_medians_score * .3) + (scores.asymmetry_fatigue_score * .2))

        scores.overall_score = self.get_score((scores.asymmetry_score.value * .5) + (scores.movement_dysfunction_score.value * .3) + (scores.fatigue_score.value * .2))

        return scores

    def get_hip_drop_scores(self, asymmetry, movement_patterns):
        combined_equations = []
        left_equation_list = []
        right_equation_list = []
        if movement_patterns is not None:
            if movement_patterns.hip_drop_apt is not None:
                left_hip_drop_apt = movement_patterns.hip_drop_apt.left
                right_hip_drop_apt = movement_patterns.hip_drop_apt.right
                combined_equations.extend([left_hip_drop_apt, right_hip_drop_apt])
                left_equation_list.append(left_hip_drop_apt)
                right_equation_list.append(right_hip_drop_apt)
            if movement_patterns.hip_drop_apt is not None:
                left_hip_drop_pva = movement_patterns.hip_drop_pva.left
                right_hip_drop_pva = movement_patterns.hip_drop_pva.right
                combined_equations.extend([left_hip_drop_pva, right_hip_drop_pva])
                left_equation_list.append(left_hip_drop_pva)
                right_equation_list.append(right_hip_drop_pva)

        scores = MovementVariableScores()
        scores.asymmetry_regression_coefficient_score = self.get_left_right_elasticity_difference_score(left_equation_list, right_equation_list)
        if asymmetry is not None and asymmetry.hip_drop is not None:
            scores.asymmetry_medians_score = self.get_median_scoring(asymmetry.hip_drop.left, asymmetry.hip_drop.right)
        scores.asymmetry_fatigue_score = self.get_left_right_adf_difference_score(left_equation_list, right_equation_list)
        scores.movement_dysfunction_score = self.get_score(self.get_elasticity_dysfunction_score(combined_equations))
        scores.fatigue_score = self.get_score(self.get_adf_score(combined_equations))

        scores.asymmetry_score = self.get_score((scores.asymmetry_regression_coefficient_score * .5) + (scores.asymmetry_medians_score * .3) + (scores.asymmetry_fatigue_score * .2))

        scores.overall_score = self.get_score((scores.asymmetry_score.value * .5) + (scores.movement_dysfunction_score.value * .3) + (scores.fatigue_score.value * .2))

        return scores

    def get_ankle_pitch_scores(self, movement_patterns):
        combined_equations = []
        left_equation_list = []
        right_equation_list = []
        if movement_patterns is not None:
            if movement_patterns.apt_ankle_pitch is not None:
                left_apt_ankle_pitch = movement_patterns.apt_ankle_pitch.left
                right_apt_ankle_pitch = movement_patterns.apt_ankle_pitch.right
                combined_equations.extend([left_apt_ankle_pitch, right_apt_ankle_pitch])
                left_equation_list.append(left_apt_ankle_pitch)
                right_equation_list.append(right_apt_ankle_pitch)

            if movement_patterns.hip_rotation_ankle_pitch is not None:
                left_hip_rotation_ankle_pitch = movement_patterns.hip_rotation_ankle_pitch.left
                right_hip_rotation_ankle_pitch = movement_patterns.hip_rotation_ankle_pitch.right
                combined_equations.extend([left_hip_rotation_ankle_pitch, right_hip_rotation_ankle_pitch])
                left_equation_list.append(left_hip_rotation_ankle_pitch)
                right_equation_list.append(right_hip_rotation_ankle_pitch)

        scores = MovementVariableScores()
        scores.asymmetry_regression_coefficient_score = self.get_left_right_elasticity_difference_score(left_equation_list, right_equation_list)
        scores.asymmetry_medians_score = 0
        scores.asymmetry_fatigue_score = 0
        scores.movement_dysfunction_score = self.get_score(self.get_elasticity_dysfunction_score(combined_equations))
        scores.fatigue_score = self.get_score(0)

        scores.asymmetry_score = self.get_score((scores.asymmetry_regression_coefficient_score * .5) + 50)

        scores.overall_score = self.get_score((scores.asymmetry_score.value * .5) + (scores.movement_dysfunction_score.value * .3) + 20)

        return scores

    def get_knee_valgus_scores(self, asymmetry, movement_patterns):
        combined_equations = []
        left_equation_list = []
        right_equation_list = []
        if movement_patterns is not None:
            if movement_patterns.knee_valgus_hip_drop is not None:
                left_knee_valgus_hip_drop = movement_patterns.knee_valgus_hip_drop.left
                right_knee_valgus_hip_drop = movement_patterns.knee_valgus_hip_drop.right
                combined_equations.extend([left_knee_valgus_hip_drop, right_knee_valgus_hip_drop])
                left_equation_list.append(left_knee_valgus_hip_drop)
                right_equation_list.append(right_knee_valgus_hip_drop)

            if movement_patterns.knee_valgus_pva is not None:
                left_knee_valgus_pva = movement_patterns.knee_valgus_pva.left
                right_knee_valgus_pva = movement_patterns.knee_valgus_pva.right
                combined_equations.extend([left_knee_valgus_pva, right_knee_valgus_pva])
                left_equation_list.append(left_knee_valgus_pva)
                right_equation_list.append(right_knee_valgus_pva)

            if movement_patterns.knee_valgus_apt is not None:
                left_knee_valgus_apt = movement_patterns.knee_valgus_apt.left
                right_knee_valgus_apt = movement_patterns.knee_valgus_apt.right
                combined_equations.extend([left_knee_valgus_apt, right_knee_valgus_apt])
                left_equation_list.append(left_knee_valgus_apt)
                right_equation_list.append(right_knee_valgus_apt)

        # combined_equations = [left_knee_valgus_hip_drop, right_knee_valgus_hip_drop, left_knee_valgus_pva, right_knee_valgus_pva, left_knee_valgus_apt, right_knee_valgus_apt]

        scores = MovementVariableScores()
        scores.asymmetry_regression_coefficient_score = self.get_left_right_elasticity_difference_score(left_equation_list, right_equation_list)
        if asymmetry is not None and asymmetry.knee_valgus is not None:
            scores.asymmetry_medians_score = self.get_median_scoring(asymmetry.knee_valgus.left, asymmetry.knee_valgus.right)
        scores.asymmetry_fatigue_score = self.get_left_right_adf_difference_score(left_equation_list, right_equation_list)
        scores.movement_dysfunction_score = self.get_score(self.get_elasticity_dysfunction_score(combined_equations))
        scores.fatigue_score = self.get_score(self.get_adf_score(combined_equations))

        scores.asymmetry_score = self.get_score((scores.asymmetry_regression_coefficient_score * .5) + (scores.asymmetry_medians_score * .3) + (scores.asymmetry_fatigue_score * .2))

        scores.overall_score = self.get_score((scores.asymmetry_score.value * .5) + (scores.movement_dysfunction_score.value * .3) + (scores.fatigue_score.value * .2))

        return scores

    def get_hip_rotation_scores(self, asymmetry, movement_patterns):

        combined_equations = []
        left_equation_list = []
        right_equation_list = []
        if movement_patterns is not None:
            if movement_patterns.hip_rotation_apt is not None:
                left_hip_rotation_apt = movement_patterns.hip_rotation_apt.left
                right_hip_rotation_apt = movement_patterns.hip_rotation_apt.right
                combined_equations.extend([left_hip_rotation_apt, right_hip_rotation_apt])
                left_equation_list.append(left_hip_rotation_apt)
                right_equation_list.append(right_hip_rotation_apt)

            if movement_patterns.hip_rotation_ankle_pitch is not None:
                left_hip_rotation_ankle_pitch = movement_patterns.hip_rotation_ankle_pitch.left
                right_hip_rotation_ankle_pitch = movement_patterns.hip_rotation_ankle_pitch.right
                combined_equations.extend([left_hip_rotation_ankle_pitch, right_hip_rotation_ankle_pitch])
                left_equation_list.append(left_hip_rotation_ankle_pitch)
                right_equation_list.append(right_hip_rotation_ankle_pitch)

        scores = MovementVariableScores()
        scores.asymmetry_regression_coefficient_score = self.get_left_right_elasticity_difference_score(left_equation_list, right_equation_list)
        if asymmetry is not None and asymmetry.hip_rotation is not None:
            scores.asymmetry_medians_score = self.get_median_scoring(asymmetry.hip_rotation.left, asymmetry.hip_rotation.right)
        scores.asymmetry_fatigue_score = self.get_left_right_adf_difference_score(right_equation_list, right_equation_list)
        scores.movement_dysfunction_score = self.get_score(self.get_elasticity_dysfunction_score(combined_equations))
        scores.fatigue_score = self.get_score(self.get_adf_score(combined_equations))

        scores.asymmetry_score = self.get_score((scores.asymmetry_regression_coefficient_score * .5) + (scores.asymmetry_medians_score * .3) + (scores.asymmetry_fatigue_score * .2))

        scores.overall_score = self.get_score((scores.asymmetry_score.value * .5) + (scores.movement_dysfunction_score.value * .3) + (scores.fatigue_score.value * .2))

        return scores

    def get_score(self, value):

        movement_score = MovementVariableScore()
        movement_score.value = int(value) if value is not None else None
        movement_score.text = ""
        movement_score.color = None
        movement_score.active = True

        return movement_score

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

