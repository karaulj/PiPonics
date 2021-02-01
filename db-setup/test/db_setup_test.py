import unittest
import sys, os
import db_setup
import json


def get_json_data(filename):
    data = None
    with open(filename) as f:
        data = json.load(f)
    return data


class Test_get_config_file_json_contents(unittest.TestCase):

    def setUp(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
    def tearDown(self):
        sys.stdout.close()
        sys.stdout = self._original_stdout

    def test_no_file(self):
        with self.assertRaises(IOError):
            json_file = ''
            actual = db_setup.get_config_file_json_contents(json_file=json_file)

    def test_invalid_file(self):
        with self.assertRaises(json.decoder.JSONDecodeError):
            json_file = '/data/invalid.json'
            actual = db_setup.get_config_file_json_contents(json_file=json_file)

    def test_1system_1tank_1sensor(self):
        expected = {
        "systems": [
        {
        "name": "sys1",
        "tanks": [
        {
        "name": "tank1",
        "nice_name": "Primary Fish Tank",
        "sensors": [
        {
        "type": "pH"
        }
        ]
        }
        ]
        }
        ],
        "metadata": {
        "sensors": [
        {
        "type": "pH",
        "units": None,
        "sql_data_type": "SMALLINT"
        }
        ]
        }
        }
        json_file = '/data/1system_1tank_1sensor.json'
        actual = db_setup.get_config_file_json_contents(json_file=json_file)
        self.assertEqual(actual, expected)
        self.assertEqual(actual["systems"][0]["tanks"][0]["sensors"][0]["type"], expected["systems"][0]["tanks"][0]["sensors"][0]["type"])


class Test_generate_metadata_sensor_table_str(unittest.TestCase):

    def setUp(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
    def tearDown(self):
        sys.stdout.close()
        sys.stdout = self._original_stdout

    def test_empty_file(self):
        json_file = '/data/empty.json'
        data = get_json_data(json_file)
        actual = db_setup.generate_metadata_sensor_table_str(json_data=data)
        expected = ''
        self.assertEqual(actual, expected)

    def test_no_sensors(self):
        json_file = '/data/metadata_no_sensors.json'
        data = get_json_data(json_file)
        actual = db_setup.generate_metadata_sensor_table_str(json_data=data)
        expected = ''
        self.assertEqual(actual, expected)

    def test_multiple_sensors(self):
        json_file = '/data/metadata_mult_sensors.json'
        data = get_json_data(json_file)
        actual = db_setup.generate_metadata_sensor_table_str(json_data=data)

        metadata_schema_str = "CREATE SCHEMA metadata;"
        self.assertIn(metadata_schema_str, actual)

        create_table_str = """CREATE TABLE metadata.sensors (
  sensor_id SERIAL PRIMARY KEY,
  type VARCHAR NOT NULL,
  units VARCHAR,
  sql_data_type VARCHAR NOT NULL
);"""
        self.assertIn(create_table_str, actual)

        insert_str = """INSERT INTO metadata.sensors (type, units, sql_data_type)
VALUES ('pH', NULL, 'SMALLINT');"""
        self.assertIn(insert_str, actual)

        insert_str = """INSERT INTO metadata.sensors (type, units, sql_data_type)
VALUES ('temp', 'degrees F', 'FLOAT');"""
        self.assertIn(insert_str, actual)

        insert_str = """INSERT INTO metadata.sensors (type, units, sql_data_type)
VALUES ('DO', 'mg/L', 'FLOAT');"""
        self.assertIn(insert_str, actual)


class Test_generate_db_tables_str(unittest.TestCase):

    def setUp(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
    def tearDown(self):
        sys.stdout.close()
        sys.stdout = self._original_stdout

    def test_empty_file(self):
        json_file = '/data/empty.json'
        data = get_json_data(json_file)
        actual = db_setup.generate_db_tables_str(json_data=data)
        expected = ''
        self.assertEqual(actual, expected)

    def test_1system_1tank_1sensor(self):
        json_file = '/data/1system_1tank_1sensor.json'
        data = get_json_data(json_file)
        actual = db_setup.generate_db_tables_str(json_data=data)

        create_schema_str = "CREATE SCHEMA sys1;"
        self.assertIn(create_schema_str, actual)

        create_table_str = """
CREATE TABLE sys1.tank1_pH (
  entry_id SERIAL PRIMARY KEY,
  timestamp timestamp without time zone DEFAULT LOCALTIMESTAMP,
  reading SMALLINT NOT NULL
);"""
        self.assertIn(create_table_str, actual)

if __name__ == "__main__":
    unittest.main(verbosity=2)
