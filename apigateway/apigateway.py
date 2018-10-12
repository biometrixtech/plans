from fathomapi.api.handler import handler as fathom_handler
from fathomapi.api.flask_app import app


from routes.active_recovery import app as active_recovery_routes
from routes.athlete import app as athlete_routes
from routes.athlete_season import app as athlete_season_routes
from routes.daily_plan import app as daily_plan_routes
from routes.daily_readiness import app as daily_readiness_routes
from routes.daily_schedule import app as daily_schedule_routes
from routes.functional_strength import app as functional_strength_routes
from routes.misc import app as misc_routes
from routes.post_session_survey import app as post_session_survey_routes
from routes.session import app as add_delete_session_routes
from routes.weekly_schedule import app as weekly_schedule_routes
app.register_blueprint(active_recovery_routes, url_prefix='/active_recovery')
app.register_blueprint(add_delete_session_routes, url_prefix='/session')
app.register_blueprint(athlete_routes, url_prefix='/athlete')
app.register_blueprint(athlete_season_routes, url_prefix='/athlete_season')
app.register_blueprint(daily_plan_routes, url_prefix='/daily_plan')
app.register_blueprint(daily_readiness_routes, url_prefix='/daily_readiness')
app.register_blueprint(daily_schedule_routes, url_prefix='/schedule')
app.register_blueprint(functional_strength_routes, url_prefix='/functional_strength')
app.register_blueprint(misc_routes, url_prefix='/misc')
app.register_blueprint(post_session_survey_routes, url_prefix='/post_session_survey')
app.register_blueprint(weekly_schedule_routes, url_prefix='/weekly_schedule')


def handler(event, context):
    return fathom_handler(event, context)


if __name__ == '__main__':
    app.run(debug=True)
