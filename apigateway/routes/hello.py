from flask import Blueprint

app = Blueprint('hello', __name__)


@app.route('/world', methods=['GET'])
def handle_misc_uuid():
    return {'message': 'Hello world!!!'}
