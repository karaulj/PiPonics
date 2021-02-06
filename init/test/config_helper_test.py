import unittest
import sys, os
import config_helper
import json


class Test_get_json_file_contents(unittest.TestCase):

    def setUp(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
    def tearDown(self):
        sys.stdout.close()
        sys.stdout = self._original_stdout

    def test_no_file(self):
        with self.assertRaises(IOError):
            json_file = ''
            actual = config_helper.get_json_file_contents(json_file=json_file)

    def test_invalid_file(self):
        with self.assertRaises(json.decoder.JSONDecodeError):
            json_file = '/data/invalid.json'
            actual = config_helper.get_json_file_contents(json_file=json_file)

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
        actual = config_helper.get_json_file_contents(json_file=json_file)
        self.assertEqual(actual, expected)
        self.assertEqual(actual["systems"][0]["tanks"][0]["sensors"][0]["type"], expected["systems"][0]["tanks"][0]["sensors"][0]["type"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
