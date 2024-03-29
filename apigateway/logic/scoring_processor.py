from models.scoring import MovementVariableScore, MovementVariableScores, MovementVariableSummary, SessionScoringSummary, ScoreInfluencer, EquationType
from models.scoring import MovementVariableSummaryData, RecoveryQuality, DataCard, MovementVariableType, DataCardData
from models.styles import LegendColor, DataCardVisualType
from models.asymmetry import AnteriorPelvicTilt, KneeValgus, AnklePitch, HipRotation
import statistics
from math import sqrt


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

        session_scoring_summary = SessionScoringSummary()

        total_score = 0
        total_score_denom = 0
        all_scores = []
        # all_data_cards = []
        if session.asymmetry is not None and session.asymmetry.anterior_pelvic_tilt is not None:
            apt_scores = scoring_processor.get_apt_scores(session.asymmetry, session.movement_patterns)
            # apt_scores.overall_score.color = 11
            session_scoring_summary.apt = self.get_apt_moving_variable_summary(apt_scores, session)
            session_scoring_summary.all_data_cards.extend(session_scoring_summary.apt.data_cards)
            total_score += apt_scores.overall_score.value * .35
            total_score_denom += .35
            all_scores.append(apt_scores)
        if session.asymmetry is not None and session.asymmetry.ankle_pitch is not None:
            ankle_pitch_scores = scoring_processor.get_ankle_pitch_scores(session.movement_patterns)
            # ankle_pitch_scores.overall_score.color = 11
            session_scoring_summary.ankle_pitch = self.get_ankle_pitch_moving_variable_summary(ankle_pitch_scores, session)
            session_scoring_summary.all_data_cards.extend(session_scoring_summary.ankle_pitch.data_cards)
            all_scores.append(ankle_pitch_scores)

        if session.asymmetry is not None and session.asymmetry.hip_drop is not None:
            hip_drop_scores = scoring_processor.get_hip_drop_scores(session.asymmetry, session.movement_patterns)
            # hip_drop_scores.overall_score.color = 11
            session_scoring_summary.hip_drop = self.get_hip_drop_moving_variable_summary(hip_drop_scores, session)
            session_scoring_summary.all_data_cards.extend(session_scoring_summary.hip_drop.data_cards)
            total_score += hip_drop_scores.overall_score.value * .25
            total_score_denom += .25
            all_scores.append(hip_drop_scores)
                    
        if session.asymmetry is not None and session.asymmetry.knee_valgus is not None:
            knee_valgus_scores = scoring_processor.get_knee_valgus_scores(session.asymmetry, session.movement_patterns)
            # knee_valgus_scores.overall_score.color = 11
            session_scoring_summary.knee_valgus = self.get_knee_valgus_moving_variable_summary(knee_valgus_scores, session)
            session_scoring_summary.all_data_cards.extend(session_scoring_summary.knee_valgus.data_cards)
            total_score += knee_valgus_scores.overall_score.value * .20
            total_score_denom += .20
            all_scores.append(knee_valgus_scores)

        if session.asymmetry is not None and session.asymmetry.hip_rotation is not None:
            hip_rotation_scores = scoring_processor.get_hip_rotation_scores(session.asymmetry, session.movement_patterns)
            # hip_rotation_scores.overall_score.color = 11
            session_scoring_summary.hip_rotation = self.get_hip_rotation_moving_variable_summary(hip_rotation_scores, session)
            session_scoring_summary.all_data_cards.extend(session_scoring_summary.hip_rotation.data_cards)
            total_score += hip_rotation_scores.overall_score.value * .20
            total_score_denom += .20
            all_scores.append(hip_rotation_scores)

        if total_score_denom > 0:
            total_score /= total_score_denom

        session_scoring_summary.event_date_time = session.event_date
        session_scoring_summary.score = scoring_processor.get_score(total_score)

        session_scoring_summary.score.text = 'workout\nmovement quality'
        session_scoring_summary.get_data_points()

        session_scoring_summary.get_summary_pills()

        return session_scoring_summary

    def get_apt_moving_variable_summary(self, apt_movement_scores, session):

        apt_movement_variable_summary = MovementVariableSummary()
        apt_movement_variable_summary.score = apt_movement_scores.overall_score
        apt_movement_variable_summary.change = apt_movement_scores.change
        apt_movement_variable_summary.data_cards = self.get_data_cards(apt_movement_scores)
        apt_movement_variable_summary.dashboard_title = "Pelvic Tilt Quality"
        apt_movement_variable_summary.child_title = "Pelvic Tilt"
        apt_movement_variable_summary.summary_text.text = "movement quality"
        apt_movement_variable_summary.summary_text.active = True
        apt_movement_variable_summary.description.text = "Pelvic Tilt measures hip position as you arch your back. Proper alignment is critical for core activation."
        apt_movement_variable_summary.description.active = True

        if session.asymmetry is not None and session.asymmetry.anterior_pelvic_tilt is not None:
            apt_movement_variable_summary.summary_data = self.get_movement_variable_summary_data(session, session.asymmetry.anterior_pelvic_tilt)

            apt_movement_variable_summary.body_side = self.get_body_side(session, session.asymmetry.anterior_pelvic_tilt)

        return apt_movement_variable_summary

    def get_movement_variable_summary_data(self, session, movement_variable_object):

        viz = MovementVariableSummaryData()
        viz.left_start_angle = 0
        viz.right_start_angle = 0
        if isinstance(movement_variable_object, KneeValgus) or isinstance(movement_variable_object, HipRotation):
            viz.multiplier = 1.5
        else:
            viz.multiplier = 1.0
        if session.asymmetry is not None and movement_variable_object is not None:

            if movement_variable_object.percent_events_asymmetric > 0:
                viz.left_y = round(movement_variable_object.left, 0)
                viz.right_y = round(movement_variable_object.right, 0)

            else:
                average_symmetry = round(
                    (
                            movement_variable_object.left + movement_variable_object.right) / float(
                        2), 0)

                viz.left_y = average_symmetry
                viz.right_y = average_symmetry
        if viz.left_y == viz.right_y:
            if isinstance(movement_variable_object, AnteriorPelvicTilt) or isinstance(movement_variable_object, AnklePitch) or isinstance(movement_variable_object, KneeValgus):
                viz.left_y_legend_color = LegendColor(26)
                viz.right_y_legend_color = LegendColor(26)
        viz.left_y_legend = viz.left_y
        viz.right_y_legend = viz.right_y
        return viz

    def get_ankle_pitch_moving_variable_summary(self, ankle_pitch_movement_scores, session):

        ankle_pitch_movement_variable_summary = MovementVariableSummary()
        ankle_pitch_movement_variable_summary.score = ankle_pitch_movement_scores.overall_score
        ankle_pitch_movement_variable_summary.change = ankle_pitch_movement_scores.change
        ankle_pitch_movement_variable_summary.data_cards = self.get_data_cards(ankle_pitch_movement_scores)
        ankle_pitch_movement_variable_summary.dashboard_title = "Leg Extension Quality"
        ankle_pitch_movement_variable_summary.child_title = "Leg Extension"
        ankle_pitch_movement_variable_summary.summary_text.text = "movement quality"
        ankle_pitch_movement_variable_summary.summary_text.active = True
        ankle_pitch_movement_variable_summary.description.text = "Leg Extension measures the range of motion accessed by hip extension & back kick."
        ankle_pitch_movement_variable_summary.description.active = True

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
        hip_drop_movement_variable_summary.change = hip_drop_movement_scores.change
        hip_drop_movement_variable_summary.data_cards = self.get_data_cards(hip_drop_movement_scores)
        hip_drop_movement_variable_summary.dashboard_title = "Hip Drop Quality"
        hip_drop_movement_variable_summary.child_title = "Hip Drop"
        hip_drop_movement_variable_summary.summary_text.text = "movement quality"
        hip_drop_movement_variable_summary.summary_text.active = True
        hip_drop_movement_variable_summary.description.text = "Hip Drop measures the position of your hips as you support the weight of your body while running."
        hip_drop_movement_variable_summary.description.active = True

        if session.asymmetry is not None and session.asymmetry.hip_drop is not None:
            hip_drop_movement_variable_summary.summary_data = self.get_movement_variable_summary_data(session,
                                                                                                      session.asymmetry.hip_drop)

            hip_drop_movement_variable_summary.body_side = self.get_body_side(session, session.asymmetry.hip_drop)

        return hip_drop_movement_variable_summary

    def get_knee_valgus_moving_variable_summary(self, knee_valgus_movement_scores, session):

        knee_valgus_movement_variable_summary = MovementVariableSummary()
        knee_valgus_movement_variable_summary.score = knee_valgus_movement_scores.overall_score
        knee_valgus_movement_variable_summary.change = knee_valgus_movement_scores.change
        knee_valgus_movement_variable_summary.data_cards = self.get_data_cards(knee_valgus_movement_scores)
        knee_valgus_movement_variable_summary.dashboard_title = "Knee Valgus Quality"
        knee_valgus_movement_variable_summary.child_title = "Knee Valgus"
        knee_valgus_movement_variable_summary.summary_text.text = "movement quality"
        knee_valgus_movement_variable_summary.summary_text.active = True
        knee_valgus_movement_variable_summary.description.text = "Knee Valgus estimates how far your knees bow inward in the loading phase of your gait."
        knee_valgus_movement_variable_summary.description.active = True

        if session.asymmetry is not None and session.asymmetry.knee_valgus is not None:
            knee_valgus_movement_variable_summary.summary_data = self.get_movement_variable_summary_data(session,
                                                                                                         session.asymmetry.knee_valgus)

            knee_valgus_movement_variable_summary.body_side = self.get_body_side(session, session.asymmetry.knee_valgus)

        return knee_valgus_movement_variable_summary

    def get_hip_rotation_moving_variable_summary(self, hip_rotation_movement_scores, session):

        hip_rotation_movement_variable_summary = MovementVariableSummary()
        hip_rotation_movement_variable_summary.score = hip_rotation_movement_scores.overall_score
        hip_rotation_movement_variable_summary.change = hip_rotation_movement_scores.change
        hip_rotation_movement_variable_summary.data_cards = self.get_data_cards(hip_rotation_movement_scores, )
        hip_rotation_movement_variable_summary.dashboard_title = "Hip Rotation Quality"
        hip_rotation_movement_variable_summary.child_title = "Hip Rotation"
        hip_rotation_movement_variable_summary.summary_text.text = "movement quality"
        hip_rotation_movement_variable_summary.summary_text.active = True
        hip_rotation_movement_variable_summary.description.text = "Hip Rotation measures the forward rotation of your hips in the loading phase of your gait."
        hip_rotation_movement_variable_summary.description.active = True

        if session.asymmetry is not None and session.asymmetry.hip_rotation is not None:
            hip_rotation_movement_variable_summary.summary_data = self.get_movement_variable_summary_data(session,
                                                                                                          session.asymmetry.hip_rotation)

            hip_rotation_movement_variable_summary.body_side = self.get_body_side(session, session.asymmetry.hip_rotation)

        return hip_rotation_movement_variable_summary

    def get_data_cards(self, movement_scores):

        # These two cards are always present
        symmetry_card = DataCard(DataCardVisualType.magnitude)
        symmetry_card.data = DataCardData.symmetry
        symmetry_card.movement_variable = movement_scores.movement_variable_type
        movement_dysfunction_card = DataCard(DataCardVisualType.magnitude)
        movement_dysfunction_card.data = DataCardData.dysfunction
        movement_dysfunction_card.movement_variable = movement_scores.movement_variable_type

        symmetry_card.assign_score_value(movement_scores.asymmetry_score)
        symmetry_card.get_symmetry_text(movement_scores)

        movement_dysfunction_card.assign_score_value(movement_scores.movement_dysfunction_score)
        movement_dysfunction_card.get_dysfunction_text(movement_scores)

        cards = [movement_dysfunction_card, symmetry_card]
        if movement_scores.fatigue_score.value is not None and  movement_scores.fatigue_score.value < 100:
            fatigue_card = DataCard(DataCardVisualType.boolean)
            fatigue_card.movement_variable = movement_scores.movement_variable_type
            fatigue_card.data = DataCardData.fatigue
            fatigue_card.value = True
            fatigue_card.color = 5
            fatigue_card.title_text = "Possible Fatigue"
            fatigue_card.icon = 2
            fatigue_card.get_fatigue_text()
            cards.append(fatigue_card)

        return cards


class ScoringProcessor(object):
    def __init__(self):
        pass

    def get_apt_scores(self, asymmetry, movement_patterns):
        combined_equations = []
        left_equation_list = []
        right_equation_list = []
        equations = []

        if movement_patterns is not None:
            if movement_patterns.apt_ankle_pitch is not None:
                left_apt_ankle_pitch = movement_patterns.apt_ankle_pitch.left
                right_apt_ankle_pitch = movement_patterns.apt_ankle_pitch.right
                combined_equations = [left_apt_ankle_pitch, right_apt_ankle_pitch]
                left_equation_list = [left_apt_ankle_pitch]
                right_equation_list = [right_apt_ankle_pitch]
                equations.append(EquationType.apt_ankle_pitch)

        scores = MovementVariableScores(MovementVariableType.apt)
        scores.asymmetry_regression_coefficient_score = self.get_left_right_elasticity_difference_score(left_equation_list, right_equation_list, equations, scores)
        scores.asymmetry_medians_score = self.get_median_scoring(asymmetry.anterior_pelvic_tilt.left, asymmetry.anterior_pelvic_tilt.right, scores=scores)
        scores.asymmetry_fatigue_score = self.get_left_right_adf_difference_score(left_equation_list, right_equation_list, equations, scores)
        scores.movement_dysfunction_score = self.get_score(self.get_elasticity_dysfunction_score(combined_equations, equations, scores))
        scores.fatigue_score = self.get_score(self.get_adf_score(combined_equations, equations, scores))

        scores.asymmetry_score = self.get_score((scores.asymmetry_regression_coefficient_score * .5) + (scores.asymmetry_medians_score * .3) + (scores.asymmetry_fatigue_score * .2))

        scores.overall_score = self.get_score((scores.asymmetry_score.value * .5) + (scores.movement_dysfunction_score.value * .3) + (scores.fatigue_score.value * .2))

        # TODO: update with real logic
        # scores.change.value = -1.2
        # scores.change.text = "pts"
        # scores.change.color = 6
        # scores.change.active = True

        return scores

    def get_hip_drop_scores(self, asymmetry, movement_patterns):
        combined_equations = []
        left_equation_list = []
        right_equation_list = []
        equations = []
        if movement_patterns is not None:
            if movement_patterns.hip_drop_apt is not None:
                left_hip_drop_apt = movement_patterns.hip_drop_apt.left
                right_hip_drop_apt = movement_patterns.hip_drop_apt.right
                combined_equations.extend([left_hip_drop_apt, right_hip_drop_apt])
                left_equation_list.append(left_hip_drop_apt)
                right_equation_list.append(right_hip_drop_apt)
                equations.append(EquationType.hip_drop_apt)
            if movement_patterns.hip_drop_pva is not None:
                left_hip_drop_pva = movement_patterns.hip_drop_pva.left
                right_hip_drop_pva = movement_patterns.hip_drop_pva.right
                combined_equations.extend([left_hip_drop_pva, right_hip_drop_pva])
                left_equation_list.append(left_hip_drop_pva)
                right_equation_list.append(right_hip_drop_pva)
                equations.append(EquationType.hip_drop_pva)

        scores = MovementVariableScores(MovementVariableType.hip_drop)
        scores.asymmetry_regression_coefficient_score = self.get_left_right_elasticity_difference_score(left_equation_list, right_equation_list, equations, scores)
        scores.asymmetry_medians_score = self.get_median_scoring(asymmetry.hip_drop.left, asymmetry.hip_drop.right, scores=scores)
        scores.asymmetry_fatigue_score = self.get_left_right_adf_difference_score(left_equation_list, right_equation_list, equations, scores)
        scores.movement_dysfunction_score = self.get_score(self.get_elasticity_dysfunction_score(combined_equations, equations, scores))
        scores.fatigue_score = self.get_score(self.get_adf_score(combined_equations, equations, scores))

        scores.asymmetry_score = self.get_score((scores.asymmetry_regression_coefficient_score * .5) + (scores.asymmetry_medians_score * .3) + (scores.asymmetry_fatigue_score * .2))

        scores.overall_score = self.get_score((scores.asymmetry_score.value * .5) + (scores.movement_dysfunction_score.value * .3) + (scores.fatigue_score.value * .2))

        # TODO: update with real logic
        # scores.change.value = 2.0
        # scores.change.text = "pts"
        # scores.change.color = 13
        # scores.change.active = True

        return scores

    def get_ankle_pitch_scores(self, movement_patterns):
        combined_equations = []
        left_equation_list = []
        right_equation_list = []
        equations = []
        if movement_patterns is not None:
            if movement_patterns.apt_ankle_pitch is not None:
                left_apt_ankle_pitch = movement_patterns.apt_ankle_pitch.left
                right_apt_ankle_pitch = movement_patterns.apt_ankle_pitch.right
                combined_equations.extend([left_apt_ankle_pitch, right_apt_ankle_pitch])
                left_equation_list.append(left_apt_ankle_pitch)
                right_equation_list.append(right_apt_ankle_pitch)
                equations.append(EquationType.apt_ankle_pitch)

            if movement_patterns.hip_rotation_ankle_pitch is not None:
                left_hip_rotation_ankle_pitch = movement_patterns.hip_rotation_ankle_pitch.left
                right_hip_rotation_ankle_pitch = movement_patterns.hip_rotation_ankle_pitch.right
                combined_equations.extend([left_hip_rotation_ankle_pitch, right_hip_rotation_ankle_pitch])
                left_equation_list.append(left_hip_rotation_ankle_pitch)
                right_equation_list.append(right_hip_rotation_ankle_pitch)
                equations.append(EquationType.hip_rotation_ankle_pitch)

        scores = MovementVariableScores(MovementVariableType.ankle_pitch)
        scores.asymmetry_regression_coefficient_score = self.get_left_right_elasticity_difference_score(left_equation_list, right_equation_list, equations, scores)
        scores.asymmetry_medians_score = 0
        scores.asymmetry_fatigue_score = 0
        scores.movement_dysfunction_score = self.get_score(self.get_elasticity_dysfunction_score(combined_equations, equations, scores))
        scores.fatigue_score = self.get_score(100) # TODO: This is such that it does not appear in fatigue card

        scores.asymmetry_score = self.get_score((scores.asymmetry_regression_coefficient_score * .5) + 50)

        scores.overall_score = self.get_score((scores.asymmetry_score.value * .5) + (scores.movement_dysfunction_score.value * .3) + 20)

        # TODO: update with real logic
        # scores.change.value = 0.0
        # scores.change.text = "pts"
        # scores.change.color = 13
        # scores.change.active = True

        return scores

    def get_knee_valgus_scores(self, asymmetry, movement_patterns):
        combined_equations = []
        left_equation_list = []
        right_equation_list = []
        equations = []
        if movement_patterns is not None:
            if movement_patterns.knee_valgus_hip_drop is not None:
                left_knee_valgus_hip_drop = movement_patterns.knee_valgus_hip_drop.left
                right_knee_valgus_hip_drop = movement_patterns.knee_valgus_hip_drop.right
                combined_equations.extend([left_knee_valgus_hip_drop, right_knee_valgus_hip_drop])
                left_equation_list.append(left_knee_valgus_hip_drop)
                right_equation_list.append(right_knee_valgus_hip_drop)
                equations.append(EquationType.knee_valgus_hip_drop)

            if movement_patterns.knee_valgus_pva is not None:
                left_knee_valgus_pva = movement_patterns.knee_valgus_pva.left
                right_knee_valgus_pva = movement_patterns.knee_valgus_pva.right
                combined_equations.extend([left_knee_valgus_pva, right_knee_valgus_pva])
                left_equation_list.append(left_knee_valgus_pva)
                right_equation_list.append(right_knee_valgus_pva)
                equations.append(EquationType.knee_valgus_pva)

            if movement_patterns.knee_valgus_apt is not None:
                left_knee_valgus_apt = movement_patterns.knee_valgus_apt.left
                right_knee_valgus_apt = movement_patterns.knee_valgus_apt.right
                combined_equations.extend([left_knee_valgus_apt, right_knee_valgus_apt])
                left_equation_list.append(left_knee_valgus_apt)
                right_equation_list.append(right_knee_valgus_apt)
                equations.append(EquationType.knee_valgus_apt)

        # combined_equations = [left_knee_valgus_hip_drop, right_knee_valgus_hip_drop, left_knee_valgus_pva, right_knee_valgus_pva, left_knee_valgus_apt, right_knee_valgus_apt]

        scores = MovementVariableScores(MovementVariableType.knee_valgus)
        scores.asymmetry_regression_coefficient_score = self.get_left_right_elasticity_difference_score(left_equation_list, right_equation_list, equations, scores)
        scores.asymmetry_medians_score = self.get_median_scoring(asymmetry.knee_valgus.left, asymmetry.knee_valgus.right, scores=scores)
        scores.asymmetry_fatigue_score = self.get_left_right_adf_difference_score(left_equation_list, right_equation_list, equations, scores)
        scores.movement_dysfunction_score = self.get_score(self.get_elasticity_dysfunction_score(combined_equations, equations, scores))
        scores.fatigue_score = self.get_score(self.get_adf_score(combined_equations, equations, scores))

        scores.asymmetry_score = self.get_score((scores.asymmetry_regression_coefficient_score * .5) + (scores.asymmetry_medians_score * .3) + (scores.asymmetry_fatigue_score * .2))

        scores.overall_score = self.get_score((scores.asymmetry_score.value * .5) + (scores.movement_dysfunction_score.value * .3) + (scores.fatigue_score.value * .2))

        return scores

    def get_hip_rotation_scores(self, asymmetry, movement_patterns):

        combined_equations = []
        left_equation_list = []
        right_equation_list = []
        equations = []
        if movement_patterns is not None:
            if movement_patterns.hip_rotation_apt is not None:
                left_hip_rotation_apt = movement_patterns.hip_rotation_apt.left
                right_hip_rotation_apt = movement_patterns.hip_rotation_apt.right
                combined_equations.extend([left_hip_rotation_apt, right_hip_rotation_apt])
                left_equation_list.append(left_hip_rotation_apt)
                right_equation_list.append(right_hip_rotation_apt)
                equations.append(EquationType.hip_rotation_apt)

            if movement_patterns.hip_rotation_ankle_pitch is not None:
                left_hip_rotation_ankle_pitch = movement_patterns.hip_rotation_ankle_pitch.left
                right_hip_rotation_ankle_pitch = movement_patterns.hip_rotation_ankle_pitch.right
                combined_equations.extend([left_hip_rotation_ankle_pitch, right_hip_rotation_ankle_pitch])
                left_equation_list.append(left_hip_rotation_ankle_pitch)
                right_equation_list.append(right_hip_rotation_ankle_pitch)
                equations.append(EquationType.hip_rotation_ankle_pitch)

        scores = MovementVariableScores(MovementVariableType.hip_rotation)
        scores.asymmetry_regression_coefficient_score = self.get_left_right_elasticity_difference_score(left_equation_list, right_equation_list, equations, scores)
        scores.asymmetry_medians_score = self.get_median_scoring(asymmetry.hip_rotation.left, asymmetry.hip_rotation.right, scores=scores)
        scores.asymmetry_fatigue_score = self.get_left_right_adf_difference_score(right_equation_list, right_equation_list, equations, scores)
        scores.movement_dysfunction_score = self.get_score(self.get_elasticity_dysfunction_score(combined_equations, equations, scores))
        scores.fatigue_score = self.get_score(self.get_adf_score(combined_equations, equations, scores))

        scores.asymmetry_score = self.get_score((scores.asymmetry_regression_coefficient_score * .5) + (scores.asymmetry_medians_score * .3) + (scores.asymmetry_fatigue_score * .2))

        scores.overall_score = self.get_score((scores.asymmetry_score.value * .5) + (scores.movement_dysfunction_score.value * .3) + (scores.fatigue_score.value * .2))

        return scores

    def get_score(self, value):

        movement_score = MovementVariableScore()
        movement_score.value = int(value) if value is not None else None
        movement_score.text = ""
        # Define colors based on threshold. Make sure this matches the thresholds in the data cards
        if movement_score.value == 100:
            movement_score.color = LegendColor.success_light
        elif movement_score.value >= 90:
            movement_score.color = LegendColor.yellow_light
        elif movement_score.value >= 80:
            movement_score.color = LegendColor.warning_light
        else:
            movement_score.color = LegendColor.error_light
        movement_score.active = True

        return movement_score

    def get_left_right_elasticity_difference_score(self, left_equation_list, right_equation_list, equations, scores):

        score = 100
        if len(left_equation_list) > 0:
            ratio = 1 / float(len(left_equation_list))
        else:
            return score

        for coefficient_count in range(0, len(left_equation_list)):
            left_coefficient = max(0, left_equation_list[coefficient_count].elasticity)
            right_coefficient = max(0, right_equation_list[coefficient_count].elasticity)

            coefficient_diff = abs(right_coefficient - left_coefficient)
            if coefficient_diff > 0:
                influencer = ScoreInfluencer()
                influencer.equation_type = equations[coefficient_count]
                if right_coefficient > left_coefficient:
                    influencer.side = 2
                else:
                    influencer.side = 1
                scores.asymmetry_regression_coefficient_score_influencers.append(influencer)

            score -= sqrt(coefficient_diff) * 30 * ratio

        return score

    def get_median_scoring(self, left, right, scores, min_diff=0.5, max_diff=10):

        score = 100
        diff = abs(left - right)
        if left == right or diff < min_diff:
            percent_diff = 0
        elif diff >= max_diff:
            percent_diff = 100
        else:
            percent_diff = (diff / max_diff) * 100
        if percent_diff != 0:
            if left > right:
                scores.medians_score_side = 1
            else:
                scores.medians_score_side = 2

        # score = score - (percent_diff * .9)

        # alt
        score = score - percent_diff

        score = max(0, score)

        return score

    def get_left_right_adf_difference_score(self, left_equation_list, right_equation_list, equations, scores):

        score = 100
        if len(left_equation_list) > 0:
            ratio = 1 / float(len(left_equation_list))
        else:
            return score

        influencers = []

        for coefficient_count in range(0, len(left_equation_list)):
            if ((left_equation_list[coefficient_count].y_adf != 0 and right_equation_list[coefficient_count].y_adf == 0) or
                    (left_equation_list[coefficient_count].y_adf == 0 and right_equation_list[coefficient_count].y_adf != 0)):
                score = score - (25 * ratio)
                # record that this equation influenced the score
                influencer = ScoreInfluencer()
                influencer.equation_type = equations[coefficient_count]
                if left_equation_list[coefficient_count].y_adf != 0:
                    influencer.side = 1
                else:
                    influencer.side = 2
                influencers.append(influencer)

        left_adfs = 0
        right_adfs = 0

        for i in influencers:
            if i.side == 1:
                left_adfs += 1
            else:
                right_adfs += 1

        if left_adfs > 0 and right_adfs > 0:
            influencers = []
            score = 100

        scores.asymmetry_fatigue_score_influencers.extend(influencers)

        return score

    def get_elasticity_dysfunction_score(self, equation_list, equations, scores):

        score = 100
        if len(equation_list) > 0:
            ratio = 1 / float(len(equation_list))
        else:
            return score
        #
        # for coefficient_count in range(0, len(equation_list)):
        #     if equation_list[coefficient_count].elasticity >= 0:
        #         score = score - (equation_list[coefficient_count].elasticity * 50 * ratio)

        influencing_equations = set()
        # alternative
        for coefficient_count in range(0, len(equation_list)):
            if equation_list[coefficient_count].elasticity > 0:
                score -= sqrt(equation_list[coefficient_count].elasticity) * 30 * ratio
                # record that this equation influenced the score
                influencing_equations.add(equations[coefficient_count//2].value)
        for eq in influencing_equations:
            influencer = ScoreInfluencer()
            influencer.equation_type = eq
            scores.movement_dysfunction_influencers.append(influencer)

        score = max(0, score)

        return score

    def get_adf_score(self, equation_list, equations, scores):

        score = 100
        if len(equation_list) > 0:
            ratio = 1 / float(len(equation_list))
        else:
            return score

        influencing_equations = set()
        for coefficient_count in range(0, len(equation_list)):
            if equation_list[coefficient_count].y_adf != 0:
                score = score - (25 * ratio)
                # record that this equation influenced the score
                influencing_equations.add(equations[coefficient_count//2].value)
        for eq in influencing_equations:
            influencer = ScoreInfluencer()
            influencer.equation_type = eq
            scores.fatigue_score_influencers.append(influencer)

        return score
