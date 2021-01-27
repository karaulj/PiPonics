import os
import sys
#import logging
import time
import json


KEY_SYSTEMS = "systems"
KEY_SYSTEMS_NAME = "name"

KEY_TANKS = "tanks"
KEY_TANKS_SENSORS = "sensors"

KEY_CROPS = "crops"
KEY_CROPS_ACTUATORS = "actuators"

KEY_NAME = "name"
KEY_NICE_NAME = "nice_name"
KEY_TYPE = "type"
KEY_MAIN_FLAG = "main"


def init_logging():
    logging_fmt = '[%(asctime)s] %(filename)s [%(levelname)s] %(message)s'
    #filename = "/logs/" + time.strftime("%y-%m-%d_%H:%M:%S") + "_db-setup.log"
    filename = "/logs/db-setup.log"
    #logging.basicConfig(filename=filename, filemode='a', format=logging_fmt, level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logFormatter = logging.Formatter(logging_fmt)
    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)


def get_sql_schema_create_str(schema_name):
    return """
DROP SCHEMA IF EXISTS {0};
CREATE SCHEMA {0};
""".format(schema_name)


def get_sql_table_create_str(table_name):
    return ""



def get_config_file_json_contents():
    json_data = None
    try:
        config_path = '/home/{}'.format(os.getenv('CONFIG_FILE'))
        with open(config_path, 'r') as f:
            json_data = json.load(f)
        print("Got json data from {}".format(config_path))
        print("Json data: {}\n".format(json.dumps(json_data)))
    except IOError:
        print("Config file " + config_path + " not found. Ensure CONFIG_FILE is set in .env file.")
        raise
    except JSONDecodeError:
        print("Could not decode json document. Refer to sample config.json")
        raise
    except:
        print("Unknown Error occured")
        raise

    return json_data


def generate_sql_script(json_data):
    if json_data is None:
        print("Internal Error: Json data is null. Exiting")
        sys.exit(1)
    json_data_orig = json_data

    f_contents = []
    f_contents.append("--Ponics Database Init Script (auto-generated)\n\n")

    # find systems
    try:
        systems = json_data[KEY_SYSTEMS]
    except KeyError:
        print("No {} key found in config file".format(KEY_SYSTEMS))
        return ""

    for i, system in enumerate(systems):
        # get system name
        try:
            sys_name = system[KEY_NAME]
        except KeyError:
            sys_name = "sys{}".format(i+1)
        print("Found system: '{}'".format(sys_name))

        # find tanks
        try:
            tanks = system[KEY_TANKS]
        except KeyError:
            print("No tanks found for system '{}'".format(sys_name))
            continue

        # iterate through tanks in system
        for j, tank in enumerate(tanks):
            # get tank name
            try:
                tank_name = "{}_{}".format(sys_name, tank[KEY_NAME])
            except KeyError:
                tank_name = "{}_tank{}".format(sys_name, j+1)
            print("Found tank: '{}'".format(tank_name))

            # find sensors
            try:
                sensors = tank[KEY_TANKS_SENSORS]
            except KeyError:
                print("No sensors found for tank '{}'".format(tank_name))
                continue

            # create schema for tank
            f_contents.append(get_sql_schema_create_str(tank_name))

            # iterate through sensors in tank
            for k, sensor in enumerate(sensors):
                # get sensor type
                try:
                    sensor_type = sensor[KEY_TYPE]
                except KeyError:
                    print("No sensor 'type' property found for {}, sensor {}".format(tank_name, k+1))
                    continue
                # get sensor name
                try:
                    sensor_name = sensor[KEY_NAME]
                except KeyError:
                    sensor_name = "sensor_{}".format(sensor_type)

                # create table for sensor
                f_contents.append(get_sql_table_create_str(sensor_name))





    json_data = json_data_orig
    print(json_data["systems"])
    print(json_data["systems"][0]["name"])
    print(json_data["systems"][0]["tanks"])
    print(json_data["systems"][0]["tanks"][0])
    print(json_data["systems"][0]["tanks"][0]["name"])
    print(json_data["systems"][0]["crops"])
    print(json_data["systems"][0]["crops"][0])
    print(json_data["systems"][0]["crops"][0]["name"])

    sql_script_file = '/sql/db-init.sql'
    with open(sql_script_file, 'w') as f:
        f.writelines(f_contents)
    print("\nFULL SQL SCRIPT OUTPUT:")
    print(''.join(f_contents))

    print("Wrote db init sql script to {}".format(sql_script_file))
    return sql_script_file


def main():
    #print([f for f in os.listdir('/home')])
    json_contents = get_config_file_json_contents()
    sql_file = generate_sql_script(json_contents)
    return sql_file


if __name__ == "__main__":
    print("Starting db init sql script generation")
    #init_logging()
    main()
    print("db init finished successfully")
    sys.exit(0)
