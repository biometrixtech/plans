class DemoOutput(object):
    def __init__(self):
        self.user_stats_header_line = ("date, high_relative_load_sessions, high_relative_load_score, eligible_for_high_load_trigger," +
                                       "expected_weekly_workouts, vo2_max, vo2_max_date_time, best_running_time, best_running_distance, best_running_date," +
                                       "internal_ramp, internal_monotony, internal_strain, internal_strain_events, " +
                                       "acute_internal_total_load, chronic_internal_total_load, internal_acwr, internal_freshness_index," +
                                       "power_load_ramp, power_load_monotony, power_load_strain, power_load_strain_events, " +
                                       "acute_total_power_load, chronic_total_power_load, power_load_acwr, power_load_freshness_index," +
                                       "acute_days, chronic_days, total_historical_sessions, average_weekly_internal_load," +
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
            phase_exercise_string = ""
            for exercise_phase in active_rest.exercise_phases:
                if len(phase_exercise_string) > 0:
                    phase_exercise_string += "; "
                phase_exercise_string += str(exercise_phase.name).upper() + ":"
                exercise_string = ""
                if len(exercise_phase.exercises) > 0:
                    for exercise_id, assigned_exercise in exercise_phase.exercises.items():
                        if len(exercise_string) > 0:
                            exercise_string += ";"
                        exercise_string += exercise_id
                else:
                    exercise_string = " None"
                phase_exercise_string += exercise_string
            phase_string += phase_exercise_string
            worked = 0
        else:
            oops = 0

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
            phase_exercise_string = ""
            for exercise_phase in movement_prep.movement_integration_prep.exercise_phases:
                if len(phase_exercise_string) > 0:
                    phase_exercise_string += "; "
                phase_exercise_string += str(exercise_phase.name).upper() + ":"
                exercise_string = ""
                if len(exercise_phase.exercises) > 0:
                    for exercise_id, assigned_exercise in exercise_phase.exercises.items():
                        if len(exercise_string) > 0:
                            exercise_string += ";"
                        exercise_string += exercise_id
                else:
                    exercise_string = " None"
                phase_exercise_string += exercise_string
            phase_string += phase_exercise_string
            worked = 0
        else:
            oops = 0

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
            phase_exercise_string = ""
            for exercise_phase in active_rest.exercise_phases:
                if len(phase_exercise_string) > 0:
                    phase_exercise_string += "; "
                phase_exercise_string += str(exercise_phase.name).upper() + ":"
                exercise_string = ""
                if len(exercise_phase.exercises) > 0:
                    for exercise_id, assigned_exercise in exercise_phase.exercises.items():
                        if len(exercise_string) > 0:
                            exercise_string += ";"
                        exercise_string += exercise_id
                else:
                    exercise_string = " None"
                phase_exercise_string += exercise_string
            phase_string += phase_exercise_string
        elif active_recovery is not None:
            phase_string += "Active Recovery,"
            phase_exercise_string = ""
            for exercise_phase in active_recovery.exercise_phases:
                if len(phase_exercise_string) > 0:
                    phase_exercise_string += "; "
                phase_exercise_string += str(exercise_phase.name).upper() + ":"
                exercise_string = ""
                if len(exercise_phase.exercises) > 0:
                    for exercise_id, assigned_exercise in exercise_phase.exercises.items():
                        if len(exercise_string) > 0:
                            exercise_string += ";"
                        exercise_string += exercise_id
                else:
                    exercise_string = " None"
                phase_exercise_string += exercise_string
            phase_string += phase_exercise_string
        else:
            phase_string += ","

        if ice is not None:
            phase_string += "; Ice:"
            for body_part in ice.body_parts:
                phase_string += body_part.body_part_location.name + "; side=" + str(body_part.side) + ";"
        if cwi is not None:
            phase_string += "; **COLD WATER IMMERSION**"

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
            training_string += training_exposure.detailed_adaptation_type.name + "; " + str(
                training_exposure.rpe.highest_value()) + ";" + str(training_exposure.volume.highest_value()) + ";"
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
