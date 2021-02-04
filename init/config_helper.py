import os, sys
import json


KEY_SYSTEM = "system"
KEY_SYSTEMS = "systems"
KEY_SYSTEMS_NAME = "name"

KEY_TANK = "tank"
KEY_TANKS = "tanks"
KEY_TANKS_NAME = "name"
KEY_TANKS_NICE_NAME = "nice_name"

KEY_SENSOR = "sensor"
KEY_SENSORS = "sensors"
KEY_SENSORS_NAME = "name"
KEY_SENSORS_TYPE = "type"
KEY_SENSORS_UNITS = "units"

KEY_CROP = "crop"
KEY_CROPS = "crops"
KEY_CROPS_NAME = "name"
KEY_CROPS_NICE_NAME = "nice_name"

KEY_ACTUATOR = "actuator"
KEY_ACTUATORS = "actuators"
KEY_ACTUATORS_NAME = "name"
KEY_ACTUATORS_TYPE = "type"
KEY_ACTUATORS_MAIN = "main"

KEY_METADATA = "metadata"
KEY_METADATA_SENSORS = "sensors"
KEY_METADATA_SENSORS_ID = "sensor_id"
KEY_METADATA_SENSORS_TYPE = "type"
KEY_METADATA_SENSORS_UNITS = "units"
KEY_METADATA_SENSORS_SQL_DATATYPE = "sql_data_type"

KEY_UUID = "uuid"


def get_json_file_contents(json_file:str, print_func=print) -> dict:
    try:
        with open(json_file, 'r') as f:
            entity_data = json.load(f)
        print_func("File '{}' parsed successfully".format(json_file))
        return entity_data
    except IsADirectoryError:
        print_func("Error: '{}' is a directory. Ensure env var is set, if any.".format(description_file))
        sys.exit(1)
    except IOError:
        print_func("Error: File '{}' not found.".format(json_file))
        sys.exit(1)
    except json.decoder.JSONDecodeError:
        print_func("Error: Could not decode json document at '{}'.".format(json_file))
        raise
    except:
        print_func("Error: Unknown exception occured.")
        raise
    return None


def get_default_system_name(*args, **kwargs):
    return 'sys{}'.format(args[0])

def get_default_tank_name(*args, **kwargs):
    return 'tank{}'.format(args[0])

def get_default_crop_name(*args, **kwargs):
    return 'crop{}'.format(args[0])

def get_default_sensor_name(*args, **kwargs):
    return '{}'.format(args[0])

def get_default_actuator_name(*args, **kwargs):
    return '{}'.format(args[0])
