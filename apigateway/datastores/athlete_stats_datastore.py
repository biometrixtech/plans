from aws_xray_sdk.core import xray_recorder
from config import get_mongo_collection
from models.stats import AthleteStats
from models.soreness import BodyPartLocation, HistoricSoreness, HistoricSorenessStatus, Soreness, BodyPart
from models.metrics import AthleteMetric, MetricType, DailyHighLevelInsight, WeeklyHighLevelInsight, MetricColor


class AthleteStatsDatastore(object):
    mongo_collection = 'athletestats'

    @xray_recorder.capture('datastore.AthlteStatsDatastore.get')
    def get(self, athlete_id):
        return self._query_mongodb(athlete_id)

    def put(self, items):
        if not isinstance(items, list):
            items = [items]
        try:
            for item in items:
                self._put_mongodb(item)
        except Exception as e:
            raise e

    def get_many(self, athletes):
        if not isinstance(athletes, list):
            athletes = [athletes]
        athlete_stats_list = []
        for athlete in athletes:
            athlete_stats = _query_mongodb(self, athlete)
            if athlete_stats is None:
                # athlete_stats = AthleteStats(athlete_id=)
                pass
            else:
                athlete_stats_list.append(athlete_stats)
        return athlete_stats_list

    @xray_recorder.capture('datastore.AthleteStatsDatastore._query_mongodb')
    def _query_mongodb(self, athlete_id):
        mongo_collection = get_mongo_collection(self.mongo_collection)
        if isinstance(athlete_id, list):
            query = {'athlete_id': {'$in': athlete_id}}
            mongo_results = mongo_collection.find(query)
            athlete_stats_list = []
            for mongo_result in mongo_results:
                athlete_stats_list.append(self.get_athlete_stats_from_mongo(mongo_result))

            return athlete_stats_list
        else:
            query = {'athlete_id': athlete_id}
            mongo_result = mongo_collection.find_one(query)

            if mongo_result is not None:
                return self.get_athlete_stats_from_mongo(mongo_result)
            else:
                return None

    def get_athlete_stats_from_mongo(self, mongo_result):
        athlete_stats = AthleteStats(athlete_id=mongo_result['athlete_id'])
        athlete_stats.event_date = mongo_result['event_date']
        athlete_stats.session_RPE = mongo_result.get('session_RPE', None)
        athlete_stats.session_RPE_event_date = mongo_result.get('session_RPE_event_date', None)
        athlete_stats.acute_avg_RPE = mongo_result['acute_avg_RPE']
        athlete_stats.acute_avg_readiness = mongo_result['acute_avg_readiness']
        athlete_stats.acute_avg_sleep_quality = mongo_result['acute_avg_sleep_quality']
        athlete_stats.acute_avg_max_soreness = mongo_result['acute_avg_max_soreness']
        athlete_stats.chronic_avg_RPE = mongo_result['chronic_avg_RPE']
        athlete_stats.chronic_avg_readiness = mongo_result['chronic_avg_readiness']
        athlete_stats.chronic_avg_max_soreness = mongo_result['chronic_avg_max_soreness']
        athlete_stats.functional_strength_eligible = mongo_result.get('functional_strength_eligible', False)
        athlete_stats.completed_functional_strength_sessions = mongo_result.get(
            'completed_functional_strength_sessions', 0)
        athlete_stats.next_functional_strength_eligible_date = mongo_result.get(
            'next_functional_strength_eligible_date', None)
        athlete_stats.current_sport_name = mongo_result.get('current_sport_name', None)
        athlete_stats.current_position = mongo_result.get('current_position', None)
        athlete_stats.historic_soreness = [self._historic_soreness_from_mongodb(s)
                                           for s in mongo_result.get('historic_soreness', [])]
        athlete_stats.daily_severe_soreness = [self._soreness_from_mongodb(s)
                                               for s in mongo_result.get('daily_severe_soreness', [])]
        athlete_stats.daily_severe_pain = [self._soreness_from_mongodb(s)
                                           for s in mongo_result.get('daily_severe_pain', [])]
        athlete_stats.daily_severe_soreness_event_date = mongo_result.get('daily_severe_soreness_event_date', None)
        athlete_stats.daily_severe_pain_event_date = mongo_result.get('daily_severe_soreness_event_date', None)
        athlete_stats.metrics = [self._metrics_from_mongodb(s) for s in mongo_result.get('metrics', [])]
        return athlete_stats

    @xray_recorder.capture('datastore.AthleteStatsDatastore._put_mongodb')
    def _put_mongodb(self, item):
        item = item.json_serialise()

        mongo_collection = get_mongo_collection(self.mongo_collection)
        query = {'athlete_id': item['athlete_id']}
        mongo_collection.replace_one(query, item, upsert=True)

    def _historic_soreness_from_mongodb(self, historic_soreness):

        hs = HistoricSoreness(BodyPartLocation(historic_soreness["body_part_location"]), historic_soreness["side"],
                              historic_soreness["is_pain"])
        hs.historic_soreness_status = HistoricSorenessStatus(historic_soreness["historic_soreness_status"])
        hs.streak = historic_soreness.get('streak', 0.0)
        hs.average_severity = historic_soreness.get('average_severity', 0.0)
        hs.last_reported = historic_soreness.get('last_reported', "")
        hs.streak_start_date = historic_soreness.get('streak_start_date', "")

        return hs

    def _soreness_from_mongodb(self, soreness_dict):
        soreness = Soreness()
        soreness.body_part = BodyPart(BodyPartLocation(soreness_dict['body_part']), None)
        soreness.pain = soreness_dict.get('pain', False)
        soreness.severity = soreness_dict['severity']
        soreness.side = soreness_dict.get('side', None)
        return soreness

    def _metrics_from_mongodb(self, metric):
        rec = AthleteMetric(metric['name'], MetricType(metric['metric_type']))
        rec.color = MetricColor(metric.get('color', 0))
        high_level_insight = metric.get('high_level_insight', 0)
        if rec.metric_type == MetricType.daily:
            rec.high_level_insight = DailyHighLevelInsight(high_level_insight)
        else:
            rec.high_level_insight = WeeklyHighLevelInsight(high_level_insight)
        rec.high_level_action_description = metric.get('high_level_action_description', "")
        rec.specific_insight_training_volume = metric.get('specific_insight_training_volume', "")
        rec.specific_insight_recovery = metric.get('specific_insight_recovery', 0)
        # rec.body_part_location = metric.get('body_part_location', None)
        # rec.body_part_side = metric.get('body_part_side', None)
        # rec.soreness = [self._soreness_from_mongodb(s) for s in metric.get('soreness', [])]
        rec.specific_actions = metric.get('specific_actions', [])
        return rec



