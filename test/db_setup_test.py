import unittest
import sys, os
import json

import db_setup
import config_utils as ch
import db_utils as dbu


class Test_generate_metadata_sensor_table_str(unittest.TestCase):

    def setUp(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
    def tearDown(self):
        sys.stdout.close()
        sys.stdout = self._original_stdout

    def test_empty_file(self):
        json_file = '/data/empty.json'
        data = ch.get_json_file_contents(json_file)
        actual = db_setup.generate_metadata_sensor_table_str(json_data=data)
        expected = ''
        self.assertEqual(actual, expected)

    def test_no_sensors(self):
        json_file = '/data/metadata_no_sensors.json'
        data = ch.get_json_file_contents(json_file)
        actual = db_setup.generate_metadata_sensor_table_str(json_data=data)
        expected = ''
        self.assertEqual(actual, expected)

    def test_multiple_sensors(self):
        json_file = '/data/metadata_mult_sensors.json'
        data = ch.get_json_file_contents(json_file)
        actual = db_setup.generate_metadata_sensor_table_str(json_data=data)

        metadata_schema_str = "CREATE SCHEMA IF NOT EXISTS metadata;"
        self.assertIn(metadata_schema_str, actual)

        create_table_str = """CREATE TABLE IF NOT EXISTS metadata.sensors (
  sensor_id SERIAL PRIMARY KEY,
  type VARCHAR NOT NULL,
  units VARCHAR,
  sql_data_type VARCHAR NOT NULL
);"""
        self.assertIn(create_table_str, actual)

        insert_str = """INSERT INTO metadata.sensors (type, units, sql_data_type)
VALUES ('pH', NULL, 'SMALLINT')"""
        self.assertIn(insert_str, actual)

        insert_str = """INSERT INTO metadata.sensors (type, units, sql_data_type)
VALUES ('temp', 'degrees F', 'FLOAT')"""
        self.assertIn(insert_str, actual)

        insert_str = """INSERT INTO metadata.sensors (type, units, sql_data_type)
VALUES ('DO', 'mg/L', 'FLOAT')"""
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
        data = ch.get_json_file_contents(json_file)
        actual = db_setup.generate_db_tables_str(json_data=data)
        expected = ''
        self.assertEqual(actual, expected)

    def test_1system_1tank_1sensor(self):
        json_file = '/data/1system_1tank_1sensor.json'
        data = ch.get_json_file_contents(json_file)
        actual = db_setup.generate_db_tables_str(json_data=data)

        create_schema_str = "CREATE SCHEMA IF NOT EXISTS sys1;"
        self.assertIn(create_schema_str, actual)

        create_table_str = """
CREATE TABLE IF NOT EXISTS sys1.tank1_pH (
  {} SERIAL PRIMARY KEY,
  {} timestamp DEFAULT LOCALTIMESTAMP,
  {} SMALLINT NOT NULL
);""".format(dbu.SENSOR_PRIMARY_KEY_COL_NAME, dbu.SENSOR_TIMESTAMP_COL_NAME, dbu.SENSOR_READING_COL_NAME)
        self.assertIn(create_table_str, actual)

    def test_2system_full(self):
        json_file = '/data/2system_full.json'
        data = ch.get_json_file_contents(json_file)
        actual = db_setup.generate_db_tables_str(json_data=data)
        print(actual)

        create_sys1_schema_str = "CREATE SCHEMA IF NOT EXISTS mainsys;"
        self.assertIn(create_sys1_schema_str, actual)

        create_sys2_schema_str = "CREATE SCHEMA IF NOT EXISTS backupsys;"
        #self.assertIn(create_sys2_schema_str, actual)

        create_sys1_table_str = "CREATE TABLE IF NOT EXISTS mainsys.fishtank1_DO"
        self.assertIn(create_sys1_table_str, actual)

        create_sys2_table_str = "CREATE TABLE IF NOT EXISTS backupsys.growbed1_temp"
        self.assertIn(create_sys2_table_str, actual)

    def test_emptysystem(self):
        json_file = '/data/emptysystem.json'
        data = ch.get_json_file_contents(json_file)
        actual = db_setup.generate_db_tables_str(json_data=data)

        expected = "\n--Ponics Database Tables Script (auto-generated)\n"

        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main(verbosity=2)
