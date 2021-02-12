

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


def get_sensor_tablename(system_name:str, container_name:str, sensor_name:str):
    return '{}.{}_{}'.format(system_name, container_name, sensor_name)
