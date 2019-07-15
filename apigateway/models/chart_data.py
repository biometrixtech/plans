from serialisable import Serialisable
from datetime import datetime, timedelta
from utils import format_date, format_datetime, parse_datetime, parse_date
from fathomapi.utils.exceptions import InvalidSchemaException
from models.soreness import Soreness
from models.body_parts import BodyPart
from models.soreness_base import BodyPartSide
from models.sport import SportName
from models.session import SportTrainingSession, SessionSource
from logic.soreness_processing import SorenessCalculator


class BaseChart(object):
    def __init__(self, end_date):
        self.end_date = end_date
        self.data = {}

        self.auto_fill_data()

    def __setattr__(self, name, value):
        if name in ['end_date']:
            if value is not None and not isinstance(value, datetime):
                try:
                    value = parse_datetime(value)
                except InvalidSchemaException:
                    value = parse_date(value)
        super().__setattr__(name, value)

    def auto_fill_data(self):

        start_date = self.end_date - timedelta(days=14)

        for i in range(1, 15):
            chart_data = DataSeriesData()
            chart_data.date = (start_date + timedelta(days=i)).date()
            day_of_week = (start_date + timedelta(days=i)).strftime('%a')
            chart_data.day_of_week = day_of_week
            self.data[chart_data.date] = chart_data

    def get_output_list(self):

        data = sorted(list(self.data.values()), key=lambda x: x.date, reverse=False)

        return data


class BaseChartBoolean(object):
    def __init__(self, end_date):
        self.end_date = end_date
        self.data = {}

        self.auto_fill_data()

    def __setattr__(self, name, value):
        if name in ['end_date']:
            if value is not None and not isinstance(value, datetime):
                try:
                    value = parse_datetime(value)
                except InvalidSchemaException:
                    value = parse_date(value)
        super().__setattr__(name, value)

    def auto_fill_data(self):

        start_date = self.end_date - timedelta(days=14)

        for i in range(1, 15):
            chart_data = DataSeriesBooleanData()
            chart_data.date = (start_date + timedelta(days=i)).date()
            day_of_week = (start_date + timedelta(days=i)).strftime('%a')
            chart_data.day_of_week = day_of_week
            self.data[chart_data.date] = chart_data

    def get_output_list(self):

        data = sorted(list(self.data.values()), key=lambda x: x.date, reverse=False)

        return data


class DataSeriesBaseData(Serialisable):
    def __init__(self, default_value):
        self.date = None
        self.day_of_week = ""
        self.value = default_value
        self.default_value = default_value

    def json_serialise(self):
        ret = {
            'date': format_date(self.date),
            'day_of_week': self.day_of_week,
            'value': self.value
        }
        return ret


class DataSeriesData(DataSeriesBaseData):
    def __init__(self):
        super().__init__(0)
        self.date = None
        self.day_of_week = ""

    @classmethod
    def json_deserialise(cls, input_dict):
        chart_data = cls()
        chart_data.date = input_dict['date']
        chart_data.day_of_week = input_dict.get('day_of_week', '')
        chart_data.value = input_dict.get('value', 0)
        return chart_data


class DataSeriesBooleanData(DataSeriesBaseData):
    def __init__(self):
        super().__init__(False)
        self.date = None
        self.day_of_week = ""

    @classmethod
    def json_deserialise(cls, input_dict):
        chart_data = cls()
        chart_data.date = input_dict['date']
        chart_data.day_of_week = input_dict.get('day_of_week', '')
        chart_data.value = input_dict.get('value', False)
        return chart_data


class TrainingVolumeChart(BaseChart):
    def __init__(self, end_date):
        super().__init__(end_date)

    def add_training_volume(self, training_session, load_stats):

        training_volume = training_session.training_volume(load_stats)
        if training_volume is not None and training_volume > 0 and training_session.event_date.date() in self.data:
            self.data[training_session.event_date.date()].training_volume += training_volume
            self.data[training_session.event_date.date()].sport_names.add(training_session.sport_name)

    def auto_fill_data(self):

        start_date = self.end_date - timedelta(days=14)

        for i in range(1, 15):
            chart_data = TrainingVolumeChartData()
            chart_data.date = (start_date + timedelta(days=i)).date()
            day_of_week = (start_date + timedelta(days=i)).strftime('%a')
            chart_data.day_of_week = day_of_week
            self.data[chart_data.date] = chart_data


class WorkoutChart(BaseChart, Serialisable):
    def __init__(self, end_date):
        super().__init__(end_date)
        self.status = ""
        self.bolded_text = []
        self.lockout = True
        self.last_workout_today = None
        self.last_sport_name = None

    def json_serialise(self):
        ret = {
            'end_date': format_date(self.end_date),
            'status': self.status,
            'bolded_text': self.bolded_text,
            'lockout': self.lockout,
            'data': [{"date": format_date(d), "value": v.json_serialise()} for d, v in self.data.items()],
            'last_workout_today': format_datetime(self.last_workout_today) if self.last_workout_today is not None else None,
            'last_sport_name': self.last_sport_name.value if self.last_sport_name is not None else None
        }

        return ret

    def add_training_volume(self, training_session, load_stats, sport_max_load):

        training_volume = training_session.training_volume(load_stats)
        if training_volume is not None and training_volume > 0 and training_session.event_date.date() in self.data:
            training_volume = round(training_volume, 2)
            self.data[training_session.event_date.date()].value += training_volume
            self.data[training_session.event_date.date()].sport_names.add(training_session.sport_name)

            summary = WorkoutSummary()
            summary.sport_name = training_session.sport_name
            summary.source = training_session.source
            if summary.source == SessionSource.user:
                summary.duration = training_session.duration_minutes
            else:
                summary.duration = training_session.duration_health
            summary.distance = round(training_session.distance, 2) if training_session.distance is not None else None
            if training_session.source == SessionSource.user and training_session.created_date is not None:
                summary.event_date = training_session.created_date
            else:
                summary.event_date = training_session.event_date
            summary.end_date = training_session.end_date
            summary.RPE = training_session.session_RPE
            summary.training_volume = training_volume

            if summary.event_date.date() == self.end_date.date():
                if self.last_workout_today is None:
                    self.last_workout_today = summary.event_date
                    self.last_sport_name = summary.sport_name
                elif summary.event_date > self.last_workout_today:
                    self.last_workout_today = summary.event_date
                    self.last_sport_name = summary.sport_name

            if (summary.event_date == self.last_workout_today and summary.event_date.date() == self.end_date.date()
                    and summary.sport_name.value in sport_max_load):

                if summary.event_date == sport_max_load[summary.sport_name.value].event_date_time:
                    if sport_max_load[summary.sport_name.value].first_time_logged:
                        self.status = f"First {summary.sport_name.get_display_name()} workout recorded!"
                        self.bolded_text = []
                        self.bolded_text.append(summary.sport_name.get_display_name())
                    else:
                        self.status = f"You set a new personal record for {summary.sport_name.get_display_name()} load!"
                        self.bolded_text = []
                        self.bolded_text.append(SportName(summary.sport_name.value).name)
                else:
                    percent = int(round((training_volume / sport_max_load[summary.sport_name.value].load) * 100, 0))
                    self.status = f"Today's workout was {str(percent)}% of your {summary.sport_name.get_display_name()} PR"
                    self.bolded_text = []
                    self.bolded_text.append(summary.sport_name.get_display_name())
                    self.bolded_text.append(str(percent) + "%")

            self.data[training_session.event_date.date()].sessions.append(summary)

            if (self.end_date.date() - training_session.event_date.date()).days < 7:
                self.lockout = False

    def auto_fill_data(self):

        start_date = self.end_date - timedelta(days=14)

        for i in range(1, 15):
            chart_data = WorkoutChartData()
            chart_data.date = (start_date + timedelta(days=i)).date()
            day_of_week = (start_date + timedelta(days=i)).strftime('%a')
            chart_data.day_of_week = day_of_week
            self.data[chart_data.date] = chart_data


class TrainingVolumeChartData(Serialisable):
    def __init__(self):
        self.date = None
        self.day_of_week = ""
        self.sport_names = set()
        self.training_volume = 0

    def json_serialise(self):
        ret = {
            'date': format_date(self.date),
            'day_of_week': self.day_of_week,
            'sport_names': [sport_name.value for sport_name in self.sport_names if sport_name is not None],
            'training_volume': self.training_volume
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        chart_data = cls()
        chart_data.date = input_dict['date']
        chart_data.day_of_week = input_dict.get('day_of_week', '')
        chart_data.sport_names = set(SportName(sport_name) for sport_name in input_dict.get('sport_names', []))
        chart_data.training_volume = input_dict.get('training_volume', 0)
        return chart_data


class WorkoutSummary(Serialisable):
    def __init__(self):
        self.sport_name = None
        self.source = SessionSource.user
        self.duration = 0
        self.event_date = None
        self.end_date = None
        self.distance = 0
        self.RPE = 0
        self.training_volume = 0

    def json_serialise(self):
        ret = {
            'sport_name': self.sport_name.value if self.sport_name is not None else None,
            'source': self.source.value if self.source is not None else None,
            'duration': self.duration,
            'event_date': format_datetime(self.event_date),
            'end_date': format_datetime(self.end_date),
            'distance': self.distance,
            'RPE': self.RPE,
            'training_volume': self.training_volume
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        summary = cls()
        summary.sport_name = input_dict['sport_name']
        summary.source = input_dict.get('source', 0)
        summary.duration = input_dict.get('duration', 0)
        summary.event_date = input_dict['event_date']
        summary.end_date = input_dict['end_date']
        summary.distance = input_dict.get('distance', 0)
        summary.RPE = input_dict.get('RPE', 0)
        summary.training_volume = input_dict.get('training_volume', 0)

        return summary

    def __setattr__(self, key, value):
        if key in ['event_date', 'end_date',]:
            if not isinstance(value, datetime) and value is not None:
                value = parse_datetime(value)
        elif key == 'sport_name' and value is not None and not isinstance(value, SportName):
            value = SportName(value)
        elif key == 'source' and not isinstance(value, SessionSource):
            value = SessionSource(value)
        super().__setattr__(key, value)


class WorkoutChartData(Serialisable):
    def __init__(self):
        self.date = None
        self.day_of_week = ""
        self.sport_names = set()
        self.value = 0
        self.sessions = []

    def json_serialise(self):
        ret = {
            'date': format_date(self.date),
            'day_of_week': self.day_of_week,
            'sport_names': [sport_name.value for sport_name in self.sport_names if sport_name is not None],
            'value': self.value,
            'sessions': [session.json_serialise() for session in self.sessions]
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        chart_data = cls()
        chart_data.date = input_dict['date']
        chart_data.day_of_week = input_dict.get('day_of_week', '')
        chart_data.sport_names = set(SportName(sport_name) for sport_name in input_dict.get('sport_names', []))
        chart_data.value = input_dict.get('value', 0)
        chart_data.sessions = list(WorkoutSummary.json_deserialise(s) for s in input_dict.get('sessions', []))
        return chart_data


class MuscularStrainChart(BaseChart):
    def __init__(self, end_date):
        super().__init__(end_date)  # backdate this since it was calculated overnight

    def add_muscular_strain(self, muscular_strain):

        if muscular_strain is not None and (muscular_strain.date - timedelta(days=1)).date() in self.data:
            self.data[(muscular_strain.date - timedelta(days=1)).date()].value += muscular_strain.value


class DOMSChart(BaseChart):
    def __init__(self, end_date):
        self.day_scale = 3
        super().__init__(end_date + timedelta(days=self.day_scale))

    def process_doms(self, doms_list, soreness_list):

        doms = {}

        start_date = self.end_date - timedelta(days=14)

        for i in range(1, 15):
            new_date = (start_date + timedelta(days=i)).date()
            doms[new_date] = []

        for d in doms_list:
            daily_soreness = list(s for s in soreness_list if s.body_part.location == d.body_part_location and s.side == d.side and not s.pain)
            for s in daily_soreness:
                if s.reported_date_time.date() in doms:
                    doms[s.reported_date_time.date()].append(s)

        for soreness_date, soreness in doms.items():
            if len(soreness) > 0:
                severity_list = sorted(doms[soreness_date], key=lambda x: x.severity, reverse=True)
                self.add_doms(severity_list[0])

        # do we have soreness data for today? (We may need to fake it)
        todays_soreness = doms[(self.end_date - timedelta(days=self.day_scale)).date()]
        if len(todays_soreness) == 0:
            doms_severity = sorted(doms_list, key=lambda x: x.average_severity, reverse=True)
            fake_soreness = Soreness()
            fake_soreness.side = doms_severity[0].side
            fake_soreness.body_part = BodyPart(doms_severity[0].body_part_location, None)
            fake_soreness.severity = doms_severity[0].average_severity
            fake_soreness.reported_date_time = self.end_date - timedelta(days=self.day_scale)
            self.add_doms(fake_soreness)

    def add_doms(self, soreness):

        if soreness is not None and soreness.reported_date_time.date() in self.data:
            self.data[soreness.reported_date_time.date()].value = soreness.severity
            if soreness.reported_date_time.date() + timedelta(days=self.day_scale) == self.end_date.date():
                for s in range(1,self.day_scale + 1):
                    self.data[(soreness.reported_date_time + timedelta(days=s)).date()].value = \
                        self.get_projected_severity(soreness.severity, s)

    def get_projected_severity(self, severity, day):

        if severity <= 1:
            if day == 1:
                return 0
            else:
                return None
        elif 1 < severity <= 2:
            if day == 1:
                return 1.6
            elif day == 2:
                return 0
            else:
                return None
        elif 2 < severity <= 3:
            if day == 1:
                return 2.65
            elif day ==2:
                return 1.75
            elif day == 3:
                return 0
            else:
                return None
        elif 3 < severity <= 4:
            if day == 1:
                return 3.75
            elif day == 2:
                return 3.2
            elif day == 3:
                return 2
        elif 4 < severity <=5:
            if day == 1:
                return 4.8
            elif day == 2:
                return 4.25
            elif day == 3:
                return 3
        else:
            return None


class HighRelativeLoadChart(BaseChartBoolean):
    def __init__(self, end_date):
        super().__init__(end_date)

    def add_relative_load(self, relative_load):

        if relative_load is not None and relative_load.date.date() in self.data:
            self.data[relative_load.date.date()].value = True


class BodyPartSummary(Serialisable):
    def __init__(self):
        self.body_part = None
        self.side = 0
        self.pain = False
        self.value = 0

    def __hash__(self):
        return hash((self.body_part, self.side, self.pain))

    def __eq__(self, other):
        return ((self.body_part == other.body_part,
                 self.side == other.side, self.pain == other.pain))

    def json_serialise(self):
        ret = {
            'body_part': self.body_part,
            'side': self.side,
            'pain': self.pain,
            'value': self.value
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        body_part = cls()
        body_part.body_part = input_dict['body_part']
        body_part.side = input_dict.get('side', 0)
        body_part.pain = input_dict.get('pain', False)
        body_part.value = input_dict.get('value', 0)
        return body_part


class BodyResponseChartData(Serialisable):
    def __init__(self):
        self.date = None
        self.day_of_week = ""
        self.pain_value = 0
        self.soreness_value = 0
        self.body_parts = []

    def json_serialise(self):
        ret = {
            'date': format_date(self.date),
            'day_of_week': self.day_of_week,
            'pain_value': self.pain_value,
            'soreness_value': self.soreness_value,
            'body_parts': list(b.json_serialise() for b in self.body_parts)
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        chart_data = cls()
        chart_data.date = input_dict['date']
        chart_data.day_of_week = input_dict.get('day_of_week', "")
        chart_data.pain_value = input_dict.get('pain_value', 0)
        chart_data.soreness_value = input_dict.get('soreness_value', 0)
        chart_data.body_parts = list(BodyPartSummary.json_deserialise(b) for b in input_dict.get('body_parts', []))
        return chart_data


class BodyResponseChart(Serialisable):
    def __init__(self, end_date):
        self.end_date = end_date
        self.data = {}
        self.auto_fill_data()
        self.status = ""
        self.bolded_text = []
        self.max_value_today = None
        self.max_value_pain = None
        self.lockout = True

    def __setattr__(self, name, value):
        if name in ['end_date']:
            if value is not None and not isinstance(value, datetime):
                try:
                    value = parse_datetime(value)
                except InvalidSchemaException:
                    value = parse_date(value)
        super().__setattr__(name, value)

    def json_serialise(self):
        ret = {
            'end_date': format_date(self.end_date),
            'status': self.status,
            'bolded_text': [t for t in self.bolded_text],
            'max_value_today': self.max_value_today,
            'max_value_pain': self.max_value_pain,
            'lockout': self.lockout,
            'data': [{"date": format_date(d), "value": v.json_serialise()} for d, v in self.data.items()]
        }

        return ret

    def get_output_list(self):

        data = sorted(list(self.data.values()), key=lambda x: x.date, reverse=False)

        return data

    def auto_fill_data(self):

        start_date = self.end_date - timedelta(days=14)

        for i in range(1, 15):
            chart_data = BodyResponseChartData()
            chart_data.date = (start_date + timedelta(days=i)).date()
            day_of_week = (start_date + timedelta(days=i)).strftime('%a')
            chart_data.day_of_week = day_of_week
            chart_data.body_parts = {}

            self.data[chart_data.date] = chart_data

    def scale_severity(self, severity):

        if severity <= 1:
            return 1
        elif 1 < severity <= 3:
            return 2
        else:
            return 3

    def get_projected_doms_severity(self, severity):

        if severity is None:
            return None

        if 1 < severity <= 2:
            return 2

        elif 2 < severity <= 3:
            return 3

        elif 3 < severity <= 4:
            return 4

        elif 4 < severity <= 5:
            return 5
        else:
            return None

    def set_status_text(self):

        if self.max_value_pain:
            if self.max_value_today <= 1:
                self.status = "Avoid worsening pain by modifying training."
            elif 1 < self.max_value_today <= 3:
                self.status = "To help avoid injury, modify training to avoid pain."
            else:
                self.status = "Consider seeing a doctor about your pain symptoms."
        else:
            days = self.get_projected_doms_severity(self.max_value_today)
            if days is None:
                self.status = ""
            elif days > 1:
                self.status = str(days) + " days of soreness projected without active recovery"
                self.bolded_text = []
                self.bolded_text.append(str(days) + " days")
            else:
                self.bolded_text = []
                self.status = str(days) + " day of soreness projected without active recovery"
                self.bolded_text.append(str(days) + " days")

    def process_soreness(self, soreness_list):

        for s in soreness_list:
            self.add_soreness(s)

    def add_soreness(self, soreness):

        if soreness is not None and soreness.reported_date_time.date() in self.data:
            if (self.end_date.date() - soreness.reported_date_time.date()).days < 7:
                self.lockout = False

            if self.end_date.date() == soreness.reported_date_time.date():
                if self.max_value_today is None:
                    self.max_value_today = soreness.severity
                    self.max_value_pain = soreness.pain
                elif self.max_value_pain:
                    if soreness.pain:
                        if soreness.severity > self.max_value_today:
                            self.max_value_today = soreness.severity
                    else: #highest value so far is pain but soreness is soreness
                        if self.max_value_today <= 1:
                            if soreness.severity > 2:
                                self.max_value_pain = False
                                self.max_value_today = soreness.severity
                        elif 1 < self.max_value_today <= 2:
                            if soreness.severity > 3:
                                self.max_value_pain = False
                                self.max_value_today = soreness.severity
                        elif 2 < self.max_value_today <= 3:
                            if soreness.severity > 4:
                                self.max_value_pain = False
                                self.max_value_today = soreness.severity
                else:
                    if not soreness.pain:
                        if soreness.severity > self.max_value_today:
                            self.max_value_today = soreness.severity
                    else: #highest value so far is soreness but soreness is pain
                        if self.max_value_today < 3:
                            self.max_value_pain = True
                            self.max_value_today = soreness.severity
                        elif 3 <= self.max_value_today < 4:
                            if soreness.severity >= 2:
                                self.max_value_pain = True
                                self.max_value_today = soreness.severity
                        elif self.max_value_today >= 4:
                            if soreness.severity >= 3:
                                self.max_value_pain = False
                                self.max_value_today = soreness.severity

                self.set_status_text()

            if soreness.pain:
                self.data[soreness.reported_date_time.date()].pain_value = max(self.scale_severity(soreness.severity),
                                                                               self.data[soreness.reported_date_time.date()].pain_value)
            else:
                self.data[soreness.reported_date_time.date()].soreness_value = max(self.scale_severity(soreness.severity),
                                                                                   self.data[soreness.reported_date_time.date()].soreness_value)
            body_part_summary = BodyPartSummary()
            body_part_summary.body_part = soreness.body_part.location.value
            body_part_summary.side = soreness.side
            body_part_summary.value = self.scale_severity(soreness.severity)
            body_part_summary.pain = soreness.pain

            if body_part_summary in self.data[soreness.reported_date_time.date()].body_parts:
                self.data[soreness.reported_date_time.date()].body_parts[body_part_summary].value = max(body_part_summary.value,
                                                                                                        self.data[
                                                                                                            soreness.reported_date_time.date()].body_parts[
                                                                                                            body_part_summary].value)

            self.data[soreness.reported_date_time.date()].body_parts[body_part_summary] = body_part_summary


class BodyPartChartData(Serialisable):
    def __init__(self):
        self.date = None
        self.day_of_week = ""
        self.value = 0

    def json_serialise(self):
        ret = {
            'date': format_date(self.date),
            'day_of_week': self.day_of_week,
            'value': self.value
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        chart_data = cls()
        chart_data.date = input_dict['date']
        chart_data.day_of_week = input_dict.get('day_of_week', "")
        chart_data.value = input_dict.get('value', 0)
        return chart_data


class BodyPartChartCollection(object):
    def __init__(self, end_date):
        self.end_date = end_date
        self.body_parts = {}

    def process_soreness_list(self, soreness_list):

        for s in soreness_list:
            body_part_side = BodyPartSide(s.body_part.location, s.side)
            if body_part_side not in self.body_parts:
                self.body_parts[body_part_side] = BodyPartChart(self.end_date)
                self.body_parts[body_part_side].auto_fill_data()
            self.body_parts[body_part_side].add_soreness(s)

    def get_soreness_dictionary(self):

        soreness_dictionary = {}

        for body_part_side, body_part_chart in self.body_parts.items():
            if body_part_chart.contains_soreness_data:
                soreness_dictionary[body_part_side] = body_part_chart.get_soreness_output_list()
            else:
                soreness_dictionary.pop(body_part_side, None)

        return soreness_dictionary

    def get_pain_dictionary(self):

        pain_dictionary = {}

        for body_part_side, body_part_chart in self.body_parts.items():
            if body_part_chart.contains_pain_data:
                pain_dictionary[body_part_side] = body_part_chart.get_pain_output_list()
            else:
                pain_dictionary.pop(body_part_side, None)

        return pain_dictionary


class BodyPartChart(object):
    def __init__(self, end_date):
        self.end_date = end_date
        self.soreness_data = {}
        self.pain_data = {}
        self.contains_soreness_data = False
        self.contains_pain_data = False

        self.auto_fill_data()

    def __setattr__(self, name, value):
        if name in ['end_date']:
            if value is not None and not isinstance(value, datetime):
                try:
                    value = parse_datetime(value)
                except InvalidSchemaException:
                    value = parse_date(value)
        super().__setattr__(name, value)

    def get_soreness_output_list(self):

        if self.contains_soreness_data:
            data = sorted(list(self.soreness_data.values()), key=lambda x: x.date, reverse=False)
        else:
            data = []

        return data

    def get_pain_output_list(self):

        if self.contains_pain_data:
            data = sorted(list(self.pain_data.values()), key=lambda x: x.date, reverse=False)
        else:
            data = []

        return data

    def auto_fill_data(self):

        start_date = self.end_date - timedelta(days=14)

        for i in range(1, 15):
            soreness_chart_data = BodyPartChartData()
            soreness_chart_data.date = (start_date + timedelta(days=i)).date()
            day_of_week = (start_date + timedelta(days=i)).strftime('%a')
            soreness_chart_data.day_of_week = day_of_week

            pain_chart_data = BodyPartChartData()
            pain_chart_data.date = (start_date + timedelta(days=i)).date()
            pain_chart_data.day_of_week = day_of_week
            self.soreness_data[soreness_chart_data.date] = soreness_chart_data
            self.pain_data[pain_chart_data.date] = pain_chart_data

    def add_soreness(self, soreness):

        if soreness.pain:
            if soreness is not None and soreness.reported_date_time.date() in self.pain_data:
                self.pain_data[soreness.reported_date_time.date()].value = max(
                    SorenessCalculator().get_severity(soreness.severity, soreness.movement),
                    self.pain_data[soreness.reported_date_time.date()].value)
                self.contains_pain_data = True
        else:
            if soreness is not None and soreness.reported_date_time.date() in self.soreness_data:
                self.soreness_data[soreness.reported_date_time.date()].value = max(
                    SorenessCalculator().get_severity(soreness.severity, soreness.movement),
                    self.soreness_data[soreness.reported_date_time.date()].value)
                self.contains_soreness_data = True


class OveractiveUnderactiveChartData(Serialisable):
    def __init__(self):
        self.overactive_body_parts = []
        self.underactive_body_parts = []

    def json_serialise(self):
        ret = {
            'overactive_body_parts': self.overactive_body_parts,
            'underactive_body_parts': self.underactive_body_parts,
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        chart_data = cls()
        chart_data.overactive_body_parts = input_dict.get('overactive_body_parts', [])
        chart_data.underactive_body_parts = input_dict.get('overactive_body_parts', [])
        return chart_data


class TightUnderactiveChartData(Serialisable):
    def __init__(self):
        self.tight_body_parts = []
        self.underactive_body_parts = []

    def json_serialise(self):
        ret = {
            'tight_body_parts': self.tight_body_parts,
            'underactive_body_parts': self.underactive_body_parts,
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        chart_data = cls()
        chart_data.tight_body_parts = input_dict.get('tight_body_parts', [])
        chart_data.underactive_body_parts = input_dict.get('overactive_body_parts', [])
        return chart_data