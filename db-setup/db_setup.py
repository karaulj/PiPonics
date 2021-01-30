import os
import sys
#import logging
import time
import json
#from pypika import Query, Table, Column


KEY_SYSTEMS = "systems"
KEY_SYSTEMS_NAME = "name"

KEY_TANKS = "tanks"
KEY_TANKS_NAME = "name"
KEY_TANKS_NICE_NAME = "nice_name"
KEY_TANKS_SENSORS = "sensors"
KEY_TANKS_SENSORS_NAME = "name"
KEY_TANKS_SENSORS_TYPE = "type"

KEY_CROPS = "crops"
KEY_CROPS_NAME = "name"
KEY_CROPS_NICE_NAME = "nice_name"
KEY_CROPS_ACTUATORS = "actuators"
KEY_CROPS_ACTUATORS_NAME = "name"
KEY_CROPS_ACTUATORS_TYPE = "type"
KEY_CROPS_ACTUATORS_MAIN = "main"

KEY_METADATA = "metadata"
KEY_METADATA_SENSORS = "sensors"
KEY_METADATA_SENSORS_TYPE = "type"
KEY_METADATA_SENSORS_UNITS = "units"
KEY_METADATA_SENSORS_SQL_DATATYPE = "sql_data_type"


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

""" START SQL QUERY HELPER FUNCTIONS """
def get_sql_schema_create_str(schema_name:str) -> str:
    return """
DROP SCHEMA IF EXISTS {0};
CREATE SCHEMA {0};
""".format(schema_name)
def get_sql_table_create_str(schema_name:str, table_name:str, columns:list) -> str:
    return """
CREATE TABLE {0}.{1} (
  {2}
);
""".format(schema_name, table_name, ",\n  ".join(columns))
def get_sql_insert_str(schema_name:str, table_name:str, col_names:list, col_vals:list) -> str:
    return """
INSERT INTO {0}.{1} ({2})
VALUES ({3});
""".format(schema_name, table_name, ", ".join(col_names), ", ".join(col_vals))
""" END SQL QUERY HELPER FUNCTIONS """


def get_sensor_sql_data_type(json_data:dict, sensor_type:str) -> str:
    try:
        sensor_list = json_data[KEY_METADATA][KEY_METADATA_SENSORS]
        for sensor in sensor_list:
            if sensor[KEY_METADATA_SENSORS_TYPE] == sensor_type:
                return sensor[KEY_METADATA_SENSORS_SQL_DATATYPE]
        return None
    except:
        return None


def get_config_file_json_contents(json_file:str) -> dict:
    json_data = None
    try:
        with open(json_file, 'r') as f:
            json_data = json.load(f)
        print("Got json data from {}".format(json_file))
        print("Json data: {}\n".format(json.dumps(json_data)))
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


def generate_metadata_sensor_table_str(json_data:dict) -> str:
    """Return sql script for generating metadata table.

    Keyword arguments:
    json_data -- json object, root of config file (required)
    """

    print("Beginning metadata sensor table creation")

    # find metadata
    try:
        metadata = json_data[KEY_METADATA]
    except KeyError:
        print("No '{}' property found in config file".format(KEY_METADATA))
        return ""

    # find sensors
    try:
        sensors = metadata[KEY_METADATA_SENSORS]
    except KeyError:
        print("No '{}' property found for '{}' object in config file".format(KEY_METADATA_SENSORS, KEY_METADATA))
        return ""

    f_contents = []
    f_contents.append("\n--Ponics Metadata Table Script (auto-generated)\n")
    metadata_schema_created = False

    # iterate through sensors
    for i, sensor in enumerate(sensors):
        # get sensor type
        try:
            sensor_type = "'{}'".format(sensor[KEY_METADATA_SENSORS_TYPE])
        except KeyError:
            print("No '{}' property found for sensor object at '{}', '{}', #{}".format(KEY_METADATA_SENSORS_TYPE, KEY_METADATA, KEY_METADATA_SENSORS, i+1))
            continue
        # get sensor units
        try:
            sensor_units = sensor[KEY_METADATA_SENSORS_UNITS]
            if sensor_units is None:
                sensor_units = "NULL"
            else:
                sensor_units = "'{}'".format(sensor_units)
        except KeyError:
            print("No '{}' property found for sensor object at '{}', '{}', #{}".format(KEY_METADATA_SENSORS_UNITS, KEY_METADATA, KEY_METADATA_SENSORS, i+1))
            continue
        # get sensor sql data type
        try:
            sensor_sql_data_type = "'{}'".format(sensor[KEY_METADATA_SENSORS_SQL_DATATYPE])
        except KeyError:
            print("No '{}' property found for sensor object at '{}', '{}', #{}".format(KEY_METADATA_SENSORS_SQL_DATATYPE, KEY_METADATA, KEY_METADATA_SENSORS, i+1))
            continue

        if not metadata_schema_created:
            # create metadata schema and sensor metadata table
            f_contents.append(get_sql_schema_create_str(KEY_METADATA))
            columns = []
            columns.append("sensor_id SERIAL PRIMARY KEY")
            columns.append("{} VARCHAR NOT NULL".format(KEY_METADATA_SENSORS_TYPE))
            columns.append("{} VARCHAR".format(KEY_METADATA_SENSORS_UNITS))
            columns.append("{} VARCHAR NOT NULL".format(KEY_METADATA_SENSORS_SQL_DATATYPE))
            f_contents.append(get_sql_table_create_str(KEY_METADATA, KEY_METADATA_SENSORS, columns))
            metadata_schema_created = True

        # add row to table
        col_names = [KEY_METADATA_SENSORS_TYPE, KEY_METADATA_SENSORS_UNITS, KEY_METADATA_SENSORS_SQL_DATATYPE]
        col_vals = [sensor_type, sensor_units, sensor_sql_data_type]
        f_contents.append(get_sql_insert_str(KEY_METADATA, KEY_METADATA_SENSORS, col_names, col_vals))


    return ''.join(f_contents)


def generate_db_tables_str(json_data:dict, write_to_file:bool=True) -> str:
    """Return sql script for generating db tables.

    Keyword arguments:
    json_data -- json object, root of config file (required).
    write_to_file -- write tablenames to /common/$TABLENAMES_FILE if True.
    """

    # find systems
    try:
        systems = json_data[KEY_SYSTEMS]
    except KeyError:
        print("No '{}' property found in config file".format(KEY_SYSTEMS))
        return ""   # return blank string for no sql script created

    tablenames = []
    f_contents = []
    f_contents.append("\n--Ponics Database Tables Script (auto-generated)\n")

    # iterate through systems
    for i, system in enumerate(systems):
        # get system name
        try:
            sys_name = system[KEY_SYSTEMS_NAME]
        except KeyError:
            sys_name = "sys{}".format(i+1)
        print("Found system: '{}'".format(sys_name))
        # find tanks
        try:
            tanks = system[KEY_TANKS]
        except KeyError:
            print("No '{}' property found for system '{}'".format(KEY_TANKS, sys_name))
            continue

        # only create system schema if at least one sensor
        sys_schema_created = False

        # iterate through tanks in system
        for j, tank in enumerate(tanks):
            # get tank name
            try:
                tank_name = "{}".format(tank[KEY_TANKS_NAME])
            except KeyError:
                tank_name = "tank{}".format(j+1)
            print("Found tank: '{}'".format(tank_name))
            # find sensors
            try:
                sensors = tank[KEY_TANKS_SENSORS]
            except KeyError:
                print("No '{}' property found for tank '{}'".format(KEY_TANKS_SENSORS, tank_name))
                continue

            # iterate through sensors in tank
            for k, sensor in enumerate(sensors):
                # get sensor type
                try:
                    sensor_type = sensor[KEY_TANKS_SENSORS_TYPE]
                except KeyError:
                    print("No '{}' property found for system '{}', tank '{}', sensor #{}".format(KEY_TANKS_SENSORS_TYPE, sys_name, tank_name, k+1))
                    continue
                # get sensor name
                try:
                    sensor_name = "{}_{}".format(tank_name, sensor[KEY_TANKS_SENSORS_NAME])
                except KeyError:
                    sensor_name = "{}_{}".format(tank_name, sensor_type)

                if not sys_schema_created:
                    # create schema for system (since sensor table exists)
                    f_contents.append(get_sql_schema_create_str(sys_name))
                    sys_schema_created = True

                # create table for sensor
                sensor_datatype = get_sensor_sql_data_type(json_data, sensor_type)
                if sensor_datatype is None:
                    continue

                columns = []
                columns.append("entry_id SERIAL PRIMARY KEY")
                columns.append("timestamp timestamp without time zone DEFAULT LOCALTIMESTAMP")
                columns.append("reading {} NOT NULL".format(sensor_datatype))
                f_contents.append(get_sql_table_create_str(sys_name, sensor_name, columns))
                tablenames.append("{}.{}".format(sys_name, sensor_name))

    # print/write list of tablenames
    print("List of generated tables: {}".format(tablenames))
    if write_to_file:
        with open('/common/{}'.format(os.getenv('TABLENAMES_FILE')), 'w') as f:
            f.write(",".join(tablenames))

    return ''.join(f_contents)


def main(config_file:str, sql_file:str=None) -> str:
    """ Generates an sql file for database initialization and returns the file path. Expects a config json file at /home/$CONFIG_FILE.

    Keyword arguments:
    config_file -- path to config json file (required).
    sql_file -- SQL filename to write to. Omits writing if None (default).
    """
    #print([f for f in os.listdir('/home')])
    json_contents = get_config_file_json_contents(config_file)

    if json_contents is None:
        print("Internal Error: Json data is null. Exiting")
        sys.exit(1)

    db_init_tables_str = generate_db_tables_str(json_contents, write_to_file=True)
    metadata_sensor_table_str = generate_metadata_sensor_table_str(json_contents)
    sql_script_str = db_init_tables_str + metadata_sensor_table_str

    print("\n*** BEGIN FULL SQL SCRIPT ***\n{}\n*** END FULL SQL SCRIPT ***\n".format(sql_script_str))

    if sql_file is not None:
        with open(sql_file, 'w') as f:
            f.write(sql_script_str)
        print("Wrote db init sql script to {}".format(sql_file))
        return sql_file
    else:
        return ''


if __name__ == "__main__":
    """
    import time
    print("starting wait")
    time.sleep(10)
    """
    print("Starting db init sql script generation")
    #init_logging()
    config_file = '/home/{}'.format(os.getenv('CONFIG_FILE'))
    if config_file is None:
        print("Error: CONFIG_FILE environment variable not set. Please specify in .env file.")
        sys.exit(1)
    sql_file = '/sql/{}'.format(os.getenv('DB_INIT_SQL_FILE'))

    main(config_file=config_file, sql_file=sql_file)
    print("db init finished successfully")
    sys.exit(0)
