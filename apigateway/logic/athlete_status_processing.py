import datetime

from datastores.datastore_collection import DatastoreCollection
from fathomapi.utils.exceptions import NoSuchEntityException
from utils import parse_datetime, format_datetime, parse_date, format_date


class AthleteStatusProcessing(object):
    def __init__(self, user_id, event_date, datastore_collection=DatastoreCollection()):
        self.user_id = user_id
        self.event_date = format_date(event_date)
        self.current_time = event_date
        self.soreness_start_time = parse_date(format_date(event_date - datetime.timedelta(days=2)))
        self.typical_sessions_start_date = format_date(event_date - datetime.timedelta(days=14))
        self.daily_readiness_store = datastore_collection.daily_readiness_datastore
        self.post_session_store = datastore_collection.post_session_survey_datastore
        self.athlete_stats_store = datastore_collection.athlete_stats_datastore
        self.daily_plan_store = datastore_collection.daily_plan_datastore
        self.severe_pain_today_yesterday = False
        self.sore_body_parts = []
        self.cleaned_sore_body_parts = []
        self.hist_sore_status = []
        self.clear_candidates = []
        self.dormant_tipping_candidates = []
        self.current_sport_name = None
        self.current_position = None
        self.functional_strength_eligible = False
        self.completed_functional_strength_sessions = 0

    def get_previous_soreness(self):
        # get soreness from readiness
        try:
            readiness_surveys = self.daily_readiness_store.get(self.user_id,
                                                               start_date=self.soreness_start_time,
                                                               end_date=self.current_time,
                                                               last_only=False)
            for rs_survey in readiness_surveys:
                self.sore_body_parts.extend([s for s in rs_survey.soreness if s.severity > 1])
        except NoSuchEntityException:
            pass
        # get soreness from ps_survey
        post_session_surveys = self.post_session_store.get(user_id=self.user_id,
                                                           start_date=self.soreness_start_time,
                                                           end_date=self.current_time)
        post_session_surveys = [s for s in post_session_surveys if s is not None and self.soreness_start_time <= s.event_date_time < self.current_time]
        for ps_survey in post_session_surveys:
            self.sore_body_parts.extend([s for s in ps_survey.survey.soreness if s.severity > 1])
        # check for severe pain yesterday or today
        severe_pain_dates = [s.reported_date_time for s in self.sore_body_parts if s.pain and s.severity >= 3 and s.reported_date_time > self.soreness_start_time + datetime.timedelta(days=1)]
        if len(severe_pain_dates) > 0:
            self.severe_pain_today_yesterday = True
        self.cleaned_sore_body_parts = self.remove_duplicate_sore_body_parts()
        # get athlete_stats
        athlete_stats = self.athlete_stats_store.get(athlete_id=self.user_id)
        if athlete_stats is not None:
            # get historical soreness
            self.hist_sore_status, self.clear_candidates, self.dormant_tipping_candidates = athlete_stats.get_q2_q3_list()
            # get fs eligibility and sports
            self.current_sport_name = athlete_stats.current_sport_name.value if athlete_stats.current_sport_name is not None else None
            self.current_position = athlete_stats.current_position.value if athlete_stats.current_position is not None else None
            if (athlete_stats.functional_strength_eligible and (athlete_stats.next_functional_strength_eligible_date is None
                                                                or parse_datetime(athlete_stats.next_functional_strength_eligible_date) < self.current_time) and
                    not self.severe_pain_today_yesterday):
                self.functional_strength_eligible = True
            self.completed_functional_strength_sessions = athlete_stats.completed_functional_strength_sessions
            self.remove_duplicates_sore_body_parts_historic_soreness()
        return (self.cleaned_sore_body_parts,
                self.hist_sore_status,
                self.clear_candidates,
                self.dormant_tipping_candidates,
                self.current_sport_name,
                self.current_position,
                self.functional_strength_eligible,
                self.completed_functional_strength_sessions)

    def remove_duplicates_sore_body_parts_historic_soreness(self):
        q3_list = [{"body_part": q["body_part"], "side": q["side"]} for q in self.clear_candidates]
        q2_list = [{"body_part": q["body_part"], "side": q["side"]} for q in self.hist_sore_status]
        tipping_list = [{"body_part": q["body_part"], "side": q["side"]} for q in self.dormant_tipping_candidates]
        for sore_part in self.cleaned_sore_body_parts:
            part = {"body_part": sore_part["body_part"], "side": sore_part["side"]}
            if part in q2_list or part in q3_list:
                sore_part['delete'] = True
            elif part in tipping_list:
                for t in self.dormant_tipping_candidates:
                    if t['body_part'] == sore_part['body_part'] and t['side'] == sore_part['side']:
                        sore_part['status'] = t['status']
                        t['delete'] = True
                        break
        cleaned_sore_parts = [s for s in self.cleaned_sore_body_parts if not s.get('delete', False)]
        cleaned_tipping_candidates = [s for s in self.dormant_tipping_candidates if not s.get('delete', False)]
        self.cleaned_sore_body_parts = cleaned_sore_parts
        self.dormant_tipping_candidates = cleaned_tipping_candidates

    def remove_duplicate_sore_body_parts(self):
        self.cleaned_sore_body_parts = [s.json_serialise(api=True) for s in self.sore_body_parts]
        self.cleaned_sore_body_parts = [dict(t) for t in {tuple(d.items()) for d in self.cleaned_sore_body_parts}]
        unique_parts = []
        for soreness in self.cleaned_sore_body_parts:
            body_part = {'body_part': soreness['body_part'],
                         'side': soreness['side']}
            if body_part in unique_parts:
                if not soreness['pain']:
                    soreness['delete'] = True
                else:
                    for part in self.cleaned_sore_body_parts:
                        if part['body_part'] == soreness['body_part'] and part['side'] == soreness['side'] and not part['pain']:
                            part['delete'] = True
                            continue
            else:
                unique_parts.append(body_part)
        return [s for s in self.cleaned_sore_body_parts if not s.get('delete', False)]

    def get_typical_sessions(self):
        plans = self.daily_plan_store.get(
                                          user_id=self.user_id,
                                          start_date=self.typical_sessions_start_date,
                                          end_date=self.event_date
                                         )
        sessions = []
        for plan in plans:
            sessions.extend(plan.training_sessions)
        sessions = [s for s in sessions if s.event_date is not None]
        sessions = [{'sport_name': s.sport_name.value,
                     'strength_and_conditioning_type': s.strength_and_conditioning_type.value,
                     'session_type': s.session_type().value,
                     'event_date': format_datetime(s.event_date),
                     'duration': s.duration_minutes,
                     'count': 1} for s in sessions]
        sessions = sorted(sessions, key=lambda k: k['event_date'], reverse=True)
        filtered_sessions = []
        for session in sessions:
            if session['session_type'] == 1 and session['strength_and_conditioning_type'] is not None:
                session = remap_strength_conditioning_sessions(session)
            session['session_type'] = 6
            if session['session_type'] == 1 and session['strength_and_conditioning_type'] is None:
                pass
            elif session['session_type'] in [0, 2, 3, 6] and session['sport_name'] is None:
                pass
            elif len(filtered_sessions) == 0:
                filtered_sessions.append(session)
            else:
                exists = [session['sport_name'] == s['sport_name'] and
                          session['strength_and_conditioning_type'] == s['strength_and_conditioning_type'] and
                          session['session_type'] == s['session_type'] for s in filtered_sessions]
                if any(exists):
                    session = [filtered_sessions[i] for i in range(len(exists)) if exists[i]][0]
                    session['count'] += 1
                else:
                    filtered_sessions.append(session)
        filtered_sessions = sorted(filtered_sessions, key=lambda k: k['count'], reverse=True)

        return filtered_sessions[0:5]


def remap_strength_conditioning_sessions(session):
    sc_sport_map = {0: 52,
                    1: 53,
                    2: 54,
                    3: 55,
                    4: 56}
    session['sport_name'] = sc_sport_map[session['strength_and_conditioning_type']]
    session['strength_and_conditioning_type'] = None
    return session
