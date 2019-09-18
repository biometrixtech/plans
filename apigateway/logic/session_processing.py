from models.session import SessionSource
from models.sport import SportName


class SessionMergeProcessing(object):
    def __init__(self, source_session_list, destination_session):
        self.source_sessions = source_session_list
        self.destination_session = destination_session

    def merge_all_sessions(self):

        for s in self.source_sessions:
            self.destination_session = self.merge_sessions(s, self.destination_session)
            s.deleted = True

        # TODO make sure this handles unsaved HK sessions

    def merge_sessions(self, source_session, destination_session):

        if source_session.source == SessionSource.three_sensor:
            raise Exception("3-sensor sessions may not be source sessions for merging.")

        if source_session.id is not None:
            destination_session.source_session_ids.append(source_session.id)
            destination_session.source_session_ids.extend(source_session.source_session_ids)

        destination_session.apple_health_kit_ids.extend(source_session.apple_health_kit_ids)
        destination_session.apple_health_kit_source_names.extend(source_session.apple_health_kit_source_names)

        destination_session.source_session_ids = list(set(destination_session.source_session_ids))
        destination_session.apple_health_kit_ids = list(set(destination_session.apple_health_kit_ids))
        destination_session.apple_health_kit_source_names = list(set(destination_session.apple_health_kit_source_names))

        destination_session = self.merge_dates(source_session, destination_session)
        destination_session = self.merge_sport_info(source_session, destination_session)
        destination_session = self.merge_durations(source_session, destination_session)
        destination_session = self.merge_health_kit_data(source_session, destination_session)
        destination_session = self.merge_variable_to_max(source_session, destination_session, "shrz")

        # we will never have source as three sensor
        #if source_session.source == SessionSource.three_sensor and destination_session.source != SessionSource.three_sensor:
        #    destination_session.asymmetry = source_session.asymmetry

        # unsure about how this triggers
        if destination_session.source == SessionSource.user:
            if source_session.source != SessionSource.user:
                destination_session.source = source_session.source

        return destination_session

    def merge_health_kit_data(self, source_session, destination_session):

        try:
            destination_session = self.merge_variable_to_max(source_session, destination_session, "calories")
        except ValueError:
            pass

        try:
            destination_session = self.merge_variable_to_max(source_session, destination_session, "distance")
        except ValueError:
            pass

        return destination_session

    def merge_durations(self, source_session, destination_session):

        destination_session = self.merge_variable_to_max(source_session, destination_session, "duration_sensor")
        destination_session = self.merge_variable_to_max(source_session, destination_session, "duration_health")
        destination_session = self.merge_variable_to_max(source_session, destination_session, "duration_minutes")

        return destination_session

    def merge_variable_to_max(self, source_session, destination_session, variable_name):
        if getattr(source_session, variable_name) is not None and getattr(destination_session, variable_name) is None:
            setattr(destination_session, variable_name, getattr(source_session, variable_name))

        elif getattr(source_session, variable_name) is not None and getattr(destination_session, variable_name) is not None and getattr(source_session, variable_name) > getattr(destination_session, variable_name):
            setattr(destination_session, variable_name, getattr(source_session, variable_name))

        return destination_session

    def merge_variable_to_min(self, source_session, destination_session, variable_name):
        if getattr(source_session, variable_name) is not None and getattr(destination_session, variable_name) is None:
            setattr(destination_session, variable_name, getattr(source_session, variable_name))

        elif getattr(source_session, variable_name) is not None and getattr(destination_session,
                                                                            variable_name) is not None and getattr(
                source_session, variable_name) < getattr(destination_session, variable_name):
            setattr(destination_session, variable_name, getattr(source_session, variable_name))

        return destination_session

    def merge_dates(self, source_session, destination_session):

        if source_session.source != SessionSource.user and destination_session.source == SessionSource.user:
            destination_session.event_date = source_session.event_date
            destination_session.end_date = source_session.end_date
            destination_session.completed_date_time = source_session.completed_date_time
        elif source_session.source == SessionSource.user:
             pass
        else:
            destination_session = self.merge_variable_to_min(source_session, destination_session, "event_date")
            destination_session = self.merge_variable_to_max(source_session, destination_session, "end_date")
            destination_session = self.merge_variable_to_min(source_session, destination_session, "created_date")
            destination_session = self.merge_variable_to_max(source_session, destination_session, "completed_date_time")

        return destination_session

    def merge_sport_info(self, source_session, destination_session):

        if source_session.source == SessionSource.health and destination_session.source != SessionSource.health:
            destination_session.sport_name = source_session.sport_name
            destination_session.sport_type = source_session.sport_type
        elif source_session.source == SessionSource.user and destination_session.source == SessionSource.three_sensor and destination_session.sport_name == SportName.distance_running:
            destination_session.sport_name = source_session.sport_name
            destination_session.sport_type = source_session.sport_type
        elif source_session.source == SessionSource.health and destination_session.source in [SessionSource.health, SessionSource.user_health]:
            if source_session.calories is None and destination_session.calories is not None:
                pass
            elif source_session.calories is not None and destination_session.calories is None:
                destination_session.sport_name = source_session.sport_name
                destination_session.sport_type = source_session.sport_type
            elif source_session.calories is not None and source_session.calories >= 0 and destination_session.calories is not None and destination_session.calories >= 0:
                if source_session.calories > destination_session.calories:
                    destination_session.sport_name = source_session.sport_name
                    destination_session.sport_type = source_session.sport_type
                else:
                    pass

        return destination_session






