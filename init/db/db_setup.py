import os
import sys
import json
import config_helper as ch


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
        sensor_list = json_data[ch.KEY_METADATA][ch.KEY_METADATA_SENSORS]
        for sensor in sensor_list:
            if sensor[ch.KEY_METADATA_SENSORS_TYPE] == sensor_type:
                return sensor[ch.KEY_METADATA_SENSORS_SQL_DATATYPE]
        return None
    except:
        return None


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
            sensor_type = "'{}'".format(sensor[ch.KEY_METADATA_SENSORS_TYPE])
        except KeyError:
            print("No '{}' property found for sensor object at '{}', '{}', #{}".format(ch.KEY_METADATA_SENSORS_TYPE, ch.KEY_METADATA, ch.KEY_METADATA_SENSORS, i+1))
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

        if not metadata_schema_created:
            # create metadata schema and sensor metadata table
            f_contents.append(get_sql_schema_create_str(ch.KEY_METADATA))
            columns = []
            columns.append("{} SERIAL PRIMARY KEY".format(ch.KEY_METADATA_SENSORS_ID))
            columns.append("{} VARCHAR NOT NULL".format(ch.KEY_METADATA_SENSORS_TYPE))
            columns.append("{} VARCHAR".format(ch.KEY_METADATA_SENSORS_UNITS))
            columns.append("{} VARCHAR NOT NULL".format(ch.KEY_METADATA_SENSORS_SQL_DATATYPE))
            f_contents.append(get_sql_table_create_str(ch.KEY_METADATA, ch.KEY_METADATA_SENSORS, columns))
            metadata_schema_created = True

        # add row to table
        col_names = [ch.KEY_METADATA_SENSORS_TYPE, ch.KEY_METADATA_SENSORS_UNITS, ch.KEY_METADATA_SENSORS_SQL_DATATYPE]
        col_vals = [sensor_type, sensor_units, sensor_sql_data_type]
        f_contents.append(get_sql_insert_str(ch.KEY_METADATA, ch.KEY_METADATA_SENSORS, col_names, col_vals))

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
            sys_name = system[ch.KEY_SYSTEMS_NAME].replace('/', '')
        except KeyError:
            sys_name = ch.get_default_system_name(i+1)
        print("Found system: '{}'".format(sys_name))

        # only create system schema if at least one sensor
        sys_schema_created = False

        # find tanks
        try:
            tanks = system[ch.KEY_TANKS]
        except KeyError:
            print("No '{}' property found for system '{}'".format(ch.KEY_TANKS, sys_name))
            continue

        # iterate through tanks in system
        for j, tank in enumerate(tanks):
            # get tank name
            try:
                tank_name = "{}".format(tank[ch.KEY_TANKS_NAME].replace('/', ''))
            except KeyError:
                tank_name = ch.get_default_tank_name(j+1)
            print("Found tank: '{}'".format(tank_name))

            # find sensors
            try:
                sensors = tank[ch.KEY_SENSORS]
            except KeyError:
                print("No '{}' property found for tank '{}'".format(ch.KEY_SENSORS, tank_name))
                continue

            # iterate through sensors in tank
            for k, sensor in enumerate(sensors):
                # get sensor type
                try:
                    sensor_type = sensor[ch.KEY_SENSORS_TYPE].replace('/', '')
                except KeyError:
                    print("No '{}' property found for system '{}', tank '{}', sensor #{}".format(ch.KEY_SENSORS_TYPE, sys_name, tank_name, k+1))
                    continue
                # get sensor name
                try:
                    sensor_name = "{}".format(sensor[ch.KEY_SENSORS_NAME].replace('/', ''))
                except KeyError:
                    sensor_name = ch.get_default_sensor_name(sensor_type)

                if not sys_schema_created:
                    # create schema for system (at least one sensor exists)
                    f_contents.append(get_sql_schema_create_str(sys_name))
                    sys_schema_created = True

                # create table for sensor
                sensor_datatype = get_sensor_sql_data_type(json_data, sensor_type)
                if sensor_datatype is None:
                    continue

                print("Found sensor: '{}'".format(sensor_name))

                columns = []
                columns.append("entry_id SERIAL PRIMARY KEY")
                columns.append("timestamp timestamp without time zone DEFAULT LOCALTIMESTAMP")
                columns.append("reading {} NOT NULL".format(sensor_datatype))
                f_contents.append(get_sql_table_create_str(sys_name, '{}_{}'.format(tank_name, sensor_name), columns))

        # find crops
        try:
            crops = system[ch.KEY_CROPS]
        except KeyError:
            print("No '{}' property found for system '{}'".format(ch.KEY_CROPS, sys_name))
            continue

        # iterate through crops in system
        for j, crop in enumerate(crops):
            # get crop name
            try:
                crop_name = "{}".format(crop[ch.KEY_CROPS_NAME].replace('/', ''))
            except KeyError:
                crop_name = ch.get_default_crop_name(j+1)
            print("Found crop: '{}'".format(crop_name))

            # find sensors
            try:
                sensors = crop[ch.KEY_SENSORS]
            except KeyError:
                print("No '{}' property found for crop '{}'".format(ch.KEY_SENSORS, crop_name))
                continue

            # iterate through sensors in crop
            for k, sensor in enumerate(sensors):
                # get sensor type
                try:
                    sensor_type = sensor[ch.KEY_SENSORS_TYPE].replace('/', '')
                except KeyError:
                    print("No '{}' property found for system '{}', crop '{}', sensor #{}".format(ch.KEY_SENSORS_TYPE, sys_name, crop_name, k+1))
                    continue
                # get sensor name
                try:
                    sensor_name = "{}".format(sensor[ch.KEY_SENSORS_NAME].replace('/', ''))
                except KeyError:
                    sensor_name = ch.get_default_sensor_name(sensor_type)

                if not sys_schema_created:
                    # create schema for system (at least one sensor exists)
                    f_contents.append(get_sql_schema_create_str(sys_name))
                    sys_schema_created = True

                # create table for sensor
                sensor_datatype = get_sensor_sql_data_type(json_data, sensor_type)
                if sensor_datatype is None:
                    continue

                print("Found sensor: '{}'".format(sensor_name))

                columns = []
                columns.append("entry_id SERIAL PRIMARY KEY")
                columns.append("timestamp timestamp without time zone DEFAULT LOCALTIMESTAMP")
                columns.append("reading {} NOT NULL".format(sensor_datatype))
                f_contents.append(get_sql_table_create_str(sys_name, '{}_{}'.format(crop_name, sensor_name), columns))

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
        sql_file = None

    # run main program
    main(config_file, sql_file=sql_file)  # write changes to config file
    print("db init finished successfully")
    sys.exit(0)
