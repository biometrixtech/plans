from models.modalities import ActiveRestBeforeTraining, ActiveRestAfterTraining
from models.soreness import Soreness
from models.soreness_base import HistoricSorenessStatus, BodyPartLocation
from utils import parse_date


class TestUtilities(object):

    def get_post_survey(self, RPE, soreness_list):

        survey = {
            "RPE" : RPE,
            "soreness": soreness_list
        }

        return survey


    def body_part_soreness(self, location_enum, severity, side=0, movement=None):

        if movement is None:
            soreness = {
                "body_part": location_enum,
                "side" : side,
                "severity": severity
            }
        else:

            soreness = {
                "body_part": location_enum,
                "side": side,
                "severity": severity,
                "movement": movement
            }

        return soreness

    def body_part_symptoms(self, location_enum, side=0, tight=None, knots=None, ache=None, sharp=None):

        soreness = {
            "body_part": location_enum,
            "side" : side,
            "tight": tight,
            "knots": knots,
            "ache": ache,
            "sharp": sharp
        }

        return soreness


    def body_part_pain(self, location_enum, severity, side=0, movement=None):

        if movement is None:
            soreness = {
                "body_part": location_enum,
                "severity": severity,
                "side": side,
                "pain": True
            }
        else:
            soreness = {
                "body_part": location_enum,
                "severity": severity,
                "movement": movement,
                "side": side,
                "pain": True
            }

        return soreness

    def body_part_location(self, location_enum):
        location = BodyPartLocation(location_enum)

        return location

    def body_part(self, body_enum, severity_score, movement=None):
        soreness_item = Soreness()
        soreness_item.severity = severity_score
        soreness_item.movement = movement
        soreness_item.body_part = BodyPartLocation(body_enum)
        return soreness_item


def is_status_pain(historic_soreness_status):

    if historic_soreness_status is None:
        return False
    elif (historic_soreness_status == HistoricSorenessStatus.almost_acute_pain or
            historic_soreness_status == HistoricSorenessStatus.acute_pain or
            historic_soreness_status == HistoricSorenessStatus.almost_persistent_pain or
            historic_soreness_status == HistoricSorenessStatus.persistent_pain or
            historic_soreness_status == HistoricSorenessStatus.almost_persistent_2_pain or
            historic_soreness_status == HistoricSorenessStatus.persistent_2_pain):
        return True
    else:
        return False


def convert_assigned_exercises(assigned_exercises):

    exercise_list = []

    for a in assigned_exercises:
        exercise_list.append(a.exercise.id)

    return exercise_list


def convert_assigned_dict_exercises(assigned_exercises):

    exercise_list = []

    for key, assigned_exercise in assigned_exercises.items():
        exercise_list.append(str(key))

    return exercise_list


def get_goals_triggers(assigned_exercises):

    goal_trigger_list = []

    for key, assigned_exercise in assigned_exercises.items():
        for d in assigned_exercises[key].dosages:
            #if d.goal.trigger_type is not None:
            if d.soreness_source is not None:
                goals = 'Goal=' + d.goal.text.replace(',','-') + '-->' + str(d.soreness_source.trigger_type.value).replace(',',';') + ' Priority=' + d.priority + ' Dosages='
            else:
                goals = 'Goal=' + d.goal.text.replace(',', '-') +  ' Priority=' + d.priority + ' Dosages='
            goals += "Eff Reps="+ str(d.efficient_reps_assigned) + ' & Eff Sets=' + str(d.efficient_sets_assigned)
            goals += " & Complete Reps=" + str(d.complete_reps_assigned) + ' & Complete Sets=' + str(
                d.complete_sets_assigned)
            goals += " & Compr Reps=" + str(d.comprehensive_reps_assigned) + ' & Compr Sets=' + str(
                d.comprehensive_sets_assigned)
            goal_trigger_list.append(goals)

    unique_list = set(goal_trigger_list)

    return unique_list


def calc_active_time_efficient(exercise_dictionary):

    active_time = 0

    for id, assigned_excercise in exercise_dictionary.items():
        active_time += assigned_excercise.duration_efficient() / 60

    return active_time


def calc_active_time_complete(exercise_dictionary):

    active_time = 0

    for id, assigned_excercise in exercise_dictionary.items():
        active_time += assigned_excercise.duration_complete() / 60

    return active_time


def calc_active_time_comprehensive(exercise_dictionary):

    active_time = 0

    for id, assigned_excercise in exercise_dictionary.items():
        active_time += assigned_excercise.duration_comprehensive() / 60

    return active_time


def get_insights_string(insights):

    output = ""

    j = 0

    for i in insights:
        if j > 0:
            output += ';'
        output += "trigger="+str(i.trigger_type.value)+"-"
        output += "goals=" + '**'.join(i.goal_targeted)
        if len(i.sport_names) > 0:
            output += "-sport=" + '**'.join(str(s) for s in i.sport_names)
        j += 1

    return output


def convert_alerts_to_easy_list(alerts):

    alert_list = list(str(a.trigger_type.value) for a in alerts)

    return alert_list


def get_alerts_ctas_goals_string(daily_plan):

    output = ""

    # output += ";".join(convert_alerts_to_easy_list(daily_plan.trends.biomechanics.alerts)) + ","
    # output += ";".join(daily_plan.trends.biomechanics.goals) + ","
    # output += ";".join(convert_alerts_to_easy_list(daily_plan.trends.response.alerts)) + ","
    # output += ";".join(daily_plan.trends.response.goals) + ","
    # output += ";".join(convert_alerts_to_easy_list(daily_plan.trends.stress.alerts)) + ","
    # output += ";".join(daily_plan.trends.stress.goals)
    output += ",,,,,"

    return output


def get_summary_string(daily_plan):

    line = ""

    if daily_plan.heat is not None:
        line = line + "Yes,"
    else:
        line = line + "No,"
    if len(daily_plan.pre_active_rest) > 0 and len(daily_plan.pre_active_rest[0].inhibit_exercises) > 0:
        line = line + "Yes,"
    else:
        line = line + "No,"
    if len(daily_plan.post_active_rest) > 0 and len(daily_plan.post_active_rest[0].inhibit_exercises) > 0:
        line = line + "Yes,"
    else:
        line = line + "No,"
    if len(daily_plan.cool_down) > 0:
        line = line + "Yes,"
    else:
        line = line + "No,"
    if daily_plan.ice is not None:
        line = line + "Yes,"
    else:
        line = line + "No,"
    if daily_plan.cold_water_immersion is not None:
        line = line + "Yes"
    else:
        line = line + "No"

    return line


def get_body_part_location_string(body_part_list):

    output = ""

    times = 0
    for b in body_part_list:
        if times > 0:
            output += ';'
        output += str(BodyPartLocation(b))
        times += 1

    return output


def get_priority_counts_for_collection(collection):

    priority_1_count = 0
    priority_2_count = 0
    priority_3_count = 0

    for e, d in collection.items():
        if d.dosages[0].priority == "1":
            priority_1_count += 1
        elif d.dosages[0].priority == "2":
            priority_2_count += 1
        elif d.dosages[0].priority == "3":
            priority_3_count += 1

    return priority_1_count, priority_2_count, priority_3_count


def get_priority_counts_for_dosages(daily_plan):

    priority_1_count = 0
    priority_2_count = 0
    priority_3_count = 0

    if daily_plan.pre_active_rest is not None and len(daily_plan.pre_active_rest) > 0:
        priority_1_count_new, priority_2_count_new, priority_3_count_new = get_priority_counts_for_collection(
            daily_plan.pre_active_rest[0].inhibit_exercises)
        priority_1_count += priority_1_count_new
        priority_2_count += priority_2_count_new
        priority_3_count += priority_3_count_new

        priority_1_count_new, priority_2_count_new, priority_3_count_new = get_priority_counts_for_collection(
            daily_plan.pre_active_rest[0].static_stretch_exercises)
        priority_1_count += priority_1_count_new
        priority_2_count += priority_2_count_new
        priority_3_count += priority_3_count_new

        priority_1_count_new, priority_2_count_new, priority_3_count_new = get_priority_counts_for_collection(
            daily_plan.pre_active_rest[0].active_stretch_exercises)
        priority_1_count += priority_1_count_new
        priority_2_count += priority_2_count_new
        priority_3_count += priority_3_count_new

        priority_1_count_new, priority_2_count_new, priority_3_count_new = get_priority_counts_for_collection(
            daily_plan.pre_active_rest[0].isolated_activate_exercises)
        priority_1_count += priority_1_count_new
        priority_2_count += priority_2_count_new
        priority_3_count += priority_3_count_new

        priority_1_count_new, priority_2_count_new, priority_3_count_new = get_priority_counts_for_collection(
            daily_plan.pre_active_rest[0].static_integrate_exercises)
        priority_1_count += priority_1_count_new
        priority_2_count += priority_2_count_new
        priority_3_count += priority_3_count_new

    if daily_plan.post_active_rest is not None and len(daily_plan.post_active_rest) > 0:
        priority_1_count_new, priority_2_count_new, priority_3_count_new = get_priority_counts_for_collection(
            daily_plan.post_active_rest[0].inhibit_exercises)
        priority_1_count += priority_1_count_new
        priority_2_count += priority_2_count_new
        priority_3_count += priority_3_count_new

        priority_1_count_new, priority_2_count_new, priority_3_count_new = get_priority_counts_for_collection(
            daily_plan.post_active_rest[0].static_stretch_exercises)
        priority_1_count += priority_1_count_new
        priority_2_count += priority_2_count_new
        priority_3_count += priority_3_count_new

        priority_1_count_new, priority_2_count_new, priority_3_count_new = get_priority_counts_for_collection(
            daily_plan.post_active_rest[0].isolated_activate_exercises)
        priority_1_count += priority_1_count_new
        priority_2_count += priority_2_count_new
        priority_3_count += priority_3_count_new

        priority_1_count_new, priority_2_count_new, priority_3_count_new = get_priority_counts_for_collection(
            daily_plan.post_active_rest[0].static_integrate_exercises)
        priority_1_count += priority_1_count_new
        priority_2_count += priority_2_count_new
        priority_3_count += priority_3_count_new

    priority_string = str(priority_1_count) + "," + str(priority_2_count) + "," + str(priority_3_count)

    return priority_string


def is_historic_soreness_pain(historic_soreness_status):

    if historic_soreness_status in[HistoricSorenessStatus.acute_pain,HistoricSorenessStatus.persistent_pain,
                                   HistoricSorenessStatus.persistent_2_pain,HistoricSorenessStatus.almost_persistent_pain,
                                   HistoricSorenessStatus.almost_persistent_2_pain_acute,
                                   HistoricSorenessStatus.almost_persistent_2_pain,
                                   HistoricSorenessStatus.almost_acute_pain]:
        return True
    else:
        return False


def get_cool_down_line(daily_plan):

    cool_down_line = ""

    if len(daily_plan.cool_down) > 0:
        cool_down = daily_plan.cool_down[0]
        cool_down_line += cool_down.default_plan + ','
        alert_text = ''
        for a in cool_down.alerts:
            alert_text += "trigger=" + str(a.goal.trigger_type.value) + '--'
            alert_text += str(a.sport_name) + ';'
        cool_down_line += alert_text + ','
        stretch_line = ""
        for s, ex in cool_down.dynamic_stretch_exercises.items():
            stretch_line += str(s) + ';'

        cool_down_line += stretch_line + ','
        integrate_line = ""
        for i, ex in cool_down.dynamic_integrate_exercises.items():
            integrate_line += str(i) + ';'

        cool_down_line += integrate_line + ','

        stretch_time_efficient = calc_active_time_efficient(cool_down.dynamic_stretch_exercises)
        stretch_time_complete = calc_active_time_complete(cool_down.dynamic_stretch_exercises)
        stretch_time_comprehensive = calc_active_time_comprehensive(cool_down.dynamic_stretch_exercises)

        integrate_time_efficient = calc_active_time_efficient(cool_down.dynamic_integrate_exercises)
        integrate_time_complete = calc_active_time_complete(cool_down.dynamic_integrate_exercises)
        integrate_time_comprehensive = calc_active_time_comprehensive(cool_down.dynamic_integrate_exercises)

        time_line = str(round(stretch_time_efficient, 2)) + ',' + str(round(stretch_time_complete, 2)) + ',' + str(round(stretch_time_comprehensive, 2)) + ',' + str(round(integrate_time_efficient, 2)) + ',' + str(round(integrate_time_complete, 2)) + ',' + str(round(integrate_time_comprehensive, 2))

        cool_down_line += time_line

    return cool_down_line


def get_lines(daily_plan):

    insights_string = get_insights_string(daily_plan.insights)
    alert_cta_goal_line = get_alerts_ctas_goals_string(daily_plan)
    cool_down_line = get_cool_down_line(daily_plan)
    if daily_plan.train_later:
        if len(daily_plan.pre_active_rest) == 0:
            active_rest = ActiveRestBeforeTraining(parse_date(daily_plan.event_date), False)
            daily_plan.pre_active_rest.append(active_rest)

        plan_obj = daily_plan.pre_active_rest[0]
        active_stretch_goals_triggers = get_goals_triggers(plan_obj.active_stretch_exercises)
        efficient_active_stretch_minutes = calc_active_time_efficient(
            plan_obj.active_stretch_exercises)
        complete_active_stretch_minutes = calc_active_time_complete(plan_obj.active_stretch_exercises)
        comprehensive_active_stretch_minutes = calc_active_time_comprehensive(
            plan_obj.active_stretch_exercises)
    else:
        if len(daily_plan.post_active_rest) == 0:
            active_rest = ActiveRestAfterTraining(parse_date(daily_plan.event_date), False)
            daily_plan.post_active_rest.append(active_rest)
        plan_obj = daily_plan.post_active_rest[0]
        plan_obj.active_stretch_exercises = {}
        active_stretch_goals_triggers = ''
        efficient_active_stretch_minutes = 0
        complete_active_stretch_minutes = 0
        comprehensive_active_stretch_minutes = 0

    body_part_line = plan_obj.default_plan
    inhibit_goals_triggers = get_goals_triggers(plan_obj.inhibit_exercises)
    static_stretch_goals_triggers = get_goals_triggers(plan_obj.static_stretch_exercises)
    isolated_activate_goals_triggers = get_goals_triggers(plan_obj.isolated_activate_exercises)
    static_integrate_goals_triggers = get_goals_triggers(plan_obj.static_integrate_exercises)

    efficient_inhibit_minutes = calc_active_time_efficient(plan_obj.inhibit_exercises)
    efficient_static_stretch_minutes = calc_active_time_efficient(
        plan_obj.static_stretch_exercises)

    efficient_isolated_activate_minutes = calc_active_time_efficient(
        plan_obj.isolated_activate_exercises)
    efficient_static_integrate_minutes = calc_active_time_efficient(
        plan_obj.static_integrate_exercises)
    efficient_total_minutes = efficient_inhibit_minutes + efficient_static_stretch_minutes + efficient_active_stretch_minutes + efficient_isolated_activate_minutes + efficient_static_integrate_minutes
    complete_inhibit_minutes = calc_active_time_complete(plan_obj.inhibit_exercises)
    complete_static_stretch_minutes = calc_active_time_complete(plan_obj.static_stretch_exercises)

    complete_isolated_activate_minutes = calc_active_time_complete(plan_obj.isolated_activate_exercises)
    complete_static_integrate_minutes = calc_active_time_complete(plan_obj.static_integrate_exercises)
    complete_total_minutes = complete_inhibit_minutes + complete_static_stretch_minutes + complete_active_stretch_minutes + complete_isolated_activate_minutes + complete_static_integrate_minutes
    comprehensive_inhibit_minutes = calc_active_time_comprehensive(plan_obj.inhibit_exercises)
    comprehensive_static_stretch_minutes = calc_active_time_comprehensive(
        plan_obj.static_stretch_exercises)

    comprehensive_isolated_activate_minutes = calc_active_time_comprehensive(
        plan_obj.isolated_activate_exercises)
    comprehensive_static_integrate_minutes = calc_active_time_comprehensive(
        plan_obj.static_integrate_exercises)
    comprehensive_total_minutes = comprehensive_inhibit_minutes + comprehensive_static_stretch_minutes + comprehensive_active_stretch_minutes + comprehensive_isolated_activate_minutes + comprehensive_static_integrate_minutes
    sline = body_part_line + ',' + insights_string + ',' + alert_cta_goal_line + ',' + get_summary_string(daily_plan)
    line = (body_part_line + ',' + insights_string + ',' + alert_cta_goal_line + ',' +

            ' ** '.join(inhibit_goals_triggers) + ',' +

            str(round(efficient_inhibit_minutes, 2)) + ',' + str(round(complete_inhibit_minutes, 2)) + ',' + str(
                round(comprehensive_inhibit_minutes, 2)) + ',' +

            ';'.join(convert_assigned_dict_exercises(
                plan_obj.inhibit_exercises)) + ',' +

            ' ** '.join(static_stretch_goals_triggers) + ',' +

            str(round(efficient_static_stretch_minutes, 2)) + ',' + str(
                round(complete_static_stretch_minutes, 2)) + ',' + str(
                round(comprehensive_static_stretch_minutes, 2)) + ',' +

            ';'.join(convert_assigned_dict_exercises(
                plan_obj.static_stretch_exercises)) + ',' +

            ' ** '.join(active_stretch_goals_triggers) + ',' +

            str(round(efficient_active_stretch_minutes, 2)) + ',' + str(
                round(complete_active_stretch_minutes, 2)) + ',' + str(
                round(comprehensive_active_stretch_minutes, 2)) + ',' +

            ';'.join(convert_assigned_dict_exercises(
                plan_obj.active_stretch_exercises)) + ',' +

            ' ** '.join(isolated_activate_goals_triggers) + ',' +

            str(round(efficient_isolated_activate_minutes, 2)) + ',' + str(
                round(complete_isolated_activate_minutes, 2)) + ',' + str(
                round(comprehensive_isolated_activate_minutes, 2)) + ',' +

            ';'.join(convert_assigned_dict_exercises(
                plan_obj.isolated_activate_exercises)) + ',' +

            ' ** '.join(static_integrate_goals_triggers) + ',' +

            str(round(efficient_static_integrate_minutes, 2)) + ',' + str(
                round(complete_static_integrate_minutes, 2)) + ',' + str(
                round(comprehensive_static_integrate_minutes, 2)) + ',' +

            ';'.join(convert_assigned_dict_exercises(
                plan_obj.static_integrate_exercises)) + ',' +

            str(round(efficient_total_minutes, 2)) + ',' + str(round(complete_total_minutes, 2)) + ',' + str(
                round(comprehensive_total_minutes, 2)) +

            "," + get_priority_counts_for_dosages(daily_plan)

            )
    return cool_down_line, line, sline