

class HTTPHeaders:
    CONTENT_TYPE = "Content-Type"
    ALLOW_ORIGIN = "Access-Control-Allow-Origin"

class HTTPHeaderValues:
    APPLICATION_JSON = "application/json"
    TEXT_PLAIN = "text/plain"
    TEXT_HTML = "text/html"
    ORIGIN_ANYWHERE = "*"


class APIParams:
    UUID = "uuid"
    START_TIME = "startTime"
    END_TIME = "endTime"
    SENSOR_READING_TIME = "t"
    SENSOR_READING_VALUE = "v"
    ACTUATOR_DRIVE_VALUE = "value"


class APIErrors(object):

    _err_no = -1000

    # General
    ERR_UNKNOWN = _err_no-1
    ERR_UNKNOWN_MSG = "An internal server error occurred and your request could not be completed."
    ERR_MISSING_PARAM = _err_no-2
    ERR_MISSING_PARAM_MSG = "The request is missing a required parameter."
    # UUID errors
    ERR_ENTITY_NOT_EXISTS = _err_no-3
    ERR_ENTITY_NOT_EXISTS_MSG = "The requested entity does not exist."
    # Param format errors
    ERR_BAD_PARAM = _err_no-4
    ERR_BAD_PARAM_MSG = "The provided parameter has an incorrect format."
    # db_helper
    ERR_BAD_SENSOR_PARAM = _err_no-5
    ERR_BAD_SENSOR_PARAM_MSG = "The referenced sensor item is missing or invalid."
    ERR_BAD_START_TIME_PARAM = _err_no-6
    ERR_BAD_START_TIME_PARAM_MSG = "The provided start time is missing or invalid."
    ERR_BAD_END_TIME_PARAM = _err_no-7
    ERR_BAD_END_TIME_PARAM_MSG = "The provided end time is missing or invalid."
    ERR_START_AFTER_END = _err_no-8
    ERR_START_AFTER_END_MSG = "The provided start time must be equal to or less than end time."
    ERR_DAL_NOT_INITIALIZED = _err_no-9
    ERR_DAL_NOT_INITIALIZED_MSG = "No database connection was found."
    ERR_BAD_READING_PARAM = _err_no-10
    ERR_BAD_READING_PARAM_MSG = "The provided sensor reading is missing or invalid."
    # io_controller
    ERR_BAD_ACTUATOR_PARAM = _err_no-11
    ERR_BAD_ACTUATOR_PARAM_MSG = "The referenced actuator is missing or invalid."
    ERR_BAD_DRIVE_VAL_PARAM = _err_no-12
    ERR_BAD_DRIVE_VAL_PARAM_MSG = "The provided drive value is invalid."
    ERR_IOC_NOT_INITIALIZED = _err_no-13
    ERR_IOC_NOT_INITIALIZED_MSG = "No sensor board connection was found."
