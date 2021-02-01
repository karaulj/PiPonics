from flask import (
    Blueprint, request
)

api = Blueprint('api', __name__, url_prefix='/api')


@api.route('/echo', methods=('GET'))
def hello_world():
    return 'Hello, World!'


@app.route('/test')
def test_endpoint():
    return 'Goodbye Friend'
