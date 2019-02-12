from models.soreness import BodyPartLocation, Soreness

class TestUtilities(object):

    def get_post_survey(self, RPE, soreness_list):

        survey = {
            "RPE" : RPE,
            "soreness": soreness_list
        }

        return survey


    def body_part_soreness(self, location_enum, severity, movement=None):

        if movement is None:
            soreness = {
                "body_part": location_enum,
                "severity": severity
            }
        else:
            soreness = {
                "body_part": location_enum,
                "severity": severity,
                "movement": movement
            }

        return soreness

    def body_part_pain(self, location_enum, severity, side, movement=None):

        if movement is None:
            soreness = {
                "body_part": location_enum,
                "severity": severity,
                "side":side,
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
