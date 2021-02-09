import sys, os
import json
import threading
from flask import (
    Flask, request, make_response
)
from http import (
    HTTPStatus
)
from http_const import (
    HTTPHeaders, HTTPHeaderValues
)
import entity_utils as eu

sem = None          # Static Entity Manager object
dal = None          # Data Access Layer object
ioc = None          # IO Controller object
app = Flask(__name__)


@app.route('/test', methods=["GET"])
def hello_world():
    return 'Hello, World!'

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


if __name__ == "__main__":
    #os.listdir('/home')
    flask_thread = None
    stop_thr_event = None
    uart_rx_thread = None
    try:
        description_file = "/common/{}".format(os.getenv('DESCRIPTION_FILE'))
        sem = eu.StaticEntityManger(description_file)
        dal = None
        ioc = None
        """
        stop_thr_event = threading.Event()
        uart_rx_thread = threading.Thread(target=, args=(stop_thr_event,))
        uart_rx_thread.start()
        """
        flask_thread = threading.Thread(target=app.run, args=('0.0.0.0',))
        flask_thread.start()
        #app.run(host='0.0.0.0')
    except:
        "An error occurred while trying to start the backend API server."
        if uart_rx_thread is not None and stop_thr_event is not None:
            # stop uart rx thread 'peacefully'
            stop_thr_event.set()
        raise
