import config_utils as ch


# key: val --> property name: required
SENSOR_ITEM_SCHEMA = {
    ch.KEY_UUID: True,
    ch.KEY_TYPE: True,
    ch.KEY_SYSTEM: True,
    ch.KEY_TANK_OR_CROP: True,
    ch.KEY_NICE_NAME: False,
    ch.KEY_SENSORS_UNITS: False
}

SENSOR_PRIMARY_KEY_COL_NAME = "entry_id"
SENSOR_TIMESTAMP_COL_NAME = "time"
SENSOR_READING_COL_NAME = "value"

SENSOR_COLS = [
    "{} SERIAL PRIMARY KEY".format(SENSOR_PRIMARY_KEY_COL_NAME),
    "{} timestamp DEFAULT (now() at time zone 'utc') NOT NULL".format(SENSOR_TIMESTAMP_COL_NAME),
    "{} FLOAT NOT NULL".format(SENSOR_READING_COL_NAME)
]


""" START SQL QUERY HELPER FUNCTIONS """
def get_sql_schema_create_str(schema_name:str) -> str:
    return """
CREATE SCHEMA IF NOT EXISTS {0};
""".format(schema_name)
def get_sql_table_create_str(table_name:str, columns:list) -> str:
    return """
CREATE TABLE IF NOT EXISTS {0} (
  {1}
);
""".format(table_name, ",\n  ".join(columns))
def get_sql_insert_str(table_name:str, col_names:list, col_vals:list) -> str:
    return """
INSERT INTO {0} ({1})
VALUES ({2})
ON CONFLICT DO NOTHING;
""".format(table_name, ", ".join(col_names), ", ".join(col_vals))
""" END SQL QUERY HELPER FUNCTIONS """


def get_create_sensor_table_str(sys_name, container_name, sensor_name):
    return get_sql_table_create_str(
        table_name=get_sensor_tablename(sys_name, container_name, sensor_name),
        columns=SENSOR_COLS
    )


def get_sensor_tablename(system_name:str, container_name:str, sensor_name:str):
    return '{}.{}_{}'.format(system_name, container_name, sensor_name)


def is_sensor_item(sensor_item:dict):
    for property, is_required in SENSOR_ITEM_SCHEMA.items():
        if is_required:
            try:
                sensor_item[property]
            except KeyError:
                return False
    return True


def get_datetime_from_iso8601_str(date_string:str):
    from dateutil.parser import isoparse
    try:
        return isoparse(date_string)
    except:
        return None
    return None
