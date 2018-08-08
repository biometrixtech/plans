from models.soreness import BodyPartLocation, Soreness

class TestUtilities(object):

    def get_post_survey(self, RPE, soreness_list):

        survey = {
            "RPE" : RPE,
            "soreness": soreness_list
        }

        return survey


    def body_part_soreness(self, location_enum, severity):

        soreness = {
            "body_part": location_enum,
            "severity": severity
        }

        return soreness

    def body_part_location(self, location_enum):
        location = BodyPartLocation(location_enum)

        return location

    def body_part(self, body_enum, severity_score):
        soreness_item = Soreness()
        soreness_item.severity = severity_score
        soreness_item.body_part = BodyPartLocation(body_enum)
        return soreness_item
