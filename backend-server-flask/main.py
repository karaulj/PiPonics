import sys, os
import json
import threading
from flask import (
    Flask, request, make_response
)
from http import (
    HTTPStatus
)
from http_utils import (
    HTTPHeaders, HTTPHeaderValues
)
import entity_utils as eu
import db_helper

sem = None          # Static Entity Manager object
dal = None          # Data Access Layer object
ioc = None          # IO Controller object
app = Flask(__name__)

""" ADMIN METHODS """

@app.route('/test', methods=["GET"])
def test_endpoint():
    return 'success'
@app.route('/shutdown', methods=['GET', 'POST'])
def shutdown():
    shutdown_func = request.environ.get('werkzeug.server.shutdown')
    if shutdown_func is None:
        raise RuntimeError('Not running with the Werkzeug Server; cannot shut down server.')
    shutdown_func()
    return 'Shutting down server...'

""" SYSTEM API METHODS """

@app.route('/system/all', methods=["GET"])
def get_all_systems():
    return_val = sem.get_all_systems()
    # set response
    headers = {}
    if return_val == eu.ERR_UNKNOWN:
        return_val = eu.ERR_UNKNOWN_MSG
        status = HTTPStatus.INTERNAL_SERVER_ERROR
        headers[HTTPHeaders.CONTENT_TYPE] = HTTPHeaderValues.TEXT_PLAIN
    elif return_val == eu.ERR_ENTITY_NOT_EXISTS:
        return_val = eu.ERR_ENTITY_NOT_EXISTS_MSG
        status = HTTPStatus.BAD_REQUEST
        headers[HTTPHeaders.CONTENT_TYPE] = HTTPHeaderValues.TEXT_PLAIN
    elif return_val == eu.ERR_BAD_PARAM:
        return_val = eu.ERR_BAD_PARAM_MSG
        status = HTTPStatus.NOT_ACCEPTABLE
        headers[HTTPHeaders.CONTENT_TYPE] = HTTPHeaderValues.TEXT_PLAIN
    else:
        status = HTTPStatus.OK
        headers[HTTPHeaders.CONTENT_TYPE] = HTTPHeaderValues.APPLICATION_JSON
    response = make_response(return_val, status)
    for header, header_val in headers.items():
        response.headers[header] = header_val
    return response

""" TANK API METHODS """

@app.route('/tank/all', methods=["GET"])
def get_all_tanks():
    # get parameters
    system_uuid = request.args.get(HTTPHeaders.API_UUID)
    if system_uuid is None:
        return_val = eu.ERR_MISSING_PARAM
    else:
        return_val = sem.get_tanks_from_uuid(system_uuid)
    # set response
    headers = {}
    if return_val == eu.ERR_UNKNOWN:
        return_val = eu.ERR_UNKNOWN_MSG
        status = HTTPStatus.INTERNAL_SERVER_ERROR
        headers[HTTPHeaders.CONTENT_TYPE] = HTTPHeaderValues.TEXT_PLAIN
    elif return_val == eu.ERR_ENTITY_NOT_EXISTS:
        return_val = eu.ERR_ENTITY_NOT_EXISTS_MSG
        status = HTTPStatus.BAD_REQUEST
        headers[HTTPHeaders.CONTENT_TYPE] = HTTPHeaderValues.TEXT_PLAIN
    elif return_val == eu.ERR_MISSING_PARAM:
        return_val = eu.ERR_MISSING_PARAM_MSG
        status = HTTPStatus.BAD_REQUEST
        headers[HTTPHeaders.CONTENT_TYPE] = HTTPHeaderValues.TEXT_PLAIN
    elif return_val == eu.ERR_BAD_PARAM:
        return_val = eu.ERR_BAD_PARAM_MSG
        status = HTTPStatus.NOT_ACCEPTABLE
        headers[HTTPHeaders.CONTENT_TYPE] = HTTPHeaderValues.TEXT_PLAIN
    else:
        status = HTTPStatus.OK
        headers[HTTPHeaders.CONTENT_TYPE] = HTTPHeaderValues.APPLICATION_JSON
    response = make_response(return_val, status)
    for header, header_val in headers.items():
        response.headers[header] = header_val
    return response

""" CROP API METHODS """

@app.route('/crop/all', methods=["GET"])
def get_all_crops():
    # get parameters
    system_uuid = request.args.get(HTTPHeaders.API_UUID)
    if system_uuid is None:
        return_val = eu.ERR_MISSING_PARAM
    else:
        return_val = sem.get_crops_from_uuid(system_uuid)
    # set response
    headers = {}
    if return_val == eu.ERR_UNKNOWN:
        return_val = eu.ERR_UNKNOWN_MSG
        status = HTTPStatus.INTERNAL_SERVER_ERROR
        headers[HTTPHeaders.CONTENT_TYPE] = HTTPHeaderValues.TEXT_PLAIN
    elif return_val == eu.ERR_ENTITY_NOT_EXISTS:
        return_val = eu.ERR_ENTITY_NOT_EXISTS_MSG
        status = HTTPStatus.BAD_REQUEST
        headers[HTTPHeaders.CONTENT_TYPE] = HTTPHeaderValues.TEXT_PLAIN
    elif return_val == eu.ERR_MISSING_PARAM:
        return_val = eu.ERR_MISSING_PARAM_MSG
        status = HTTPStatus.BAD_REQUEST
        headers[HTTPHeaders.CONTENT_TYPE] = HTTPHeaderValues.TEXT_PLAIN
    elif return_val == eu.ERR_BAD_PARAM:
        return_val = eu.ERR_BAD_PARAM_MSG
        status = HTTPStatus.NOT_ACCEPTABLE
        headers[HTTPHeaders.CONTENT_TYPE] = HTTPHeaderValues.TEXT_PLAIN
    else:
        status = HTTPStatus.OK
        headers[HTTPHeaders.CONTENT_TYPE] = HTTPHeaderValues.APPLICATION_JSON
    response = make_response(return_val, status)
    for header, header_val in headers.items():
        response.headers[header] = header_val
    return response

""" ACTUATOR API METHODS """

@app.route('/actuator/all', methods=["GET"])
def get_all_actuators():
    # get parameters
    tank_or_crop_uuid = request.args.get(HTTPHeaders.API_UUID)
    if tank_or_crop_uuid is None:
        return_val = eu.ERR_MISSING_PARAM
    else:
        return_val = sem.get_actuators_from_uuid(tank_or_crop_uuid)
    # set response
    headers = {}
    if return_val == eu.ERR_UNKNOWN:
        return_val = eu.ERR_UNKNOWN_MSG
        status = HTTPStatus.INTERNAL_SERVER_ERROR
        headers[HTTPHeaders.CONTENT_TYPE] = HTTPHeaderValues.TEXT_PLAIN
    elif return_val == eu.ERR_ENTITY_NOT_EXISTS:
        return_val = eu.ERR_ENTITY_NOT_EXISTS_MSG
        status = HTTPStatus.BAD_REQUEST
        headers[HTTPHeaders.CONTENT_TYPE] = HTTPHeaderValues.TEXT_PLAIN
    elif return_val == eu.ERR_MISSING_PARAM:
        return_val = eu.ERR_MISSING_PARAM_MSG
        status = HTTPStatus.BAD_REQUEST
        headers[HTTPHeaders.CONTENT_TYPE] = HTTPHeaderValues.TEXT_PLAIN
    elif return_val == eu.ERR_BAD_PARAM:
        return_val = eu.ERR_BAD_PARAM_MSG
        status = HTTPStatus.NOT_ACCEPTABLE
        headers[HTTPHeaders.CONTENT_TYPE] = HTTPHeaderValues.TEXT_PLAIN
    else:
        status = HTTPStatus.OK
        headers[HTTPHeaders.CONTENT_TYPE] = HTTPHeaderValues.APPLICATION_JSON
    response = make_response(return_val, status)
    for header, header_val in headers.items():
        response.headers[header] = header_val
    return response

""" SENSOR API METHODS """

@app.route('/sensor/all', methods=["GET"])
def get_all_sensors():
    # get parameters
    tank_or_crop_uuid = request.args.get(HTTPHeaders.API_UUID)
    if tank_or_crop_uuid is None:
        return_val = eu.ERR_MISSING_PARAM
    else:
        return_val = sem.get_sensors_from_uuid(tank_or_crop_uuid)
    # set response
    headers = {}
    if return_val == eu.ERR_UNKNOWN:
        return_val = eu.ERR_UNKNOWN_MSG
        status = HTTPStatus.INTERNAL_SERVER_ERROR
        headers[HTTPHeaders.CONTENT_TYPE] = HTTPHeaderValues.TEXT_PLAIN
    elif return_val == eu.ERR_ENTITY_NOT_EXISTS:
        return_val = eu.ERR_ENTITY_NOT_EXISTS_MSG
        status = HTTPStatus.BAD_REQUEST
        headers[HTTPHeaders.CONTENT_TYPE] = HTTPHeaderValues.TEXT_PLAIN
    elif return_val == eu.ERR_MISSING_PARAM:
        return_val = eu.ERR_MISSING_PARAM_MSG
        status = HTTPStatus.BAD_REQUEST
        headers[HTTPHeaders.CONTENT_TYPE] = HTTPHeaderValues.TEXT_PLAIN
    elif return_val == eu.ERR_BAD_PARAM:
        return_val = eu.ERR_BAD_PARAM_MSG
        status = HTTPStatus.NOT_ACCEPTABLE
        headers[HTTPHeaders.CONTENT_TYPE] = HTTPHeaderValues.TEXT_PLAIN
    else:
        status = HTTPStatus.OK
        headers[HTTPHeaders.CONTENT_TYPE] = HTTPHeaderValues.APPLICATION_JSON
    response = make_response(return_val, status)
    for header, header_val in headers.items():
        response.headers[header] = header_val
    return response


def start_api_server(description_file:str, flask_host:str='127.0.0.1', flask_port:str='5000'):
    flask_thread = None
    stop_thr_event = None
    uart_rx_thread = None
    try:
        global sem
        global dal
        global ioc
        # init sem
        if description_file is not None:
            print("Warning: No description file provided.")
            sem = eu.StaticEntityManger(description_file)
        # init dal
        do_dal_init = True
        dal_env_vars = [
            "POSTGRES_DB",
            "POSTGRES_HOST",
            "POSTGRES_PORT",
            "POSTGRES_USER",
            "POSTGRES_PASSWORD"
        ]
        for env_var in dal_env_vars:
            if os.getenv(env_var) == '':
                do_dal_init = False
            print(os.getenv(env_var))
        if do_dal_init:
            print(os.getenv('POSTGRES_HOST')=='127.0.0.1')
            dal = db_helper.DataAccessLayer(
                dbname = os.getenv('POSTGRES_DB'),
                user = os.getenv('POSTGRES_USER'),
                password = os.getenv('POSTGRES_PASSWORD'),
                host = os.getenv('POSTGRES_HOST'),
                #host = '192.168.254.28',
                #host = 'http://127.0.0.1',
                port = os.getenv('POSTGRES_PORT'),
            )
        ioc = None

        flask_thread = threading.Thread(target=app.run, args=(flask_host, flask_port))
        flask_thread.start()
        """
        stop_thr_event = threading.Event()
        uart_rx_thread = threading.Thread(target=, args=(stop_thr_event,))
        uart_rx_thread.start()
        """
    except:
        print("An error occurred while trying to start the backend API server.")
        if uart_rx_thread is not None and stop_thr_event is not None:
            # stop uart rx thread 'peacefully'
            stop_thr_event.set()
        raise


if __name__ == "__main__":
    #os.listdir('/home')
    if os.getenv('DESCRIPTION_FILE') != '':
        description_file = "/common/{}".format(os.getenv('DESCRIPTION_FILE'))
    else:
        print("Error: DESCRIPTION_FILE environment variable not set.")
        sys.exit(1)
    # start server
    if os.getenv('API_PORT') != '':
        start_api_server(description_file, flask_host='0.0.0.0', flask_port=os.getenv('API_PORT'))
    else:
        print("API_PORT environment variable not set. Using default port")
        start_api_server(description_file, flask_host='0.0.0.0')
