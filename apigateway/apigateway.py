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


def handler(event, context):
    return fathom_handler(event, context)


if __name__ == '__main__':
    app.run(debug=True)
