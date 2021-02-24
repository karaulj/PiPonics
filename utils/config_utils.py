import os, sys
import logging
import json

KEY_UUID = "uuid"
KEY_NAME = "name"
KEY_NICE_NAME = "nice_name"
KEY_TYPE = "type"

KEY_SYSTEM = "system"
KEY_SYSTEMS = "systems"

KEY_TANK_OR_CROP = "tank_or_crop"

KEY_TANK = "tank"
KEY_TANKS = "tanks"

KEY_CROP = "crop"
KEY_CROPS = "crops"

#KEY_SENSOR = "sensor"
KEY_SENSORS = "sensors"
KEY_SENSORS_UNITS = "units"
KEY_SENSOR_ID = "sensor_id"

#KEY_ACTUATOR = "actuator"
KEY_ACTUATORS = "actuators"
KEY_ACTUATOR_DRIVE_TYPE = "drive_with"
KEY_ACTUATOR_ID = "actuator_id"

KEY_METADATA = "metadata"
KEY_METADATA_SENSORS = "sensors"
KEY_METADATA_SENSORS_ID = "sensor_id"
KEY_METADATA_SENSORS_UNITS = "units"
KEY_METADATA_SENSORS_SQL_DATATYPE = "sql_data_type"

# container type to container type singular lookup
CONTAINER_TYPES = {
    KEY_TANKS: KEY_TANK,
    KEY_CROPS: KEY_CROP
}

# init logging
logger = logging.getLogger(__name__)

s_handler = logging.StreamHandler()
s_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] %(name)s [%(levelname)s] %(message)s')
s_handler.setFormatter(formatter)

logger.addHandler(s_handler)
logger.setLevel(logging.DEBUG)


def get_json_file_contents(json_file:str) -> dict:
    try:
        with open(json_file, 'r') as f:
            entity_data = json.load(f)
        logger.debug("File '{}' parsed successfully".format(json_file))
        return entity_data
    except IsADirectoryError:
        logger.exception("'{}' is a directory. Ensure env var is set, if any.".format(description_file))
        raise
    except IOError:
        logger.exception("File '{}' not found.".format(json_file))
        raise
    except json.decoder.JSONDecodeError:
        logger.exception("Could not decode json document at '{}'.".format(json_file))
        raise
    except Exception as e:
        logger.exception("Unknown exception occured.")
        raise
    return None


def get_sensor_sql_data_type(json_data:dict, sensor_type:str) -> str:
    try:
        sensor_list = json_data[KEY_METADATA][KEY_METADATA_SENSORS]
        for sensor in sensor_list:
            if sensor[KEY_TYPE] == sensor_type:
                return sensor[KEY_METADATA_SENSORS_SQL_DATATYPE]
        return "FLOAT"
    except:
        return "FLOAT"


def get_sensor_units(json_data:dict, sensor_type:str) -> str:
    try:
        sensor_list = json_data[KEY_METADATA][KEY_METADATA_SENSORS]
        for sensor in sensor_list:
            if sensor[KEY_TYPE] == sensor_type:
                return sensor[KEY_METADATA_SENSORS_UNITS]
        return None
    except:
        return None


def get_default_system_name(*args, **kwargs):
    return 'sys{}'.format(args[0])

def get_default_tank_name(*args, **kwargs):
    return 'tank{}'.format(args[0])

def get_default_crop_name(*args, **kwargs):
    return 'crop{}'.format(args[0])

def get_default_container_name(*args, **kwargs):
    container_type = args[0]
    container_no = args[1]
    if container_type == KEY_TANKS:
        return get_default_tank_name(container_no)
    elif container_type == KEY_CROPS:
        return get_default_crop_name(container_no)
    else:
        raise Exception("Unknown container type: '{}'".format(container_type))

def get_default_sensor_name(*args, **kwargs):
    return '{}'.format(args[0])

def get_default_actuator_name(*args, **kwargs):
    return '{}'.format(args[0])
