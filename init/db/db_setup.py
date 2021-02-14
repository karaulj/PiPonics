import os
import sys
import json
import config_utils as ch
import db_utils as dbu


def generate_metadata_sensor_table_str(json_data:dict) -> str:
    """Return sql script for generating metadata table.

    Keyword arguments:
    json_data -- json object, root of config file (required)
    """

    print("Beginning metadata sensor table creation")

    # find metadata
    try:
        metadata = json_data[ch.KEY_METADATA]
    except KeyError:
        print("No '{}' property found in config file".format(ch.KEY_METADATA))
        return ""

    # find sensors
    try:
        sensors = metadata[ch.KEY_METADATA_SENSORS]
    except KeyError:
        print("No '{}' property found for '{}' object in config file".format(ch.KEY_METADATA_SENSORS, ch.KEY_METADATA))
        return ""

    f_contents = []
    f_contents.append("\n--Ponics Metadata Table Script (auto-generated)\n")
    metadata_schema_created = False

    # iterate through sensors
    for i, sensor in enumerate(sensors):
        # get sensor type
        try:
            sensor_type = "'{}'".format(sensor[ch.KEY_TYPE])
        except KeyError:
            print("No '{}' property found for sensor object at '{}', '{}', #{}".format(ch.KEY_TYPE, ch.KEY_METADATA, ch.KEY_METADATA_SENSORS, i+1))
            continue
        # get sensor units
        try:
            sensor_units = sensor[ch.KEY_METADATA_SENSORS_UNITS]
            if sensor_units is None:
                sensor_units = "NULL"
            else:
                sensor_units = "'{}'".format(sensor_units)
        except KeyError:
            print("No '{}' property found for sensor object at '{}', '{}', #{}".format(ch.KEY_METADATA_SENSORS_UNITS, ch.KEY_METADATA, ch.KEY_METADATA_SENSORS, i+1))
            continue
        # get sensor sql data type
        try:
            sensor_sql_data_type = "'{}'".format(sensor[ch.KEY_METADATA_SENSORS_SQL_DATATYPE])
        except KeyError:
            print("No '{}' property found for sensor object at '{}', '{}', #{}".format(ch.KEY_METADATA_SENSORS_SQL_DATATYPE, ch.KEY_METADATA, ch.KEY_METADATA_SENSORS, i+1))
            continue

        metadata_sensors_tablename = '{}.{}'.format(ch.KEY_METADATA, ch.KEY_METADATA_SENSORS)
        if not metadata_schema_created:
            # create metadata schema and sensor metadata table
            f_contents.append(dbu.get_sql_schema_create_str(ch.KEY_METADATA))
            columns = []
            columns.append("{} SERIAL PRIMARY KEY".format(ch.KEY_METADATA_SENSORS_ID))
            columns.append("{} VARCHAR NOT NULL".format(ch.KEY_TYPE))
            columns.append("{} VARCHAR".format(ch.KEY_METADATA_SENSORS_UNITS))
            columns.append("{} VARCHAR NOT NULL".format(ch.KEY_METADATA_SENSORS_SQL_DATATYPE))
            f_contents.append(dbu.get_sql_table_create_str(metadata_sensors_tablename, columns))
            metadata_schema_created = True

        # add row to table
        col_names = [ch.KEY_TYPE, ch.KEY_METADATA_SENSORS_UNITS, ch.KEY_METADATA_SENSORS_SQL_DATATYPE]
        col_vals = [sensor_type, sensor_units, sensor_sql_data_type]
        f_contents.append(dbu.get_sql_insert_str(metadata_sensors_tablename, col_names, col_vals))

    return ''.join(f_contents)


def generate_db_tables_str(json_data:dict) -> str:
    """Return sql script for generating db tables.

    Keyword arguments:
    json_data -- json object, root of config file (required).
    """

    # find systems
    try:
        systems = json_data[ch.KEY_SYSTEMS]
    except KeyError:
        print("No '{}' property found in config file".format(ch.KEY_SYSTEMS))
        return ""   # return blank string for no sql script created

    f_contents = []
    f_contents.append("\n--Ponics Database Tables Script (auto-generated)\n")

    # iterate through systems
    for i, system in enumerate(systems):
        # get system name
        try:
            sys_name = system[ch.KEY_NAME].replace('/', '')
        except KeyError:
            sys_name = ch.get_default_system_name(i+1)
        print("Found system: '{}'".format(sys_name))

        # only create system schema if at least one sensor
        sys_schema_created = False

        for container_type, container_type_singular in ch.CONTAINER_TYPES.items():
            # find containers (tanks or crops)
            try:
                containers = system[container_type]
            except KeyError:
                print("No '{}' property found for system '{}'".format(container_type, sys_name))
                continue

            # iterate through containers in system
            for j, container in enumerate(containers):
                # get container name
                try:
                    container_name = "{}".format(container[ch.KEY_NAME].replace('/', ''))
                except KeyError:
                    container_name = ch.get_default_container_name(container_type, j+1)
                print("Found container: '{}'".format(container_name))

                # find sensors
                try:
                    sensors = container[ch.KEY_SENSORS]
                except KeyError:
                    print("No '{}' property found for container '{}'".format(ch.KEY_SENSORS, container_name))
                    continue

                # iterate through sensors in tank
                for k, sensor in enumerate(sensors):
                    # get sensor type
                    try:
                        sensor_type = sensor[ch.KEY_TYPE].replace('/', '')
                    except KeyError:
                        print("No '{}' property found for system '{}', container '{}', sensor #{}".format(ch.KEY_TYPE, sys_name, container_name, k+1))
                        continue
                    # get sensor name
                    try:
                        sensor_name = "{}".format(sensor[ch.KEY_NAME].replace('/', ''))
                    except KeyError:
                        sensor_name = ch.get_default_sensor_name(sensor_type)

                    if not sys_schema_created:
                        # create schema for system (at least one sensor exists)
                        f_contents.append(dbu.get_sql_schema_create_str(sys_name))
                        sys_schema_created = True

                    # create table for sensor
                    sensor_datatype = ch.get_sensor_sql_data_type(json_data, sensor_type)

                    print("Found sensor: '{}'".format(sensor_name))

                    columns = []
                    columns.append("{} SERIAL PRIMARY KEY".format(dbu.SENSOR_PRIMARY_KEY_COL_NAME))
                    columns.append("{} timestamptz DEFAULT LOCALTIMESTAMP".format(dbu.SENSOR_TIMESTAMP_COL_NAME))
                    columns.append("{} {} NOT NULL".format(dbu.SENSOR_READING_COL_NAME, sensor_datatype))
                    sensor_tablename = dbu.get_sensor_tablename(sys_name, container_name, sensor_name)
                    f_contents.append(dbu.get_sql_table_create_str(sensor_tablename, columns))

    return ''.join(f_contents)


def main(config_file:str, sql_file:str=None) -> int:
    """ Generates an sql file for database initialization and returns the file path. Expects a config json file at /home/$CONFIG_FILE.

    Keyword arguments:
    config_file -- path to config json file (required).
    sql_file -- SQL filename to write to. Omits writing if None (default).
    """
    json_contents = ch.get_json_file_contents(config_file)
    if json_contents is None:
        print("Internal Error: Config file json data is null. Exiting")
        sys.exit(1)

    db_init_tables_str = generate_db_tables_str(json_contents)
    metadata_sensor_table_str = generate_metadata_sensor_table_str(json_contents)
    sql_script_str = db_init_tables_str + metadata_sensor_table_str

    print("\n*** BEGIN FULL SQL SCRIPT ***\n{}\n*** END FULL SQL SCRIPT ***\n".format(sql_script_str))

    if sql_file is not None:
        with open(sql_file, 'w') as f:
            f.write(sql_script_str)
        print("Wrote db init sql script to '{}'".format(sql_file))

    return 0


if __name__ == "__main__":
    print("Starting db init sql script generation")

    # get config file
    if os.getenv('CONFIG_FILE') != '':
        config_file = '/home/{}'.format(os.getenv('CONFIG_FILE'))
    else:
        print("Error: CONFIG_FILE environment variable is not set.")
        sys.exit(1)
    # get sql file
    if os.getenv('DB_INIT_SQL_FILE') != '':
        sql_file = '/sql/{}'.format(os.getenv('DB_INIT_SQL_FILE'))
    else:
        print("Warning: DB_INIT_SQL_FILE environment variable is not set.")
        sql_file = None

    # run main program
    main(config_file, sql_file=sql_file)  # write changes to config file
    print("db init finished successfully")
    sys.exit(0)
