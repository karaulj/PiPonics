import sys, os
import logging
import json
import threading
from flask import (
    Flask, request, make_response
)
from http import (
    HTTPStatus
)
from http_utils import (
    HTTPHeaders, HTTPHeaderValues, APIParams
)
import entity_utils as eu
import db_utils as dbu
import db_helper as dbh

logger = logging.getLogger(__name__)
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
    system_uuid = request.args.get(APIParams.UUID)
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
    system_uuid = request.args.get(APIParams.UUID)
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
    tank_or_crop_uuid = request.args.get(APIParams.UUID)
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
    tank_or_crop_uuid = request.args.get(APIParams.UUID)
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
@app.route('/sensor/data', methods=["GET"])
def get_sensor_data():
    # get parameters
    sensor_uuid = request.args.get(APIParams.UUID)
    if sensor_uuid is None:
        return_val = eu.ERR_MISSING_PARAM
    else:
        sensor_item = sem.get_sensor_item_from_uuid(sensor_uuid)
        start_time = request.args.get(APIParams.START_TIME) # assume None is default
        end_time = request.args.get(APIParams.END_TIME)     # assume None is default
        try:
            return_val = dal.get_sensor_data(sensor_item, start_time, end_time)
        except AttributeError:
            if dal is None:
                app.logger.error('DAL has not been initialized.')
                return_val = dbh.ERR_DAL_NOT_INITIALIZED
            else:
                raise
    # set response
    headers = {}
    if return_val == eu.ERR_MISSING_PARAM:
        return_val = eu.ERR_MISSING_PARAM_MSG
        status = HTTPStatus.BAD_REQUEST
        headers[HTTPHeaders.CONTENT_TYPE] = HTTPHeaderValues.TEXT_PLAIN
    elif return_val == dbh.ERR_DAL_NOT_INITIALIZED:
        return_val = dbh.ERR_DAL_NOT_INITIALIZED_MSG
        status = HTTPStatus.INTERNAL_SERVER_ERROR
        headers[HTTPHeaders.CONTENT_TYPE] = HTTPHeaderValues.TEXT_PLAIN
    elif return_val == dbh.ERR_BAD_SENSOR_PARAM:
        return_val = dbh.ERR_BAD_SENSOR_PARAM_MSG
        status = HTTPStatus.BAD_REQUEST
        headers[HTTPHeaders.CONTENT_TYPE] = HTTPHeaderValues.TEXT_PLAIN
    elif return_val == dbh.ERR_BAD_START_TIME_PARAM:
        return_val = dbh.ERR_BAD_START_TIME_PARAM_MSG
        status = HTTPStatus.BAD_REQUEST
        headers[HTTPHeaders.CONTENT_TYPE] = HTTPHeaderValues.TEXT_PLAIN
    elif return_val == dbh.ERR_BAD_END_TIME_PARAM:
        return_val = dbh.ERR_BAD_END_TIME_PARAM_MSG
        status = HTTPStatus.BAD_REQUEST
        headers[HTTPHeaders.CONTENT_TYPE] = HTTPHeaderValues.TEXT_PLAIN
    else:
        status = HTTPStatus.OK
        headers[HTTPHeaders.CONTENT_TYPE] = HTTPHeaderValues.APPLICATION_JSON
    response = make_response(return_val, status)
    for header, header_val in headers.items():
        response.headers[header] = header_val
    return response


def start_api_server(do_sem_init:bool=True, do_dal_init:bool=True, do_ioc_init:bool=True, flask_host:str='127.0.0.1', flask_port:str='5000'):
    flask_thread = None
    stop_thr_event = None
    uart_rx_thread = None
    try:
        global sem
        global dal
        global ioc
        # init sem
        if do_sem_init:
            description_file = os.getenv('DESCRIPTION_FILE')
            if description_file == '' or description_file is None:
                print("Error: DESCRIPTION_FILE environment variable not set.")
                sys.exit(1)
            else:
                description_file = "/common/{}".format(description_file)
            sem = eu.StaticEntityManger(description_file)
        # init dal
        if do_dal_init:
            pg_dbname = os.getenv('POSTGRES_DB')
            if pg_dbname == '' or pg_dbname is None:
                print("POSTGRES_DB environment variable not set.")
                pg_dbname = 'postgres'
            pg_user = os.getenv('POSTGRES_USER')
            if pg_user == '' or pg_user is None:
                print("POSTGRES_USER environment variable not set.")
                pg_user = 'postgres'
            pg_password = os.getenv('POSTGRES_PASSWORD')
            if pg_password == '' or pg_password is None:
                print("POSTGRES_PASSWORD environment variable not set.")
                pg_password = 'postgres'
            pg_host = os.getenv("POSTGRES_HOST")
            if pg_host == '' or pg_host is None:
                print("POSTGRES_HOST environment variable is not set.")
                pg_host = '127.0.0.1'
                print("Skipping dal init")
            pg_port = os.getenv("POSTGRES_PORT")
            if pg_port == '' or pg_port is None:
                print("POSTGRES_PORT environment variable is not set.")
                pg_port = '5432'
            dal = dbh.DataAccessLayer(
                dbname = pg_dbname,
                user = pg_user,
                password = pg_password,
                host = pg_host,
                port = pg_port
            )
        # init ioc
        if do_ioc_init:
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
            stop_thr_event.set()
        if dal is not None:
            dal.shutdown()
        raise


def _init_logging():
    formatter = logging.Formatter('[%(asctime)s] %(name)s [%(levelname)s] %(message)s')

    s_handler = logging.StreamHandler()
    s_handler.setLevel(logging.DEBUG)
    s_handler.setFormatter(formatter)

    global logger
    logger.addHandler(s_handler)
    logger.setLevel(logging.DEBUG)
    logger.debug('Finished logger setup for main')

    app.logger.addHandler(s_handler)
    app.logger.setLevel(logging.INFO)


if __name__ == "__main__":
    #os.listdir('/home')
    _init_logging()
    # start server
    backend_port = os.getenv('BACKEND_PORT')
    if backend_port != '' and backend_port is not None:
        start_api_server(flask_host='0.0.0.0', flask_port=backend_port)
    else:
        print("BACKEND_PORT environment variable not set. Using default port")
        start_api_server(flask_host='0.0.0.0')
