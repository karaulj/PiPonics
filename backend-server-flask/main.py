import os
from flask import (
    Blueprint, request
)


KEY_ID = 'id'


api = Blueprint('api', __name__, url_prefix='/api')


@api.route('/echo', methods=('GET'))
def hello_world():
    return 'Hello, World!'


@api.route('/system/all', methods=('GET'))
def get_all_systems():
    id = request.args.get(KEY_ID)
    
