from models.training_volume import Assignment


class OTFCalculator(object):

    def get_pace(self, assignment_type, pace_level):

        assignment_list = []
        # these are the same because they increase grade to increase intensity
        assignment_list.append(Assignment(assignment_type="power_walker", assignment_level="base", min_value=1028 / 1609, max_value=800 / 1609))
        assignment_list.append(
            Assignment(assignment_type="power_walker", assignment_level="push", min_value=1028 / 1609,
                       max_value=800 / 1609))
        assignment_list.append(
            Assignment(assignment_type="power_walker", assignment_level="all_out", min_value=1028 / 1609,
                       max_value=800 / 1609))

        assignment_list.append(Assignment(assignment_type="jogger", assignment_level="base", min_value=801 / 1609, max_value=655 / 1609))
        assignment_list.append(
            Assignment(assignment_type="jogger", assignment_level="push", min_value=553 / 1609, max_value=480 / 1609))

        # TODO - get a better max number here, I am guessing!
        assignment_list.append(
            Assignment(assignment_type="jogger", assignment_level="all_out", min_value=480 / 1609, max_value=360/1609))

        # TODO - get a better max number here, I am guessing!
        assignment_list.append(Assignment(assignment_type="runner", assignment_level="base", min_value=656 / 1609, max_value=482/1609))
        # TODO - get a better max number here, I am guessing!
        assignment_list.append(Assignment(assignment_type="runner", assignment_level="push", min_value=481 / 1609, max_value=360/1609))
        # TODO - get a better max number here, I am guessing!
        assignment_list.append(Assignment(assignment_type="runner", assignment_level="all_out", min_value=481 / 1609, max_value=360/1609))

        assignment = next((a for a in assignment_list if a.assignment_type == assignment_type and
                           a.assignment_level == pace_level), None)

        return assignment

    def get_grade(self, assignment_type, pace_level, default_incline_value):

        assignment_list = []

        assignment_list.append(Assignment(assignment_type="power_walker", assignment_level="base",  min_value=.01, max_value=.03))
        assignment_list.append(
            Assignment(assignment_type="power_walker", assignment_level="push", assigned_value=.04))
        assignment_list.append(
            Assignment(assignment_type="power_walker", assignment_level="all_out", min_value=.10, max_value=.15))

        assignment = next((a for a in assignment_list if a.assignment_type == assignment_type and
                           a.assignment_level == pace_level),
                          Assignment(assignment_type=assignment_type, assignment_level=pace_level,
                                     assigned_value=default_incline_value))

        return assignment

