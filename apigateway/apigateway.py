from fathomapi.api.handler import handler as fathom_handler
from fathomapi.api.flask_app import app


from routes.active_recovery import app as active_recovery_routes
from routes.athlete import app as athlete_routes
from routes.coach import app as coach_routes
from routes.daily_plan import app as daily_plan_routes
from routes.daily_readiness import app as daily_readiness_routes
from routes.functional_strength import app as functional_strength_routes
from routes.misc import app as misc_routes
from routes.session import app as session_routes
from routes.health_data import app as health_data_routes
from routes.insights import app as insights_routes
from routes.trends import app as trend_routes
from routes.three_sensor import app as three_sensor_routes
from routes.symptoms import app as symptoms_routes
from routes.movement_prep import app as movement_prep_routes
from routes.mobility_wod import app as mobility_wod_routes
from routes.responsive_recovery import app as responsive_recovery_routes
from routes.training_session import app as training_session_routes
from routes.report_symptoms import app as report_symptoms_route

app.register_blueprint(active_recovery_routes, url_prefix='/active_recovery')
app.register_blueprint(session_routes, url_prefix='/session')
app.register_blueprint(athlete_routes, url_prefix='/athlete')
app.register_blueprint(coach_routes, url_prefix='/coach')
app.register_blueprint(daily_plan_routes, url_prefix='/daily_plan')
app.register_blueprint(daily_readiness_routes, url_prefix='/daily_readiness')
app.register_blueprint(functional_strength_routes, url_prefix='/functional_strength')
app.register_blueprint(misc_routes, url_prefix='/misc')
app.register_blueprint(health_data_routes, url_prefix='/health_data')
app.register_blueprint(insights_routes, url_prefix='/insights')
app.register_blueprint(trend_routes, url_prefix='/trends')
app.register_blueprint(three_sensor_routes, url_prefix='/three_sensor')
app.register_blueprint(symptoms_routes, url_prefix='/symptoms')
app.register_blueprint(movement_prep_routes, url_prefix='/movement_prep')
app.register_blueprint(mobility_wod_routes, url_prefix='/mobility_wod')
app.register_blueprint(responsive_recovery_routes, url_prefix='/responsive_recovery')
app.register_blueprint(training_session_routes, url_prefix='/training_session')
app.register_blueprint(report_symptoms_route, url_prefix='/report_symptoms')


def handler(event, context):
    return fathom_handler(event, context)


if __name__ == '__main__':
    app.run(debug=True)
