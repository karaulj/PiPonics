import sys, os
import json
from flask import (
    Flask, request, make_response
)
from http import (
    HTTPStatus
)
import entity_utils as eu


DEFAULT_HEADERS = {}


sem = None

app = Flask(__name__)

"""
@app.before_first_request
def api_init():
    print("in api init")
    #import config_helper as ch
    description_file = "/home/{}".format(os.getenv('DESCRIPTION_FILE'))
    entity_data = ch.get_json_file_contents(description_file)
"""

@app.route('/echo', methods=["GET"])
def hello_world():
    return 'Hello, World!'

@app.route('/all', methods=["GET"])
def get_entity_data():
    return '{}'.format(json.dumps(sem._data, indent=2))

@app.route('/system/all', methods=["GET"])
def get_all_systems():
    return_val = sem.get_all_systems()
    if return_val == eu.ERR_UNKNOWN:
        status = HTTPStatus.INTERNAL_SERVER_ERROR
    elif return_val == eu.ERR_ENTITY_NOT_EXISTS:
        status = HTTPStatus.BAD_REQUEST
    elif return_val == eu.ERR_BAD_PARAM:
        status = HTTPStatus.NOT_ACCEPTABLE
    else:
        status = HTTPStatus.OK
    response = make_response(return_val, status)
    return response


if __name__ == "__main__":
    #os.listdir('/home')
    try:
        description_file = "/common/{}".format(os.getenv('DESCRIPTION_FILE'))
        sem = eu.StaticEntityManger(description_file)
        app.run(host='0.0.0.0')
    except:
        "An error occurred while trying to start the backend API server."
        raise
