import unittest
import sys, os
import description_gen, config_helper as ch
import json
import uuid


def is_valid_uuid(uuid_str):
    try:
        uuid.UUID(uuid_str, version=4)
        return True
    except ValueError:
        return False
    return False


class Test_generate_entity_contents(unittest.TestCase):

    def setUp(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
    def tearDown(self):
        sys.stdout.close()
        sys.stdout = self._original_stdout

    def test_empty_file(self):
        json_file = '/data/empty.json'
        data = ch.get_json_file_contents(json_file)
        actual = description_gen.generate_entity_contents(json_data=data)
        expected = {}
        self.assertEqual(actual, expected)

    def test_1system_1tank_1sensor(self):
        json_file = '/data/1system_1tank_1sensor.json'
        data = ch.get_json_file_contents(json_file)
        actual = description_gen.generate_entity_contents(json_data=data)

        self.assertEqual(actual[ch.KEY_SYSTEMS][0][ch.KEY_CROPS], [])

        self.assertEqual(actual[ch.KEY_SYSTEMS][0][ch.KEY_NAME], "sys1")
        self.assertEqual(actual[ch.KEY_SYSTEMS][0][ch.KEY_TANKS][0][ch.KEY_NAME], "tank1")
        self.assertEqual(actual[ch.KEY_SYSTEMS][0][ch.KEY_TANKS][0][ch.KEY_NICE_NAME], "Primary Fish Tank")
        self.assertEqual(actual[ch.KEY_SYSTEMS][0][ch.KEY_TANKS][0][ch.KEY_SENSORS][0][ch.KEY_SENSORS_TYPE], "pH")

        self.assertTrue(is_valid_uuid(actual[ch.KEY_SYSTEMS][0][ch.KEY_UUID]))
        self.assertTrue(is_valid_uuid(actual[ch.KEY_SYSTEMS][0][ch.KEY_TANKS][0][ch.KEY_UUID]))
        self.assertTrue(is_valid_uuid(actual[ch.KEY_SYSTEMS][0][ch.KEY_TANKS][0][ch.KEY_SENSORS][0][ch.KEY_UUID]))

        self.assertEqual(actual[ch.KEY_SYSTEMS][0][ch.KEY_NAME], actual[ch.KEY_SYSTEMS][0][ch.KEY_TANKS][0][ch.KEY_SYSTEM])
        self.assertEqual(actual[ch.KEY_SYSTEMS][0][ch.KEY_NAME], actual[ch.KEY_SYSTEMS][0][ch.KEY_TANKS][0][ch.KEY_SENSORS][0][ch.KEY_SYSTEM])

        self.assertEqual(actual[ch.KEY_SYSTEMS][0][ch.KEY_TANKS][0][ch.KEY_NAME], actual[ch.KEY_SYSTEMS][0][ch.KEY_TANKS][0][ch.KEY_SENSORS][0][ch.KEY_TANK])

    def test_1system_1crop_emptysensor(self):
        json_file = '/data/1system_1crop_emptysensor.json'
        data = ch.get_json_file_contents(json_file)
        actual = description_gen.generate_entity_contents(json_data=data)

        self.assertEqual(actual[ch.KEY_SYSTEMS][0][ch.KEY_TANKS], [])

        self.assertEqual(actual[ch.KEY_SYSTEMS][0][ch.KEY_NAME], "sys1")
        self.assertEqual(actual[ch.KEY_SYSTEMS][0][ch.KEY_CROPS][0][ch.KEY_NAME], "crop1")
        self.assertEqual(actual[ch.KEY_SYSTEMS][0][ch.KEY_CROPS][0][ch.KEY_NICE_NAME], "Nutrient Film Bed")

        self.assertTrue(is_valid_uuid(actual[ch.KEY_SYSTEMS][0][ch.KEY_UUID]))
        self.assertTrue(is_valid_uuid(actual[ch.KEY_SYSTEMS][0][ch.KEY_CROPS][0][ch.KEY_UUID]))
        # should be no entry for empty sensor
        self.assertEqual(len(actual[ch.KEY_SYSTEMS][0][ch.KEY_CROPS][0][ch.KEY_SENSORS]), 0)

        self.assertEqual(actual[ch.KEY_SYSTEMS][0][ch.KEY_NAME], actual[ch.KEY_SYSTEMS][0][ch.KEY_CROPS][0][ch.KEY_SYSTEM])




if __name__ == "__main__":
    unittest.main(verbosity=2)
