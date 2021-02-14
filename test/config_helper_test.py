import unittest
import sys, os
import json
import logging

import config_utils as ch


class Test_get_json_file_contents(unittest.TestCase):

    def setUp(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        logging.disable(logging.CRITICAL)
    def tearDown(self):
        sys.stdout.close()
        sys.stdout = self._original_stdout
        logging.disable(logging.NOTSET)

    def test_no_file(self):
        with self.assertRaises(IOError):
            json_file = ''
            actual = ch.get_json_file_contents(json_file=json_file)

    def test_invalid_file(self):
        with self.assertRaises(json.decoder.JSONDecodeError):
            json_file = '/data/invalid.json'
            actual = ch.get_json_file_contents(json_file=json_file)

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
        actual = ch.get_json_file_contents(json_file=json_file)
        self.assertEqual(actual, expected)
        self.assertEqual(actual[ch.KEY_SYSTEMS][0][ch.KEY_TANKS][0][ch.KEY_SENSORS][0][ch.KEY_TYPE], expected[ch.KEY_SYSTEMS][0][ch.KEY_TANKS][0][ch.KEY_SENSORS][0][ch.KEY_TYPE])


    def test_2system_full(self):
        json_file = '/data/2system_full.json'
        actual = ch.get_json_file_contents(json_file)

        self.assertEqual(len(actual[ch.KEY_SYSTEMS]), 2)

        self.assertEqual(actual[ch.KEY_SYSTEMS][0][ch.KEY_NAME], "mainsys")
        self.assertEqual(actual[ch.KEY_SYSTEMS][0][ch.KEY_TANKS][0][ch.KEY_NAME], "fishtank1")
        self.assertEqual(actual[ch.KEY_SYSTEMS][0][ch.KEY_TANKS][0][ch.KEY_NICE_NAME], "Primary Fish Tank")
        self.assertEqual(actual[ch.KEY_SYSTEMS][0][ch.KEY_TANKS][0][ch.KEY_SENSORS][0], {"type":"DO"})
        self.assertEqual(actual[ch.KEY_SYSTEMS][0][ch.KEY_TANKS][0][ch.KEY_ACTUATORS][0], {"type":"bubbler"})

        self.assertEqual(actual[ch.KEY_SYSTEMS][1][ch.KEY_NAME], "backupsys")
        self.assertEqual(actual[ch.KEY_SYSTEMS][1][ch.KEY_NICE_NAME], "Testing Ponics System (no fish)")
        self.assertEqual(actual[ch.KEY_SYSTEMS][1][ch.KEY_CROPS][0][ch.KEY_NAME], "growbed1")
        self.assertEqual(actual[ch.KEY_SYSTEMS][1][ch.KEY_CROPS][0][ch.KEY_SENSORS][0], {"type":"temp"})
        self.assertEqual(actual[ch.KEY_SYSTEMS][1][ch.KEY_CROPS][0][ch.KEY_ACTUATORS][0], {"type":"biofilter"})


    def test_emptysystem(self):
        json_file = '/data/emptysystem.json'
        actual = ch.get_json_file_contents(json_file=json_file)
        self.assertEqual(actual, {"systems": [{}]})


if __name__ == "__main__":
    unittest.main(verbosity=2)
