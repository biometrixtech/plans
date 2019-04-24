from aws_xray_sdk.core import xray_recorder
from config import get_mongo_collection
from models.stats import AthleteStats
from models.soreness import BodyPartLocation, HistoricSoreness, HistoricSorenessStatus, Soreness, BodyPart
from models.metrics import AthleteMetric, MetricType, DailyHighLevelInsight, WeeklyHighLevelInsight, MetricColor, SpecificAction
from models.training_volume import StandardErrorRange
from utils import parse_datetime
from fathomapi.utils.exceptions import InvalidSchemaException
import numbers


class AthleteStatsDatastore(object):
    def __init__(self, mongo_collection='athletestats'):
        self.mongo_collection = mongo_collection

    @xray_recorder.capture('datastore.AthleteStatsDatastore.get')
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

    def delete(self, athlete_id=None):
        if athlete_id is None:
            raise InvalidSchemaException("Need to provide athlete_id to delete")
        self._delete_mongodb(athlete_id=athlete_id)

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

        athlete_stats.acute_internal_total_load = self._standard_error_from_monogodb(mongo_result.get('acute_internal_total_load', None))
        athlete_stats.acute_external_total_load = self._standard_error_from_monogodb(mongo_result.get('acute_external_total_load', None))
        athlete_stats.acute_external_high_intensity_load = self._standard_error_from_monogodb(mongo_result.get('acute_external_high_intensity_load', None))
        athlete_stats.acute_external_mod_intensity_load = self._standard_error_from_monogodb(mongo_result.get('acute_external_mod_intensity_load', None))
        athlete_stats.acute_external_low_intensity_load = self._standard_error_from_monogodb(mongo_result.get('acute_external_low_intensity_load', None))
        athlete_stats.chronic_internal_total_load = self._standard_error_from_monogodb(mongo_result.get('chronic_internal_total_load', None))
        athlete_stats.chronic_external_total_load = self._standard_error_from_monogodb(mongo_result.get('chronic_external_total_load', None))
        athlete_stats.chronic_external_high_intensity_load = self._standard_error_from_monogodb(mongo_result.get('chronic_external_high_intensity_load', None))
        athlete_stats.chronic_external_mod_intensity_load = self._standard_error_from_monogodb(mongo_result.get('chronic_external_mod_intensity_load', None))
        athlete_stats.chronic_external_low_intensity_load = self._standard_error_from_monogodb(mongo_result.get('chronic_external_low_intensity_load', None))

        athlete_stats.internal_monotony = self._standard_error_from_monogodb(mongo_result.get('internal_monotony', None))
        athlete_stats.historical_internal_monotony = [self._standard_error_from_monogodb(s)
                                                      for s in mongo_result.get('historic_internal_monotony', [])]
        athlete_stats.internal_strain = self._standard_error_from_monogodb(mongo_result.get('internal_strain', None))
        athlete_stats.historical_internal_strain = [self._standard_error_from_monogodb(s)
                                                    for s in mongo_result.get('historic_internal_strain', [])]
        athlete_stats.internal_strain_events = self._standard_error_from_monogodb(mongo_result.get('internal_strain_events', None))
        athlete_stats.external_monotony = self._standard_error_from_monogodb(mongo_result.get('external_monotony', None))
        athlete_stats.external_strain = self._standard_error_from_monogodb(mongo_result.get('external_strain', None))
        athlete_stats.internal_ramp = self._standard_error_from_monogodb(mongo_result.get('internal_ramp', None))
        athlete_stats.external_ramp = self._standard_error_from_monogodb(mongo_result.get('external_ramp', None))
        athlete_stats.internal_acwr = self._standard_error_from_monogodb(mongo_result.get('internal_acwr', None))
        athlete_stats.external_acwr = self._standard_error_from_monogodb(mongo_result.get('external_acwr', None))

        #athlete_stats.functional_strength_eligible = mongo_result.get('functional_strength_eligible', False)
        #athlete_stats.completed_functional_strength_sessions = mongo_result.get(
        #    'completed_functional_strength_sessions', 0)
        #athlete_stats.next_functional_strength_eligible_date = mongo_result.get(
        #    'next_functional_strength_eligible_date', None)
        athlete_stats.current_sport_name = mongo_result.get('current_sport_name', None)
        athlete_stats.current_position = mongo_result.get('current_position', None)
        athlete_stats.expected_weekly_workouts = _expected_workouts_from_mongo(mongo_result)
        athlete_stats.historic_soreness = [self._historic_soreness_from_mongodb(s)
                                           for s in mongo_result.get('historic_soreness', [])]
        athlete_stats.daily_severe_soreness = [self._soreness_from_mongodb(s)
                                               for s in mongo_result.get('daily_severe_soreness', [])]
        athlete_stats.daily_severe_pain = [self._soreness_from_mongodb(s)
                                           for s in mongo_result.get('daily_severe_pain', [])]
        athlete_stats.readiness_soreness = [self._soreness_from_mongodb(s)
                                            for s in mongo_result.get('readiness_soreness', [])]
        athlete_stats.post_session_soreness = [self._soreness_from_mongodb(s)
                                               for s in mongo_result.get('post_session_soreness', [])]
        athlete_stats.readiness_pain = [self._soreness_from_mongodb(s)
                                        for s in mongo_result.get('readiness_pain', [])]
        athlete_stats.post_session_pain = [self._soreness_from_mongodb(s)
                                           for s in mongo_result.get('post_session_pain', [])]
        athlete_stats.daily_severe_soreness_event_date = mongo_result.get('daily_severe_soreness_event_date', None)
        athlete_stats.daily_severe_pain_event_date = mongo_result.get('daily_severe_soreness_event_date', None)
        athlete_stats.metrics = [self._metrics_from_mongodb(s) for s in mongo_result.get('metrics', [])]
        athlete_stats.typical_weekly_sessions = mongo_result.get('typical_weekly_sessions', None)
        athlete_stats.wearable_devices = mongo_result.get('wearable_devices', [])
        return athlete_stats

    @xray_recorder.capture('datastore.AthleteStatsDatastore._put_mongodb')
    def _put_mongodb(self, item):
        item = item.json_serialise()

        mongo_collection = get_mongo_collection(self.mongo_collection)
        query = {'athlete_id': item['athlete_id']}
        mongo_collection.replace_one(query, item, upsert=True)

    @xray_recorder.capture('datastore.AthleteStatsDatastore._delete_mongodb')
    def _delete_mongodb(self, athlete_id):
        mongo_collection = get_mongo_collection(self.mongo_collection)
        query = {}
        if isinstance(athlete_id, list):
            query['athlete_id'] = {'$in': athlete_id}
        else:
            query['athlete_id'] = athlete_id
        if len(query) > 0:
            mongo_collection.delete_many(query)

    @staticmethod
    def _standard_error_from_monogodb(std_error):

        standard_error_range = StandardErrorRange()

        if std_error is None or isinstance(std_error, numbers.Number):

            standard_error_range.observed_value = std_error

        elif isinstance(std_error, dict):

            standard_error_range.lower_bound = std_error.get("lower_bound", None)
            standard_error_range.observed_value = std_error.get("observed_value", None)
            standard_error_range.upper_bound = std_error.get("upper_bound", None)
            standard_error_range.insufficient_data = std_error.get("insufficient_data", False)

        return standard_error_range

    @staticmethod
    def _historic_soreness_from_mongodb(historic_soreness):

        hs = HistoricSoreness(BodyPartLocation(historic_soreness["body_part_location"]), historic_soreness["side"],
                              historic_soreness["is_pain"])
        hs.historic_soreness_status = HistoricSorenessStatus(historic_soreness["historic_soreness_status"])
        hs.streak = historic_soreness.get('streak', 0.0)
        hs.average_severity = historic_soreness.get('average_severity', 0.0)
        hs.first_reported = historic_soreness.get('first_reported', "")
        hs.last_reported = historic_soreness.get('last_reported', "")
        hs.streak_start_date = historic_soreness.get('streak_start_date', "")
        hs.ask_acute_pain_question = historic_soreness.get('ask_acute_pain_question', False)
        hs.ask_persistent_2_question = historic_soreness.get('ask_persistent_2_question', False)

        return hs

    @staticmethod
    def _soreness_from_mongodb(soreness_dict):
        soreness = Soreness()
        soreness.body_part = BodyPart(BodyPartLocation(soreness_dict['body_part']), None)
        soreness.pain = soreness_dict.get('pain', False)
        soreness.severity = soreness_dict['severity']
        soreness.side = soreness_dict.get('side', None)
        soreness.reported_date_time = soreness_dict.get('reported_date_time', None)
        if soreness.reported_date_time is not None:
            soreness.reported_date_time = parse_datetime(soreness.reported_date_time)
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
        rec.insufficient_data_for_thresholds = metric.get('insufficient_data_for_thresholds', False)
        rec.range_wider_than_thresholds = metric.get('range_wider_than_thresholds', False)
        rec.specific_actions = [self._get_specific_actions_from_mongodb(sa)for sa in metric.get('specific_actions', [])]
        return rec

    @staticmethod
    def _get_specific_actions_from_mongodb(action):
        return SpecificAction(action['code'], action['text'], action['display'])


def _expected_workouts_from_mongo(mongo_result):
    typ_sessions_exp_workout = {"0-1": 0.5, "2-4": 3.0, "5+": 5.0, None: None}
    exp_workouts = mongo_result.get('expected_weekly_workouts', None)
    if exp_workouts is None:
        typical_weekly_sessions = mongo_result.get('typical_weekly_sessions', None)
        exp_workouts = typ_sessions_exp_workout[typical_weekly_sessions]
    return exp_workouts
