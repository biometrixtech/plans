from logic.soreness_and_injury import DailySoreness, BodyPart, BodyPartLocation, DailyReadinessSurvey
from models.daily_readiness import DailyReadiness
from utils import format_datetime
import datetime

class DailyReadinessDatastore(object):
    mongo_collection = 'readiness'

    def get(self, user_id):
        return self._query_mongodb(user_id)

    def put(self, items):
        if not isinstance(items, list):
            items = [items]
        try:
            for item in items:
                self._put_mongodb(item)
        except Exception as e:
            raise e

    def _query_mongodb(self, user_id):
        if user_id == "morning":
            daily_readiness = DailyReadinessSurvey()
            daily_readiness.report_date_time = "2018-06-27T11:00:00.00Z"

            return daily_readiness
        elif user_id == "afternoon":
            daily_readiness = DailyReadinessSurvey()
            daily_readiness.report_date_time = "2018-06-27T15:00:00.00Z"

            return daily_readiness
        elif user_id == "morning_practice":
            daily_readiness = DailyReadinessSurvey()
            daily_readiness_soreness = DailySoreness()
            daily_readiness_soreness.body_part = BodyPart(BodyPartLocation(12),
                                                                              1)
            daily_readiness_soreness.severity = 2
            daily_readiness.sleep_quality = 7
            daily_readiness.readiness = 8
            daily_readiness.soreness.append(daily_readiness_soreness)

            daily_readiness.report_date_time = "2018-06-27T11:00:00.00Z"

            return daily_readiness

    def _put_mongodb(self, item):
        item = self.item_to_mongodb(item)
        query = {'user_id': item['user_id'], 'event_date': format_datetime(item['event_date'])}


    @staticmethod
    def item_to_mongodb(dailyreadiness):
        """
        :param DailyReadiness dailyreadiness:
        :return: dict
        """
        item = {
            'event_date': dailyreadiness.event_date,
            'user_id': dailyreadiness.user_id,
            'soreness': [s.json_serialise() for s in dailyreadiness.soreness],
            'sleep_quality': dailyreadiness.sleep_quality,
            'readiness': dailyreadiness.readiness,
        }
        return {k: v for k, v in item.items() if v}

    @staticmethod
    def item_from_mongodb(mongo_result):
        pass


