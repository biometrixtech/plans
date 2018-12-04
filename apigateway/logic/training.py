from decimal import Decimal, getcontext
from statistics import mean, stdev
import models.session as session


'''Deprecated
class DailyPlan(object):

    def __init__(self, event_date):
        self.user_id = ""
        self.event_date = event_date
        self.practice_sessions = []
        self.strength_conditioning_sessions = []  # includes cross training
        self.games = []
        self.tournaments = []
        self.pre_recovery = session.RecoverySession()
        self.post_recovery = session.RecoverySession()
        self.corrective_sessions = []
        self.bump_up_sessions = []
        self.daily_readiness_survey = None
        self.updated = False
        self.last_updated = None

    def daily_readiness_survey_completed(self):
        if self.daily_readiness_survey is not None:
            return True
        else:
            return False

    def add_scheduled_session(self, scheduled_session):

        if isinstance(scheduled_session, session.PracticeSession):
            self.practice_sessions.append(scheduled_session)
        elif isinstance(scheduled_session, session.StrengthConditioningSession):
            self.strength_conditioning_sessions.append(scheduled_session)
        elif isinstance(scheduled_session, session.Game):
            self.games.append(scheduled_session)
        elif isinstance(scheduled_session, session.Tournament):
            self.tournaments.append(scheduled_session)
'''

class TrainingCycle(object):

    def __init__(self):
        self.calculator = Calculator()
        self.start_date = None
        self.end_date = None
        self.sessions = []  # store all sessions here. if needed, create session arrays as methods that query on type
        self.recovery_modalities = []
        self.daily_readiness_surveys = []

    def internal_monotony(self):
        return self.calculator.get_monotony("internal_load", self.sessions)

    def external_total_monotony(self):
        return self.calculator.get_monotony("external_load", self.sessions)

    def external_high_monotony(self):
        return self.calculator.get_monotony("high_intensity_load", self.sessions)

    def external_mod_monotony(self):
        return self.calculator.get_monotony("mod_intensity_load", self.sessions)

    def external_low_monotony(self):
        return self.calculator.get_monotony("low_intensity_load", self.sessions)

    def internal_strain(self):
        return self.calculator.get_strain("internal_load", self.sessions)

    def external_total_strain(self):
        return self.calculator.get_strain("external_load", self.sessions)

    def external_high_strain(self):
        return self.calculator.get_strain("high_intensity_load", self.sessions)

    def external_mod_strain(self):
        return self.calculator.get_strain("mod_intensity_load", self.sessions)

    def external_low_strain(self):
        return self.calculator.get_strain("low_intensity_load", self.sessions)

    def estimated_internal_external_load_ratio(self):
        internal_load = list(x.internal_load for x in self.sessions if x.internal_load is not None
                             and x.external_load is not None)
        external_load = list(x.external_load for x in self.sessions if x.internal_load is not None
                             and x.external_load is not None)
        if internal_load is not None and external_load is not None:
            internal_load_sum = sum(internal_load)
            external_load_sum = sum(external_load)

            return internal_load_sum / external_load_sum
        else:
            return None

    def actual_internal_external_load_ratio(self):
        internal_load = list(x.internal_load for x in self.sessions if x.internal_load is not None
                             and x.external_load is not None and not x.estimated)
        external_load = list(x.external_load for x in self.sessions if x.internal_load is not None
                             and x.external_load is not None and not x.estimated)
        if internal_load is not None and external_load is not None:
            internal_load_sum = sum(internal_load)
            external_load_sum = sum(external_load)

            return internal_load_sum / external_load_sum
        else:
            return None

    def total_hours_training_wtd(self):
        total_minutes = list(x.duration_minutes for x in self.sessions if x.duration_minutes is not None)
        total_minutes_sum = sum(total_minutes)
        return total_minutes_sum / 60

    '''
    def get_daily_plan(self, date):
        daily_plan = DailyPlan(date)
        sessions = list(s for s in self.sessions if s.in_daily_plan(date))  # assumes these are datetimes

        recovery_modalities = list(r for r in self.recovery_modalities if r.in_daily_plan(date))

        for s in sessions:
            if isinstance(s, session.PracticeSession):
                daily_plan.practice_sessions.append(s)
            elif isinstance(s, session.BumpUpSession):
                daily_plan.bump_up_sessions.append(s)
            elif isinstance(s, session.Game):
                daily_plan.games.append(s)
            elif isinstance(s, session.CorrectiveSession):
                daily_plan.corrective_sessions.append(s)
            elif isinstance(s, session.StrengthConditioningSession):
                daily_plan.strength_conditioning_sessions.append(s)
            elif isinstance(s, session.Tournament):
                daily_plan.tournaments.append(s)

        daily_plan.recovery_modalities.extend(recovery_modalities)

        return daily_plan
    '''
    def get_last_daily_readiness_survey(self):

        readiness_count = len(self.daily_readiness_surveys)
        if readiness_count == 0:
            return None
        else:
            return self.daily_readiness_surveys[readiness_count - 1]


class TrainingHistory(object):

    def __init__(self):
        self.calculator = Calculator()

        self.training_cycles = []   # in reverse order where training_cycle = 0 is current, assuming max 5

    def internal_strain_spiking(self):
        return self.calculator.is_strain_spiking("internal_strain", self.training_cycles)

    def external_total_strain_spiking(self):
        return self.calculator.is_strain_spiking("external_total_strain", self.training_cycles)

    def external_high_strain_spiking(self):
        return self.calculator.is_strain_spiking("external_high_strain", self.training_cycles)

    def external_mod_strain_spiking(self):
        return self.calculator.is_strain_spiking("external_mod_strain", self.training_cycles)

    def external_low_strain_spiking(self):
        return self.calculator.is_strain_spiking("external_low_strain", self.training_cycles)

    def actual_internal_ACWR(self):
        return self.calculator.get_ACWR("internal_load", self.training_cycles, False)

    def estimated_internal_ACWR(self):
        return self.calculator.get_ACWR("internal_load", self.training_cycles, True)

    def actual_external_total_ACWR(self):
        return self.calculator.get_ACWR("external_load", self.training_cycles, False)

    def estimated_external_total_ACWR(self):
        return self.calculator.get_ACWR("external_load", self.training_cycles, True)

    def actual_external_high_ACWR(self):
        return self.calculator.get_ACWR("high_intensity_load", self.training_cycles, False)

    def estimated_external_high_ACWR(self):
        return self.calculator.get_ACWR("high_intensity_load", self.training_cycles, True)

    def actual_external_mod_ACWR(self):
        return self.calculator.get_ACWR("mod_intensity_load", self.training_cycles, False)

    def estimated_external_mod_ACWR(self):
        return self.calculator.get_ACWR("mod_intensity_load", self.training_cycles, True)

    def actual_external_low_ACWR(self):
        return self.calculator.get_ACWR("low_intensity_load", self.training_cycles, False)

    def estimated_external_low_ACWR(self):
        return self.calculator.get_ACWR("low_intensity_load", self.training_cycles, True)

    def actual_internal_ramp(self):
        return self.calculator.get_ramp("internal_load", self.training_cycles, False)

    def estimated_internal_ramp(self):
        return self.calculator.get_ramp("internal_load", self.training_cycles, True)

    def actual_external_total_ramp(self):
        return self.calculator.get_ramp("external_load", self.training_cycles, False)

    def estimated_external_total_ramp(self):
        return self.calculator.get_ramp("external_load", self.training_cycles, True)

    def actual_external_high_ramp(self):
        return self.calculator.get_ramp("high_intensity_load", self.training_cycles, False)

    def estimated_external_high_ramp(self):
        return self.calculator.get_ramp("high_intensity_load", self.training_cycles, True)

    def actual_external_mod_ramp(self):
        return self.calculator.get_ramp("mod_intensity_load", self.training_cycles, False)

    def estimated_external_mod_ramp(self):
        return self.calculator.get_ramp("mod_intensity_load", self.training_cycles, True)

    def actual_external_low_ramp(self):
        return self.calculator.get_ramp("low_intensity_load", self.training_cycles, False)

    def estimated_external_low_ramp(self):
        return self.calculator.get_ramp("low_intensity_load", self.training_cycles, True)

    def weighted_internal_external_load_ratio(self):

        ratios = []

        for t in range(0, len(self.training_cycles) + 1):
            weighting_factor = 1 / (t + 1)
            ratio = self.training_cycles[t].actual_internal_external_load_ratio()
            if ratio is not None:
                ratios.append(ratio * weighting_factor)

        if len(ratios) > 0:
            return mean(ratios)
        else:
            return None

    def is_athlete_fatiguing(self):
        actual_ratios = list(x.actual_internal_external_load_ratio() for x in self.training_cycles
                             if x.actual_internal_external_load_ratio() is not None)
        training_history_ratio = mean(actual_ratios)
        current_ratio = self.training_cycles[0].actual_internal_external_load_ratio()

        if training_history_ratio is None or current_ratio is None:
            return None

        if training_history_ratio < current_ratio:
            return True
        else:
            return False

    def global_load_estimation_parameters(self):

        sessions = []

        for training_cycle in self.training_cycles:
            # we do not want to include estimated sessions from the current training cycle in our calculations
            filtered_sessions = list(c for c in training_cycle.sessions if c.estimated is not False)
            sessions.extend(filtered_sessions)

        parameter = session.GlobalLoadEstimationParameters()

        total_load = list(s.external_load for s in sessions if s.external_load is not None)
        total_load_minutes = list(s.duration_minutes for s in sessions if s.duration_minutes is not None)
        parameter.external_load_per_minute = total_load / total_load_minutes

        high_load = list(s.high_intensity_load for s in sessions if s.high_intensity_load is not None)
        high_load_minutes = list(s.high_intensity_minutes for s in sessions if s.high_intensity_load is not None)
        parameter.high_intensity_load_per_minute = high_load / high_load_minutes

        mod_load = list(s.mod_intensity_load for s in sessions if s.mod_intensity_load is not None)
        mod_load_minutes = list(s.mod_intensity_minutes for s in sessions if s.mod_intensity_load is not None)
        parameter.moderate_intensity_avg_load_per_minute = mod_load / mod_load_minutes

        low_load = list(s.low_intensity_load for s in sessions if s.low_intensity_load is not None)
        low_load_minutes = list(s.low_intensity_minutes for s in sessions if s.low_intensity_load is not None)
        parameter.low_intensity_avg_load_per_minute = low_load / low_load_minutes

        parameter.high_intensity_percentage = \
            high_load_minutes / (high_load_minutes + mod_load_minutes + low_load_minutes)

        parameter.moderate_intensity_percentage = \
            mod_load_minutes / (high_load_minutes + mod_load_minutes + low_load_minutes)

        parameter.low_intensity_percentage = \
            low_load_minutes / (high_load_minutes + mod_load_minutes + low_load_minutes)

        return parameter

    def session_load_estimation_parameters(self):

        parameters = []

        for session_type in session.SessionType:
            sessions = []
            for training_cycle in self.training_cycles:
                # we do not want to include estimated sessions from the current training cycle in our calculations
                filtered_sessions = list(c for c in training_cycle.sessions if c.session_type is session_type and
                                         c.estimated is not False)
                sessions.extend(filtered_sessions)
            parameter = session.SessionLoadEstimationParameter()
            parameter.session_type = session_type

            total_load = list(s.external_load for s in sessions if s.external_load is not None)
            total_load_minutes = list(s.duration_minutes for s in sessions if s.duration_minutes is not None)
            parameter.total_avg_external_load_per_minute = total_load / total_load_minutes

            high_load = list(s.high_intensity_load for s in sessions if s.high_intensity_load is not None)
            parameter.high_intensity_avg_load_per_minute = high_load / total_load_minutes

            mod_load = list(s.mod_intensity_load for s in sessions if s.mod_intensity_load is not None)
            parameter.moderate_intensity_avg_load_per_minute = mod_load / total_load_minutes

            low_load = list(s.low_intensity_load for s in sessions if s.low_intensity_load is not None)
            parameter.low_intensity_avg_load_per_minute = low_load / total_load_minutes

            # intensity minutes are NOT used to calculate average but are used to calculate percentage of time
            high_load_minutes = list(s.high_intensity_minutes for s in sessions if s.high_intensity_load is not None)
            mod_load_minutes = list(s.mod_intensity_minutes for s in sessions if s.mod_intensity_load is not None)
            low_load_minutes = list(s.low_intensity_minutes for s in sessions if s.low_intensity_load is not None)

            parameter.high_intensity_percentage = \
                high_load_minutes / (high_load_minutes + mod_load_minutes + low_load_minutes)

            parameter.moderate_intensity_percentage = \
                mod_load_minutes / (high_load_minutes + mod_load_minutes + low_load_minutes)

            parameter.low_intensity_percentage = \
                low_load_minutes / (high_load_minutes + mod_load_minutes + low_load_minutes)

            parameters.append(parameter)

        return parameters

    def current_load_gap(self):

        calc = Calculator()
        load_gap = calc.get_load_gap(self.training_cycles, True)

        return load_gap

    def impute_load(self):

        training_cycle = self.training_cycles[0]

        internal_external_load_ratio = self.weighted_internal_external_load_ratio()

        for s in range(0, len(training_cycle.sessions)):
            if not training_cycle.sessions[s].estimated:
                if training_cycle.sessions[s].internal_load() is None:
                    if (training_cycle.sessions[s].external_load is not None
                            and training_cycle.sessions[s].duration_minutes is not None
                            and training_cycle.sessions[s].internal_load_imputed):
                        training_cycle.sessions[s].session_RPE = \
                            (internal_external_load_ratio * training_cycle.sessions[s].external_load) / \
                            training_cycle.sessions[s].duration_minutes

                elif training_cycle.sessions[s].external_load is None:
                    if (training_cycle.sessions[s].internal_load() is not None
                            and training_cycle.sessions[s].external_load_imputed):
                        training_cycle.sessions[s].external_load = \
                            (internal_external_load_ratio / training_cycle.sessions[s].internal_load())

                        training_cycle.sessions[s] = self.impute_intensity(training_cycle.sessions[s])

            else:   # estimated session
                if training_cycle.sessions[s].internal_load() is not None:  # should always be populated
                    training_cycle.sessions[s].external_load = \
                        (internal_external_load_ratio / training_cycle.sessions[s].internal_load())
                    training_cycle.sessions[s].external_load_imputed = True

                    training_cycle.sessions[s] = self.impute_intensity(training_cycle.sessions[s])

    def impute_intensity(self, training_session):
        estimation_parameters = self.session_load_estimation_parameters()

        # now estimate high, moderate and low
        estimation_parameter = (p for p in estimation_parameters if p.session_type == training_session.session_type)

        if estimation_parameter is None:
            estimation_parameter = self.global_load_estimation_parameters()

        if estimation_parameter is not None:
            training_session.high_intensity_load = \
                estimation_parameter.high_intensity_avg_load_per_minute * \
                training_session.duration_minutes

            training_session.high_intensity_minutes = \
                estimation_parameter.high_intensity_percentage * \
                training_session.duration_minutes

            training_session.mod_intensity_load = \
                estimation_parameter.mod_intensity_avg_load_per_minute * \
                training_session.duration_minutes

            training_session.mod_intensity_minutes = \
                estimation_parameter.mod_intensity_percentage * \
                training_session.duration_minutes

            training_session.low_intensity_load = \
                estimation_parameter.low_intensity_avg_load_per_minute * \
                training_session.duration_minutes

            training_session.low_intensity_minutes = \
                estimation_parameter.low_intensity_percentage * \
                training_session.duration_minutes

        return training_session


class LoadGap(object):

    def __init__(self):
        self.external_total_load = None
        self.external_high_intensity_load = None
        self.external_moderate_intensity_load = None
        self.external_low_intensity_load = None
        self.internal_total_load = None

        # actual minutes is tied to session type and cannot be discerned from load itself
        # in theory, we could use past bump up sessions, but that's not too reliable until we have a history

        # self.total_external_minutes = None
        # self.high_intensity_minutes = None
        # self.moderate_intensity_minutes = None
        # self.low_intensity_minutes = None
        # self.total_internal_minutes = None

    def exists(self):
        if (self.external_total_load is None and
                self.external_high_intensity_load is None and
                self.external_moderate_intensity_load is None and
                self.external_low_intensity_load is None and
                self.internal_total_load is None):
                # self.total_external_minutes is None and
                # self.high_intensity_minutes is None and
                # self.moderate_intensity_minutes is None and
                # self.low_intensity_minutes is None and
                # self.total_internal_minutes is None

            return True
        else:
            return False


class Calculator(object):

    def get_ramp(self, attribute_name, training_cycles, included_estimated=True):

        current_training_cycle = training_cycles[0]
        previous_training_cycle = training_cycles[1]

        if included_estimated:
            current_load = list(getattr(c, attribute_name) for c in current_training_cycle.sessions
                                if getattr(c, attribute_name) is not None)
            previous_load = list(getattr(c, attribute_name) for c in previous_training_cycle.sessions
                                 if getattr(c, attribute_name) is not None)
        else:
            current_load = list(getattr(c, attribute_name) for c in current_training_cycle.sessions
                                if getattr(c, attribute_name) is not None and not c.estimated)
            previous_load = list(getattr(c, attribute_name) for c in previous_training_cycle.sessions
                                 if getattr(c, attribute_name) is not None and not c.estimated)

        if current_load is not None and previous_load is not None:
            current_load_sum = sum(current_load)
            previous_load_sum = sum(previous_load)
            ramp = ((current_load_sum - previous_load_sum) / previous_load_sum) * 100
            return ramp
        else:
            return None

    def get_acute_chronic_load(self, attribute_name, training_cycles, included_estimated=True,
                               exclude_bump_up_sessions=False):

        current_training_cycle = training_cycles[0]

        if exclude_bump_up_sessions:
            if included_estimated:
                acute_load = list(getattr(c, attribute_name) for c in current_training_cycle.sessions
                                  if getattr(c, attribute_name) is not None
                                  and c.session_type is not session.SessionType.bump_up)
            else:
                acute_load = list(getattr(c, attribute_name) for c in current_training_cycle.sessions
                                  if getattr(c, attribute_name) is not None and not c.estimated
                                  and c.session_type is not session.SessionType.bump_up)
        else:
            if included_estimated:
                acute_load = list(getattr(c, attribute_name) for c in current_training_cycle.sessions
                                  if getattr(c, attribute_name) is not None)
            else:
                acute_load = list(getattr(c, attribute_name) for c in current_training_cycle.sessions
                                  if getattr(c, attribute_name) is not None and not c.estimated)

        chronic_load = []

        # loop through past training history and calculate persistent_2 load
        for training_cycle in training_cycles[1:]:
            if included_estimated:
                load = list(getattr(c, attribute_name) for c in training_cycle.sessions
                            if getattr(c, attribute_name) is not None)
            else:
                load = list(getattr(c, attribute_name) for c in training_cycle.sessions
                            if getattr(c, attribute_name) is not None and not c.estimated)
            load_sum = sum(load)
            chronic_load.append(load_sum)

        return acute_load, chronic_load

    def get_ACWR(self, attribute_name, training_cycles, include_estimated):

        acute_load, chronic_load = self.get_acute_chronic_load(attribute_name, training_cycles, include_estimated)

        if acute_load is not None and chronic_load is not None:
            return sum(acute_load) / mean(chronic_load)
        else:
            return None

    def get_monotony(self, attribute_name, sessions):

        load = list(getattr(c, attribute_name) for c in sessions
                    if getattr(c, attribute_name) is not None)

        if load is not None:
            return mean(load) / stdev(load)
        else:
            return None

    def get_strain(self, attribute_name, sessions):

        load = list(getattr(c, attribute_name) for c in sessions
                    if getattr(c, attribute_name) is not None)

        if load is not None:
            return (mean(load) / stdev(load)) * sum(load)
        else:
            return None

    def is_strain_spiking(self, attribute_name, training_cycles):
        strain_list = list(getattr(c, attribute_name) for c in training_cycles
                           if getattr(c, attribute_name) is not None)
        if strain_list is not None:
            if (training_cycles[0].strain - mean(strain_list)) / stdev(strain_list) > 1.2:
                return True
            else:
                return False
        else:
            return False

    def get_load_gap(self, training_cycles, exclude_bump_up_sessions):

        load_gap = LoadGap()

        acute_external_load, chronic_external_load = \
            self.get_acute_chronic_load("external_load", training_cycles, True, exclude_bump_up_sessions)
        load_gap.external_total_load = \
            self.get_acute_load_gap(acute_external_load, chronic_external_load)

        acute_external_high_load, chronic_external_high_load = \
            self.get_acute_chronic_load("high_intensity_load", training_cycles, True, exclude_bump_up_sessions)
        load_gap.external_high_intensity_load = \
            self.get_acute_load_gap(acute_external_high_load, chronic_external_high_load)

        acute_external_mod_load, chronic_external_mod_load = \
            self.get_acute_chronic_load("mod_intensity_load", training_cycles, True, exclude_bump_up_sessions)
        load_gap.external_mod_intensity_load = \
            self.get_acute_load_gap(acute_external_mod_load, chronic_external_mod_load)

        acute_external_low_load, chronic_external_low_load = \
            self.get_acute_chronic_load("low_intensity_load", training_cycles, True, exclude_bump_up_sessions)
        load_gap.external_low_intensity_load = \
            self.get_acute_load_gap(acute_external_low_load, chronic_external_low_load)

        acute_internal_load, chronic_internal_load = \
            self.get_acute_chronic_load("internal_load", training_cycles, True, exclude_bump_up_sessions)
        load_gap.internal_total_load = \
            self.get_acute_load_gap(acute_internal_load, chronic_internal_load)

        return load_gap

    def get_acute_load_gap(self, acute_load, chronic_load):

        """
        returns positive or negative load gaps for the athlete for a given week.

        If positive, the athlete should add load, if negative, the athlete is overreaching or over exerting and should
        taper load

        we use UNCOUPLED ACWR formula where the period of time used in the acute calculation is not included in the
        period of time for the persistent_2 calculation

        acute_load = array of actual load values this week
        chronic_load = array of previous 4 week averages of load (if contains Nones then acute_load represents totality of data)
        REMOVED: expected_remaining_load = array of expected load amounts remaining this week

        if we don't have at least 2 weeks of past data, we don't calculate load gap

        acwr = acute_load/chronic_load
        expected_acwr = (acute_load + expected_load) / chronic_load
        target_acwr = 1.45 = (acute_load + expected_load + target_load) / chronic_load

        1.45 = (acute_load + expected_load + target_load) / chronic_load
        (chronic_load * 1.45) = (acute_load + expected_load + x)
        1.45 * chronic_load = (acute_load + expected_load + x)
        (1.45 * chronic_load) - acute_load - expected_load =  x
        """
        getcontext().prec = 3
        # acute_load.extend(expected_remaining_load)

        adjusted_acute_load = list(a for a in acute_load if a is not None)

        acute_load_sum = Decimal(sum(adjusted_acute_load).item())

        adjusted_chronic_load = list(c for c in chronic_load if c is not None)

        if len(adjusted_chronic_load) < 2:
            return None

        else:
            previous_weeks_load = adjusted_chronic_load[-1]

            chronic_load_average = Decimal(mean(adjusted_chronic_load))

            target_load = (Decimal(1.45) * chronic_load_average) - acute_load_sum

            # ensure ramp does exceed 10%
            target_max = max((Decimal(1.10) * previous_weeks_load) - acute_load_sum, 0)

            target_load = min(target_max, target_load)

        return target_load
