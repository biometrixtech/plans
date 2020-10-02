import pandas as pd


class DemoOutput(object):
    def __init__(self):
        self.user_stats_header_line = ("date, high_relative_load_sessions, high_relative_load_score, eligible_for_high_load_trigger," +
                                       "expected_weekly_workouts, vo2_max, vo2_max_date_time, best_running_time, best_running_distance, best_running_date," +
                                       "internal_ramp, internal_monotony, internal_strain, internal_strain_events, " +
                                       "acute_internal_total_load, chronic_internal_total_load, internal_acwr, internal_freshness_index," +
                                       "power_load_ramp, power_load_monotony, power_load_strain, power_load_strain_events, " +
                                       "acute_total_power_load, chronic_total_power_load, power_load_acwr, power_load_freshness_index," +
                                       "acute_days, chronic_days, total_historical_sessions, average_weekly_internal_load," +
                                       "average_weekly_power_load,average_session_internal_load,average_session_power_load," +
                                       'functional_overreaching_workout_today,functional_overreaching_workout_1_day,' +
                                       'non_functional_overreaching_workout_today,' +
                                       'non_functional_overreaching_workout_1_day,' +
                                       'non_functional_overreaching_workout_2_day,' +
                                       "base_aerobic_training, anaerobic_threshold_training, high_intensity_anaerobic_training," +
                                       "muscular_endurance, strength_endurance, hypertrophy, maximal_strength," +
                                       "speed, sustained_power, power, maximal_power")
        self.workout_header_line = ("event_date_time, id,description, distance, duration_minutes, session_rpe, "
                                    "power_load_highest, rpe_load_highest,  training_volume, high_intensity_session, target_training_exposures")
        self.periodization_plan_header_line = ("start_date, current_date, goals, training_phase_type, athlete_persona, sub_adaptation_type_personas," +
                                               "target_training_exposures, target_weekly_rpe_load,expected_weekly_workouts," +
                                               "readiness_score, load_score, rpe_score, inflammation_level, muscle_spasm_level, internal_load_acwr_ratio, power_load_acwr_ratio," +
                                               "internal_strain_events, internal_acwr, power_load_strain_events, power_load_acwr, average_weekly_internal_load,"
                                               "base_aerobic_training, anaerobic_threshold_training, high_intensity_anaerobic_training," +
                                               "muscular_endurance, strength_endurance, hypertrophy, maximal_strength," +
                                               "speed, sustained_power, power, maximal_power," +
                                               "acute_muscle_issues, chronic_muscle_issues, excessive_strain_muscles, compensating_muscles," +
                                               "functional_overreaching_muscles, non_functional_overreaching_muscles, tendon_issues")

    def get_phase_exercise_string(self, exercise_phases):
        exercises_string = ""
        phase_exercise_string_eff = ""
        phase_exercise_string_complete = ""
        phase_exercise_string_comprehensive = ""
        for exercise_phase in exercise_phases:
            phase_exercise_string_eff = self.get_phase_exercise_string_by_duration(exercise_phase, phase_exercise_string_eff, 'efficient')
            phase_exercise_string_complete = self.get_phase_exercise_string_by_duration(exercise_phase, phase_exercise_string_complete, 'complete')
            phase_exercise_string_comprehensive = self.get_phase_exercise_string_by_duration(exercise_phase, phase_exercise_string_comprehensive, 'comprehensive')
        exercises_string += phase_exercise_string_comprehensive + ","
        exercises_string += phase_exercise_string_complete + ","
        exercises_string += phase_exercise_string_eff
        return exercises_string

    def get_phase_exercise_string_by_duration(self, exercise_phase, phase_exercise_string, duration='comprehensive'):
        if len(phase_exercise_string) > 0:
            phase_exercise_string += "; "
        phase_exercise_string += str(exercise_phase.name).upper() + ":"
        exercise_string = ""
        if len(exercise_phase.exercises) > 0:
            for exercise_id, assigned_exercise in exercise_phase.exercises.items():
                if duration == 'efficient':
                    if assigned_exercise.duration_efficient() > 0:
                        if len(exercise_string) > 0:
                            exercise_string += ";"
                        exercise_string += exercise_id
                elif duration == 'complete':
                    if assigned_exercise.duration_complete() > 0:
                        if len(exercise_string) > 0:
                            exercise_string += ";"
                        exercise_string += exercise_id
                else:
                    if len(exercise_string) > 0:
                        exercise_string += ";"
                    exercise_string += exercise_id
            if exercise_string == "":
                exercise_string = " None"
        else:
            exercise_string = " None"
        phase_exercise_string += exercise_string
        return phase_exercise_string

    def get_mobility_wod_string(self, event_date, symptoms, responsive_recovery):

        active_rest = responsive_recovery.active_rest

        phase_string = str(event_date) + ","

        if len(symptoms) > 0:
            all_soreness_string = ""
            for soreness_dict in symptoms:
                if len(all_soreness_string) > 0:
                    all_soreness_string += "|||"
                soreness_string = ""
                for key, value in soreness_dict.items():
                    if len(soreness_string) > 0:
                        soreness_string += "; "
                    if key not in ['reported_date_time', 'user_id']:
                        soreness_string += key + ":"
                        if value is None:
                            soreness_string += "None"
                        else:
                            soreness_string += str(value)
                all_soreness_string += soreness_string
            phase_string += all_soreness_string + ","
        else:
            phase_string += ","

        if active_rest is not None:
            phase_string += "Mobility WOD: Active Rest,"
            exercises_string = self.get_phase_exercise_string(active_rest.exercise_phases)
            phase_string += exercises_string
            worked = 0
        else:
            oops = 0
        phase_string += ',' # blank one for ice/cwi

        return phase_string

    def get_movement_prep_string(self, event_date, symptoms, movement_prep):

        phase_string = str(event_date) + ","

        if len(symptoms) > 0:
            all_soreness_string = ""
            for soreness_dict in symptoms:
                if len(all_soreness_string) > 0:
                    all_soreness_string += "|||"
                soreness_string = ""
                for key, value in soreness_dict.items():
                    if len(soreness_string) > 0:
                        soreness_string += "; "
                    if key not in ['reported_date_time', 'user_id']:
                        soreness_string += key + ":"
                        if value is None:
                            soreness_string += "None"
                        else:
                            soreness_string += str(value)
                all_soreness_string += soreness_string
            phase_string += all_soreness_string + ","
        else:
            phase_string += ","

        if movement_prep is not None:
            phase_string += "Movement Prep,"
            exercises_string = self.get_phase_exercise_string(movement_prep.movement_integration_prep.exercise_phases)
            phase_string += exercises_string
            worked = 0
        else:
            oops = 0
        phase_string += ',' # blank one for ice/cwi

        return phase_string

    def get_responsive_recovery_string(self, event_date, symptoms, responsive_recovery):

        active_rest = responsive_recovery.active_rest
        active_recovery = responsive_recovery.active_recovery
        ice = responsive_recovery.ice
        cwi = responsive_recovery.cold_water_immersion

        phase_string = str(event_date) + ","

        if len(symptoms) > 0:
            all_soreness_string = ""
            for soreness_dict in symptoms:
                if len(all_soreness_string) > 0:
                    all_soreness_string += "|||"
                soreness_string = ""
                for key, value in soreness_dict.items():
                    if len(soreness_string) > 0:
                        soreness_string += "; "
                    if key not in ['reported_date_time', 'user_id']:
                        soreness_string += key + ":"
                        if value is None:
                            soreness_string += "None"
                        else:
                            soreness_string += str(value)
                all_soreness_string += soreness_string
            phase_string += all_soreness_string + ","
        else:
            phase_string += ","

        if active_rest is not None:
            phase_string += "Active Rest,"
            exercises_string = self.get_phase_exercise_string(active_rest.exercise_phases)
            phase_string += exercises_string
        elif active_recovery is not None:
            phase_string += "Active Recovery,"
            exercises_string = self.get_phase_exercise_string(active_recovery.exercise_phases)
            phase_string += exercises_string
        else:
            phase_string += ","

        ice_cwi_string = ","
        if ice is not None:
            ice_cwi_string += "Ice:"
            for body_part in ice.body_parts:
                ice_cwi_string += body_part.body_part_location.name + "; side=" + str(body_part.side) + ";"
        if cwi is not None:
            if len(ice_cwi_string) > 1:
                ice_cwi_string += " "
            ice_cwi_string += "**COLD WATER IMMERSION**"
        phase_string += ice_cwi_string

        return phase_string

    def get_ird_string(self, event_date, body_part_side, body_part_injury_rik):

        ird_string = str(event_date) + ","
        ird_string += (body_part_side.body_part_location.name + "; side:" + str(body_part_side.side) + '; con_load: ' +
                       str(body_part_injury_rik.concentric_volume_today.highest_value()) + "; vol_tier: " +
                       str(body_part_injury_rik.total_volume_percent_tier) + ";" +
                       "last_ache_level:" + str(body_part_injury_rik.last_ache_level) + ";"
                                                                                        "last_knots_level:" + str(
                    body_part_injury_rik.last_knots_level) + ";"
                                                             "last_muscle_spasm_level:" + str(
                    body_part_injury_rik.last_muscle_spasm_level) + ";"
                                                                    "last_sharp_level:" + str(
                    body_part_injury_rik.last_sharp_level) + ";"
                                                             "last_tight_level:" + str(
                    body_part_injury_rik.last_tight_level) + ";"
                       # "last_ache_level:" + str(body_part_injury_rik.last_ache_level) + ";"
                       )

        return ird_string

    def get_if_present_string(self, obj, attribute):

        string_val = ""

        if getattr(obj, attribute) is not None:
            string_val += str(getattr(obj, attribute)) + ","
        else:
            string_val += ","

        return string_val

    def get_std_error_if_present_string(self, obj, attribute, is_last=False):

        string_val = ""

        if getattr(obj, attribute) is not None:
            std_obj = getattr(obj, attribute)
            std_obj_val = std_obj.highest_value()
            string_val += str(std_obj_val)

        if not is_last:
            string_val += ","

        return string_val

    def get_training_unit_if_present_string(self, obj, attribute, is_last=False):
        string_val = ""

        if getattr(obj, attribute) is not None:
            string_val += "RPE=" + str(getattr(obj, attribute).rpe.highest_value()) + ";Volume=" + str(
                getattr(obj, attribute).volume.highest_value())

        if not is_last:
            string_val += ","

        return string_val

    def get_user_stats_string(self, user_stats):
        # user_stats_header_line = ("high_relative_load_sessions, high_relative_load_score, eligible_for_high_load_trigger," +
        #                           "expected_weekly_workouts, vo2_max, vo2_max_date_time, best_running_time, best_running_distance, best_running_date," +
        #                           "internal_ramp, internal_monotony, internal_strain, internal_strain_events, " +
        #                           "acute_internal_total_load, chronic_internal_total_load, internal_acwr, internal_freshness_index," +
        #                           "acute_days, chronic_days, total_historical_sessions, average_weekly_internal_load," +
        #                           "base_aerobic_training, anaerobic_threshold_training, high_intensity_anaerobic_training," +
        #                           "muscular_endurance, strength_endurance, hypertrophy, maximal_strength," +
        #                           "speed, sustained_power, power, maximal_power")

        user_stats_string = str(user_stats.event_date) + "," + str(
            len(user_stats.high_relative_load_sessions)) + "," + str(user_stats.high_relative_load_score) + "," + str(
            user_stats.eligible_for_high_load_trigger) + ","
        user_stats_string += str(user_stats.expected_weekly_workouts) + ","

        user_stats_string += self.get_std_error_if_present_string(user_stats, "vo2_max")
        user_stats_string += self.get_if_present_string(user_stats, "vo2_max_date_time")
        user_stats_string += self.get_if_present_string(user_stats, "best_running_time")
        user_stats_string += self.get_if_present_string(user_stats, "best_running_distance")
        user_stats_string += self.get_if_present_string(user_stats, "best_running_date")

        user_stats_string += self.get_std_error_if_present_string(user_stats, "internal_ramp")
        user_stats_string += self.get_std_error_if_present_string(user_stats, "internal_monotony")
        user_stats_string += self.get_std_error_if_present_string(user_stats, "internal_strain")
        user_stats_string += self.get_std_error_if_present_string(user_stats, "internal_strain_events")
        user_stats_string += self.get_std_error_if_present_string(user_stats, "acute_internal_total_load")
        user_stats_string += self.get_std_error_if_present_string(user_stats, "chronic_internal_total_load")
        user_stats_string += self.get_std_error_if_present_string(user_stats, "internal_acwr")
        user_stats_string += self.get_std_error_if_present_string(user_stats, "internal_freshness_index")

        user_stats_string += self.get_std_error_if_present_string(user_stats, "power_load_ramp")
        user_stats_string += self.get_std_error_if_present_string(user_stats, "power_load_monotony")
        user_stats_string += self.get_std_error_if_present_string(user_stats, "power_load_strain")
        user_stats_string += self.get_std_error_if_present_string(user_stats, "power_load_strain_events")
        user_stats_string += self.get_std_error_if_present_string(user_stats, "acute_power_total_load")
        user_stats_string += self.get_std_error_if_present_string(user_stats, "chronic_power_total_load")
        user_stats_string += self.get_std_error_if_present_string(user_stats, "power_load_acwr")
        user_stats_string += self.get_std_error_if_present_string(user_stats, "power_load_freshness_index")

        user_stats_string += self.get_if_present_string(user_stats, "acute_days")
        user_stats_string += self.get_if_present_string(user_stats, "chronic_days")
        user_stats_string += self.get_if_present_string(user_stats, "total_historical_sessions")

        user_stats_string += self.get_std_error_if_present_string(user_stats, "average_weekly_internal_load")
        user_stats_string += self.get_std_error_if_present_string(user_stats, "average_weekly_power_load")
        user_stats_string += self.get_std_error_if_present_string(user_stats, "average_session_internal_load")
        user_stats_string += self.get_std_error_if_present_string(user_stats, "average_session_power_load")

        user_stats_string += str(user_stats.functional_overreaching_workout_today) + ","
        user_stats_string += str(user_stats.functional_overreaching_workout_1_day) + ","
        user_stats_string += str(user_stats.non_functional_overreaching_workout_today) + ","
        user_stats_string += str(user_stats.non_functional_overreaching_workout_1_day) + ","
        user_stats_string += str(user_stats.non_functional_overreaching_workout_2_day) + ","

        user_stats_string += self.get_training_unit_if_present_string(user_stats.athlete_capacities, "base_aerobic_training")
        user_stats_string += self.get_training_unit_if_present_string(user_stats.athlete_capacities,
                                                                 "anaerobic_threshold_training")
        user_stats_string += self.get_training_unit_if_present_string(user_stats.athlete_capacities,
                                                                 "high_intensity_anaerobic_training")
        user_stats_string += self.get_training_unit_if_present_string(user_stats.athlete_capacities, "muscular_endurance")
        user_stats_string += self.get_training_unit_if_present_string(user_stats.athlete_capacities, "strength_endurance")
        user_stats_string += self.get_training_unit_if_present_string(user_stats.athlete_capacities, "hypertrophy")
        user_stats_string += self.get_training_unit_if_present_string(user_stats.athlete_capacities, "maximal_strength")
        user_stats_string += self.get_training_unit_if_present_string(user_stats.athlete_capacities, "speed")
        user_stats_string += self.get_training_unit_if_present_string(user_stats.athlete_capacities, "sustained_power")
        user_stats_string += self.get_training_unit_if_present_string(user_stats.athlete_capacities, "power")
        user_stats_string += self.get_training_unit_if_present_string(user_stats.athlete_capacities, "maximal_power",
                                                                 is_last=True)

        return user_stats_string

    def get_plan_capacities_string(self, plan):

        plan_string = ""
        plan_string += self.get_training_unit_if_present_string(plan.athlete_capacities, "base_aerobic_training")
        plan_string += self.get_training_unit_if_present_string(plan.athlete_capacities, "anaerobic_threshold_training")
        plan_string += self.get_training_unit_if_present_string(plan.athlete_capacities, "high_intensity_anaerobic_training")
        plan_string += self.get_training_unit_if_present_string(plan.athlete_capacities, "muscular_endurance")
        plan_string += self.get_training_unit_if_present_string(plan.athlete_capacities, "strength_endurance")
        plan_string += self.get_training_unit_if_present_string(plan.athlete_capacities, "hypertrophy")
        plan_string += self.get_training_unit_if_present_string(plan.athlete_capacities, "maximal_strength")
        plan_string += self.get_training_unit_if_present_string(plan.athlete_capacities, "speed")
        plan_string += self.get_training_unit_if_present_string(plan.athlete_capacities, "sustained_power")
        plan_string += self.get_training_unit_if_present_string(plan.athlete_capacities, "power")
        plan_string += self.get_training_unit_if_present_string(plan.athlete_capacities, "maximal_power", is_last=True)

        return plan_string

    def get_training_exposure_string(self, session):

        training_string = ""
        exposure_count = 0
        for training_exposure in session.training_exposures:
            rpe = training_exposure.rpe.highest_value()
            if rpe is not None:
                rpe = round(rpe, 1)
            volume = training_exposure.volume.highest_value()
            if volume is not None:
                volume = round(volume, 2)
            rpe_load = training_exposure.rpe_load.highest_value()
            if rpe_load is not None:
                rpe_load = round(rpe_load, 2)
            training_string += f"{training_exposure.detailed_adaptation_type.name}; {rpe};{volume};{rpe_load};"
            # training_string += training_exposure.detailed_adaptation_type.name + "; " + str(
            #     training_exposure.rpe.highest_value()) + ";" + str(training_exposure.volume.highest_value()) + ";"
            exposure_count += 1
            if exposure_count < len(session.training_exposures):
                training_string += "||"

        return training_string

    def get_target_training_exposure_string(self, obj, is_athlete_target_training_exposure=False):

        training_string = ""

        target_training_exposure_count = 0
        for target_training_exposure in obj.target_training_exposures:
            if is_athlete_target_training_exposure:
                training_string += ("{progression_week:" + str(target_training_exposure.progression_week) +
                                    ";exposure_count:" + self.get_std_error_if_present_string(target_training_exposure,
                                                                                         "exposure_count",
                                                                                         is_last=True) + ";" + "priority:" + str(
                            target_training_exposure.priority) + ";")
            else:
                training_string += "{exposure_count:" + self.get_std_error_if_present_string(target_training_exposure,
                                                                                        "exposure_count",
                                                                                        is_last=True) + ";" + "priority:" + str(
                    target_training_exposure.priority) + ";"

            exposure_count = 0
            target_training_exposure_count += 1
            for training_exposure in target_training_exposure.training_exposures:
                training_string += training_exposure.detailed_adaptation_type.name + "; "
                if training_exposure.rpe is not None:
                    training_string += "RPE:" + str(training_exposure.rpe.highest_value()) + ";"
                else:
                    training_string += "RPE:None;"

                if training_exposure.volume is not None:
                    training_string += "VOL:" + str(training_exposure.volume.highest_value()) + ";"
                else:
                    training_string += "VOL:None;"
                exposure_count += 1
                if exposure_count < len(target_training_exposure.training_exposures):
                    training_string += "||"
            # if target_training_exposure_count < len(obj.target_training_exposures):
            training_string += "}"

        return training_string

    def get_session_string(self, session):
        # workout_header_line = (
        #     "event_date_time, id,description, distance, duration_minutes, power_load_highest, rpe_load_highest, training_volume, target_training_exposures")
        session_string = str(session.event_date) + "," + session.id + "," + session.description + "," + str(
            session.distance) + "," + str(session.duration_minutes) + ","
        session_string += str(session.session_RPE) + "," + str(session.power_load.highest_value()) + "," + str(
            session.rpe_load.highest_value()) + "," + str(session.training_volume) + "," + str(session.contains_high_intensity_blocks()) + ","
        session_string += self.get_training_exposure_string(session)

        return session_string

    def get_periodization_goals_string(self, plan):

        goal_string = ""
        goal_count = 0
        for periodization_goal in plan.periodization_goals:
            goal_string += periodization_goal.periodization_goal_type.name + ";Training Exposures= " + self.get_target_training_exposure_string(
                periodization_goal) + ";"
            goal_count += 1
            if goal_count < len(plan.periodization_goals):
                goal_string += "||"

        return goal_string

    def get_body_part_side_string(self, body_parts):

        body_part_string = ""

        for b in body_parts:
            if len(body_part_string) > 0:
                body_part_string += ";"
            body_part_string += b.body_part_location.name + ": side=" + str(b.side)

        return body_part_string

    def get_periodization_plan_string(self, plan, event_date, athlete_readiness):

        plan_string = str(plan.start_date) + "," + str(event_date) + ","
        plan_string += self.get_periodization_goals_string(plan) + ","
        plan_string += plan.training_phase_type.name + "," + plan.athlete_persona.name + ","
        plan_string += ("cardio_persona=" + plan.sub_adaptation_type_personas.cardio_persona.name + ";" +
                        "power_persona=" + plan.sub_adaptation_type_personas.power_persona.name + ";" +
                        "strength_persona=" + plan.sub_adaptation_type_personas.strength_persona.name) + ","
        plan_string += self.get_target_training_exposure_string(plan,
                                                           is_athlete_target_training_exposure=True) + "," + self.get_std_error_if_present_string(
            plan, "target_weekly_rpe_load", is_last=True) + ","
        plan_string += self.get_std_error_if_present_string(plan, "expected_weekly_workouts", is_last=True) + ","
        plan_string += str(athlete_readiness.readiness_score) + "," + str(athlete_readiness.load_score) + "," + str(
            athlete_readiness.rpe_score) + ","
        plan_string += str(athlete_readiness.inflammation_level) + "," + str(
            athlete_readiness.muscle_spasm_level) + "," + str(
            athlete_readiness.internal_load_acwr_ratio) + "," + str(athlete_readiness.power_load_acwr_ratio) + ","

        #"internal_strain_events, internal_acwr, power_load_strain_events, power_load_acwr, average_weekly_internal_load,"
        plan_string += self.get_std_error_if_present_string(athlete_readiness,"internal_strain_events") + str(athlete_readiness.internal_acwr) + ","
        plan_string += self.get_std_error_if_present_string(athlete_readiness, "power_load_strain_events") + str(athlete_readiness.power_load_acwr) + ","
        plan_string += self.get_std_error_if_present_string(athlete_readiness, "average_weekly_internal_load") # comma included in method

        plan_string += self.get_plan_capacities_string(plan) + ","
        plan_string += self.get_body_part_side_string(plan.acute_muscle_issues) + ","
        plan_string += self.get_body_part_side_string(plan.chronic_muscle_issues) + ","
        plan_string += self.get_body_part_side_string(plan.excessive_strain_muscles) + ","
        plan_string += self.get_body_part_side_string(plan.compensating_muscles) + ","
        plan_string += self.get_body_part_side_string(plan.functional_overreaching_muscles) + ","
        plan_string += self.get_body_part_side_string(plan.non_functional_overreaching_muscles) + ","
        plan_string += self.get_body_part_side_string(plan.tendon_issues)

        return plan_string

    def get_scoring_string(self, event_date, workout):

        scoring_string = str(event_date) + "," + str(workout.score) + "," + workout.program_module_id.replace(',',
                                                                                                              '_') + ","

        scoring_string += self.get_training_exposure_string(workout)
        # scoring_string += get_training_unit_if_present_string(workout.athlete_capacities, "base_aerobic_training")
        # scoring_string += get_training_unit_if_present_string(workout.athlete_capacities, "anaerobic_threshold_training")
        # scoring_string += get_training_unit_if_present_string(workout.athlete_capacities, "high_intensity_anaerobic_training")
        # scoring_string += get_training_unit_if_present_string(workout.athlete_capacities, "muscular_endurance")
        # scoring_string += get_training_unit_if_present_string(workout.athlete_capacities, "strength_endurance")
        # scoring_string += get_training_unit_if_present_string(workout.athlete_capacities, "hypertrophy")
        # scoring_string += get_training_unit_if_present_string(workout.athlete_capacities, "maximal_strength")
        # scoring_string += get_training_unit_if_present_string(workout.athlete_capacities, "speed")
        # scoring_string += get_training_unit_if_present_string(workout.athlete_capacities, "sustained_power")
        # scoring_string += get_training_unit_if_present_string(workout.athlete_capacities, "power")
        # scoring_string += get_training_unit_if_present_string(workout.athlete_capacities, "maximal_power", is_last=True)

        return scoring_string


class UpdatedSpreadsheets(object):
    def __init__(self, persona, start_date=None):
        self.persona = persona
        self.start_date = start_date
        self.table1_periodization_plan = []
        self.table2_workouts = []
        self.table1_row = None
        self.table2_row = None
        self.demo_output = DemoOutput()
        self.session_today = True


    def initialize_table1_row(self, date):
        self.table1_row = self.get_blank_table1_row()
        self.table1_row['current_date'] = date
        self.table1_periodization_plan.append(self.table1_row)

    def initialize_table2_row(self, date=None):
        self.table2_row = self.get_blank_table2_row()
        self.table2_row['event_date_time'] = date
        self.table2_workouts.append(self.table2_row)

    def update_daily_rows(self, periodization_plan_before=None, periodization_plan_after=None,
                          user_stats_before=None, user_stats_after=None,
                          session=None,
                          recovery_string=None,
                          readiness_before=None, readiness_after=None
                          ):
        if recovery_string is not None:
            self.update_table1_with_recovery(self.table1_row, recovery_string)
        if periodization_plan_before is not None:
            self.update_table1_with_periodization_plan_before(self.table1_row, periodization_plan_before)
        if periodization_plan_after is not None:
            self.update_table1_with_periodization_plan_after(self.table1_row, periodization_plan_after)
        if user_stats_before is not None:
            self.update_table1_with_user_stats_before(self.table1_row, user_stats_before)
            if not self.session_today:
                self.update_table2_with_user_stats(self.table2_row, user_stats_before)
        if user_stats_after is not None:
            self.update_table1_with_user_stats_after(self.table1_row, user_stats_after)
            self.update_table2_with_user_stats(self.table2_row, user_stats_after)
        if session is not None:
            self.update_table1_with_session(self.table1_row, session)
            self.update_table2_with_session(self.table2_row, session)
        if readiness_before is not None:
            self.update_table1_with_athlete_readiness_before(self.table1_row, readiness_before)
        if readiness_after is not None:
            self.update_table1_with_athlete_readiness_after(self.table1_row, readiness_after)


    @staticmethod
    def get_blank_table1_row():
        blank_row = {
            "current_date": None,
            # from athlete_readiness after overnight process
            "readiness_score": None,
            "load_score": None,
            "rpe_score": None,
            "internal_load_acwr_ratio": None,
            "power_load_acwr_ratio": None,
            "internal_acwr": None,
            "power_load_acwr": None,

            # from athlete_readiness after session
            "after_readiness_score": None,
            "after_load_score": None,
            "after_rpe_score": None,
            "after_internal_load_acwr_ratio": None,
            "after_power_load_acwr_ratio": None,
            "after_internal_acwr": None,
            "after_power_load_acwr": None,

            # from periodization plan sheet after overnight process
            "acute_muscle_issues": None,
            "chronic_muscle_issues": None,
            "excessive_strain_muscles": None,
            "compensating_muscles": None,
            "functional_overreaching_muscles": None,
            "non_functional_overreaching_muscles": None,
            "tendon_issues": None,

            "inflammation_level": None,
            "muscle_spasm_level": None,
            "internal_strain_events": None,
            "power_load_strain_events": None,

            # from periodization plan sheet after session
            "after_acute_muscle_issues": None,
            "after_chronic_muscle_issues": None,
            "after_excessive_strain_muscles": None,
            "after_compensating_muscles": None,
            "after_functional_overreaching_muscles": None,
            "after_non_functional_overreaching_muscles": None,
            "after_tendon_issues": None,

            # from workout (if present)
            "high_intensity_session": None,

            # from user_stats
            "fo_workout_today": None,
            "fo_workout_1_day": None,
            "nfo_workout_today": None,
            "nfo_workout_1_day": None,
            "nfo_workout_2_day": None,
            "average_weekly_internal_load": None,

            "symptoms": None,
            "CWI": None,
            "Active Recovery": None,
            "Mobility WOD": None,
            "Active Rest": None,
            "Ice": None,
        }
        return blank_row

    @staticmethod
    def get_output_columns_table1():
        return [
        'current_date',
        'readiness_score',
        'after_readiness_score',
        'load_score',
        'rpe_score',
        'after_load_score',
        'after_rpe_score',
        'CWI',
        'Active Recovery',
        'Mobility WOD',
        'Active Rest',
        'Ice',
        'internal_load_acwr_ratio',
        'power_load_acwr_ratio',
        'internal_acwr',
        'power_load_acwr',
        'high_intensity_session',
        'fo_workout_today',
        'fo_workout_1_day',
        'nfo_workout_today',
        'nfo_workout_1_day',
        'nfo_workout_2_day',
        'after_internal_load_acwr_ratio',
        'after_power_load_acwr_ratio',
        'after_internal_acwr',
        'after_power_load_acwr',
        'average_weekly_internal_load',
        'symptoms',
        'inflammation_level',
        'muscle_spasm_level',
        'internal_strain_events',
        'power_load_strain_events',
        'acute_muscle_issues',
        'chronic_muscle_issues',
        'excessive_strain_muscles',
        'compensating_muscles',
        'functional_overreaching_muscles',
        'non_functional_overreaching_muscles',
        'tendon_issues',
        'after_acute_muscle_issues',
        'after_chronic_muscle_issues',
        'after_excessive_strain_muscles',
        'after_compensating_muscles',
        'after_functional_overreaching_muscles',
        'after_non_functional_overreaching_muscles',
        'after_tendon_issues'
        ]

    @staticmethod
    def get_blank_table2_row():
        return {
            "event_date_time": None,
            "Workout": None,
            "Library": None,
            "distance": None,
            "duration_minutes": None,
            "session_rpe": None,
            "power_load_highest": None,
            "scaled_power_load_highest": None,
            "rpe_load_highest": None,
            "training_volume": None,
            "high_intensity_session": None,
            "fo_workout_today": None,
            "fo_workout_1_day": None,
            "nfo_workout_today": None,
            "nfo_workout_1_day": None,
            "nfo_workout_2_day": None,
            "load_remaining": None,
            "rpe_base_aerobic_training": None,
            "volume_base_aerobic_training": None,
            "load_base_aerobic_training": None,
            "rpe_anaerobic_threshold_training": None,
            "volume_anaerobic_threshold_training": None,
            "load_anaerobic_threshold_training": None,
            "rpe_high_intensity_anaerobic_training": None,
            "volume_high_intensity_anaerobic_training": None,
            "load_high_intensity_anaerobic_training": None,
            "rpe_strength_endurance": None,
            "volume_strength_endurance": None,
            "load_strength_endurance": None,
            "rpe_speed": None,
            "volume_speed": None,
            "load_speed": None,
            "rpe_power": None,
            "volume_power": None,
            "load_power": None,
            "rpe_maximal_power": None,
            "volume_maximal_power": None,
            "load_maximal_power": None,
            "rpe_sustained_power": None,
            "volume_sustained_power": None,
            "load_sustained_power": None,
            "rpe_muscular_endurance": None,
            "volume_muscular_endurance": None,
            "load_muscular_endurance": None,
            "target_training_exposures": None
        }

    @staticmethod
    def get_output_columns_table2():
        return []

    @staticmethod
    def get_recovery_from_string(recovery_string):
        components = recovery_string.split(',')
        symptoms = components[1]
        recovery = {"symptoms": symptoms,
                    "CWI": False,
                    "Active Recovery": False,
                    "Mobility WOD": False,
                    "Active Rest": False,
                    "Ice": False}
        if "Mobility WOD: Active" in components[2]:
            recovery["Mobility WOD"] = True
        if components[2] == "Active Rest":
            recovery["Active Rest"] = True
        if "Active Recovery" in components[2]:
            recovery["Active Recovery"] = True
        if "Ice" in components[6]:
            recovery["Ice"] = True
        if "COLD WATER IMMERSION" in components[6]:
            recovery["CWI"] = True
        return recovery

    def update_table1_with_recovery(self, daily_row, recovery_string):
        recovery = self.get_recovery_from_string(recovery_string)
        for key, value in recovery.items():
            daily_row[key] = value

    def update_table1_with_athlete_readiness_before(self, daily_row, athlete_readiness):
        daily_row['readiness_score'] = int(athlete_readiness.readiness_score) if athlete_readiness.readiness_score is not None else None
        daily_row['load_score'] = int(athlete_readiness.load_score) if athlete_readiness.load_score is not None else None
        daily_row['rpe_score'] = int(athlete_readiness.rpe_score) if athlete_readiness.rpe_score is not None else None
        daily_row['internal_load_acwr_ratio'] = round(athlete_readiness.internal_load_acwr_ratio, 2) if athlete_readiness.internal_load_acwr_ratio is not None else None
        daily_row['power_load_acwr_ratio'] = round(athlete_readiness.power_load_acwr_ratio, 2) if athlete_readiness.power_load_acwr_ratio is not None else None
        daily_row['internal_acwr'] = round(athlete_readiness.internal_acwr, 2) if athlete_readiness.internal_acwr is not None else None
        daily_row['power_load_acwr'] = round(athlete_readiness.power_load_acwr, 2) if athlete_readiness.power_load_acwr is not None else None
        if athlete_readiness.average_weekly_internal_load is not None and athlete_readiness.average_weekly_internal_load.highest_value() is not None:
            daily_row['average_weekly_internal_load'] = int(athlete_readiness.average_weekly_internal_load.highest_value())

    @staticmethod
    def update_table1_with_athlete_readiness_after(daily_row, athlete_readiness):
        daily_row['after_readiness_score'] = int(athlete_readiness.readiness_score) if athlete_readiness.readiness_score is not None else None
        daily_row['after_load_score'] = int(athlete_readiness.load_score) if athlete_readiness.load_score is not None else None
        daily_row['after_rpe_score'] = int(athlete_readiness.rpe_score) if athlete_readiness.rpe_score is not None else None
        daily_row['after_internal_load_acwr_ratio'] = round(athlete_readiness.internal_load_acwr_ratio, 2) if athlete_readiness.internal_load_acwr_ratio is not None else None
        daily_row['after_power_load_acwr_ratio'] = round(athlete_readiness.power_load_acwr_ratio, 2) if athlete_readiness.power_load_acwr_ratio is not None else None
        daily_row['after_internal_acwr'] = round(athlete_readiness.internal_acwr, 2) if athlete_readiness.internal_acwr is not None else None
        daily_row['after_power_load_acwr'] = round(athlete_readiness.power_load_acwr, 2) if athlete_readiness.power_load_acwr is not None else None

    def update_table1_with_periodization_plan_before(self, daily_row, periodization_plan_before):

        daily_row['acute_muscle_issues'] = self.demo_output.get_body_part_side_string(periodization_plan_before.acute_muscle_issues)
        daily_row['chronic_muscle_issues'] = self.demo_output.get_body_part_side_string(periodization_plan_before.chronic_muscle_issues)
        daily_row['excessive_strain_muscles'] = self.demo_output.get_body_part_side_string(periodization_plan_before.excessive_strain_muscles)
        daily_row['compensating_muscles'] = self.demo_output.get_body_part_side_string(periodization_plan_before.compensating_muscles)
        daily_row['functional_overreaching_muscles'] = self.demo_output.get_body_part_side_string(periodization_plan_before.functional_overreaching_muscles)
        daily_row['non_functional_overreaching_muscles'] = self.demo_output.get_body_part_side_string(periodization_plan_before.non_functional_overreaching_muscles)
        daily_row['tendon_issues'] = self.demo_output.get_body_part_side_string(periodization_plan_before.tendon_issues)

    def update_table1_with_periodization_plan_after(self, daily_row, periodization_plan_after):

        daily_row['after_acute_muscle_issues'] = self.demo_output.get_body_part_side_string(periodization_plan_after.acute_muscle_issues)
        daily_row['after_chronic_muscle_issues'] = self.demo_output.get_body_part_side_string(periodization_plan_after.chronic_muscle_issues)
        daily_row['after_excessive_strain_muscles'] = self.demo_output.get_body_part_side_string(periodization_plan_after.excessive_strain_muscles)
        daily_row['after_compensating_muscles'] = self.demo_output.get_body_part_side_string(periodization_plan_after.compensating_muscles)
        daily_row['after_functional_overreaching_muscles'] = self.demo_output.get_body_part_side_string(periodization_plan_after.functional_overreaching_muscles)
        daily_row['after_non_functional_overreaching_muscles'] = self.demo_output.get_body_part_side_string(periodization_plan_after.non_functional_overreaching_muscles)
        daily_row['after_tendon_issues'] = self.demo_output.get_body_part_side_string(periodization_plan_after.tendon_issues)

    def update_table1_with_user_stats_before(self, daily_row, user_stats_before):
        pass
        # daily_row['fo_workoout_today'] = str(user_stats_before.functional_overreaching_workout_today)
        # daily_row['fo_workout_1_day'] = str(user_stats_before.functional_overreaching_workout_1_day)
        # daily_row['nfo_workout_today'] = str(user_stats_before.non_functional_overreaching_workout_today)
        # daily_row['nfo_workout_1_day'] = str(user_stats_before.non_functional_overreaching_workout_1_day)
        # daily_row['nfo_workout_2_day'] = str(user_stats_before.non_functional_overreaching_workout_2_day)

    def update_table1_with_user_stats_after(self, daily_row, user_stats_after):
        daily_row['fo_workout_today'] = str(user_stats_after.functional_overreaching_workout_today)
        daily_row['fo_workout_1_day'] = str(user_stats_after.functional_overreaching_workout_1_day)
        daily_row['nfo_workout_today'] = str(user_stats_after.non_functional_overreaching_workout_today)
        daily_row['nfo_workout_1_day'] = str(user_stats_after.non_functional_overreaching_workout_1_day)
        daily_row['nfo_workout_2_day'] = str(user_stats_after.non_functional_overreaching_workout_2_day)

    @staticmethod
    def update_table1_with_session(daily_row, session):
        if daily_row['high_intensity_session'] is not None and not daily_row['high_intensity_session']:
            daily_row['high_intensity_session'] = session.contains_high_intensity_blocks()

    def update_table2_with_session(self, session_row, session):
        session_row['Workout'] = session.description
        session_row['distance'] = int(session.distance) if session.distance is not None else None
        session_row['distance'] = round(session.distance / 100, 1) if session.distance is not None else None
        session_row['duration_minutes'] = int(session.duration_minutes)
        session_row['session_rpe'] = round(session.session_RPE, 1)
        session_row['power_load_highest'] = int(session.power_load.highest_value()) if session.power_load.highest_value() is not None else None
        session_row['scaled_power_load_highest'] = int(session.power_load.highest_value() / 50) if session.power_load.highest_value() is not None else None
        session_row['rpe_load_highest'] = int(session.rpe_load.highest_value()) if session.rpe_load.highest_value() is not None else None
        session_row['training_volume'] = int(session.training_volume) if session.training_volume is not None else None
        session_row['high_intensity_session'] = session.contains_high_intensity_blocks()
        for exposure in session.training_exposures:
            adaptation_type = exposure.detailed_adaptation_type.name
            rpe = exposure.rpe.highest_value()
            if rpe is not None:
                rpe = round(rpe, 1)
            volume = exposure.volume.highest_value()
            if volume is not None:
                volume = round(volume, 2)
            rpe_load = exposure.rpe_load.highest_value()
            if rpe_load is not None:
                rpe_load = round(rpe_load, 2)
            session_row[f"rpe_{adaptation_type}"] = rpe
            session_row[f"volume_{adaptation_type}"] = volume
            session_row[f"load_{adaptation_type}"] = rpe_load

    @staticmethod
    def update_table2_with_user_stats(session_row, user_stats_after):
        session_row['fo_workout_today'] = str(user_stats_after.functional_overreaching_workout_today)
        session_row['fo_workout_1_day'] = str(user_stats_after.functional_overreaching_workout_1_day)
        session_row['nfo_workout_today'] = str(user_stats_after.non_functional_overreaching_workout_today)
        session_row['nfo_workout_1_day'] = str(user_stats_after.non_functional_overreaching_workout_1_day)
        session_row['nfo_workout_2_day'] = str(user_stats_after.non_functional_overreaching_workout_2_day)

    def write_to_csv(self):
        table1_pd = pd.DataFrame(self.table1_periodization_plan)
        if self.start_date is not None:
            table1_pd = table1_pd[table1_pd['current_date'] >= self.start_date]
        table1_pd.to_csv(f'output/periodization_plan_{self.persona}_v2.csv', index=False, columns=self.get_output_columns_table1())
        table2_pd = pd.DataFrame(self.table2_workouts)
        if self.start_date is not None:
            table2_pd = table2_pd[table2_pd['event_date_time'] >= self.start_date]
        table2_pd.to_csv(f'output/workouts_{self.persona}_v2.csv', index=False)  #, columns=self.get_output_columns_table2())
