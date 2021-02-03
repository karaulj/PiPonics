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


def get_config_file_json_contents(json_file:str) -> dict:
    json_data = None
    try:
        with open(json_file, 'r') as f:
            json_data = json.load(f)
        print("Got json data from {}".format(json_file))
        #print("Json data: {}\n".format(json.dumps(json_data, indent=2)))
    except IOError:
        print("Config file " + json_file + " not found. Ensure CONFIG_FILE variable is set in .env file.")
        raise
    except json.decoder.JSONDecodeError:
        print("Could not decode json document. Refer to sample config.json")
        raise
    except:
        print("Unknown Error occured during json document decoding.")
        raise

    return json_data


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
