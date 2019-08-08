from flask import request, Blueprint
from fathomapi.utils.decorators import require
from fathomapi.utils.xray import xray_recorder


app = Blueprint('three_sensor', __name__)


@app.route('/biomechanics_detail', methods=['POST'])
@require.authenticated.any
# @require.body({'event_date': str})
@xray_recorder.capture('routes.three_sensor.get')
def handle_biomechanics_detail_get(principal_id=None):
    # user_id = principal_id
    # event_date = request.json['event_date']

    return {'sessions': fake_biomechanics_detail_data()}, 200


def fake_biomechanics_detail_data():
    import random
    durations = [54, 95, 170, 53, 30]
    sessions = []
    for i in range(5):
        duration = durations[i]
        detail_data = []
        for j in range(duration):
            if j < 2:
                block_detail = {
                    'x': j,
                    'y1': 0.0,
                    'y2': 0.0,
                    'flag': 0
                }
            elif int(duration * .2) < j < int(duration * .3) or int(duration * .75) < j < int(duration * .8):
                block_detail = {
                    'x': j,
                    'y1': 0.0,
                    'y2': 0.0,
                    'flag': 0
                }
            elif int(duration * .4) < j < int(duration * .6) or int(duration * .85) < j < int(duration * .9):
                block_detail = {
                    'x': j,
                    'y1': round(random.random() * 10, 2),
                    'y2': round(random.random() * -10, 2),
                    'flag': 0
                }
            else:
                block_detail = {
                    'x': j,
                    'y1': round(random.random() * 10, 2),
                    'y2': round(random.random() * -10, 2),
                    'flag': 1
                }
            detail_data.append(block_detail)

        session = {
            'session_id': f'session{i}',
            'asymmetry': {
                'apt': {
                    'detail_legend': [
                        {
                            'color': [8, 9],
                            'text': 'No Asymmetry Identified',
                        },
                        {
                            'color': [1, 4],
                            'text': 'Significant Asymmetry Identified',
                        },
                    ],
                    'detail_data': detail_data,
                    'detail_text': {}
                }
            }
        }
        sessions.insert(0, session)

    return sessions
