import unittest
import sys, os
import time
import uuid
import random
from http import (
    HTTPStatus
)
import logging
import requests

import description_gen as dg
import config_utils as ch
import entity_utils as eu
from http_utils import (
    HTTPHeaders, HTTPHeaderValues
)
import main


def is_valid_uuid(uuid_str):
    try:
        uuid.UUID(uuid_str, version=4)
        return True
    except ValueError:
        return False
    return False


class Test_api_methods(unittest.TestCase):

    def setUp(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        logging.disable(logging.CRITICAL)
        self.desc_file_env = 'test_description.json'
        os.environ['DESCRIPTION_FILE'] = self.desc_file_env
        self.desc_file = '/common/{}'.format(self.desc_file_env)
        self.api_port = str(random.randint(49152, 65534))
        self.base_url = 'http://127.0.0.1:{}'.format(self.api_port)
    def tearDown(self):
        sys.stdout.close()
        sys.stdout = self._original_stdout
        logging.disable(logging.NOTSET)

    def _start_server(self, dal_init=False):
        self.api_port = str(random.randint(49152, 65534))
        self.base_url = 'http://127.0.0.1:{}'.format(self.api_port)
        main.start_api_server(do_sem_init=True, do_dal_init=dal_init, do_ioc_init=False, flask_port=self.api_port)
        num_retries = 0

        connected = False
        while num_retries < 10:
            try:
                requests.get(self.base_url+'/test')
                connected = True
                break
            except:
                time.sleep(0.5)
            num_retries += 1

        if not connected:
            raise Exception("There was an error starting the server.")

        return

    def _shutdown_server(self):
        try:
            requests.get(self.base_url+'/shutdown')
        except ConnectionRefusedError:
            raise Exception("Could not shutdown server; connection refused")
        return

    def _tests(self):
        for name in dir(self):
            if name.startswith('apitest'):
                yield name, getattr(self, name)

    def test_all_seq(self):
        for name, test_method in self._tests():
            """
            try:
                test_method()
            except Exception as e:
                self.fail("'{}' failed ({}: {})".format(name, type(e), e))
            """
            test_method()
            time.sleep(0.1)

    def apitest_empty(self):
        json_file = '/data/empty.json'
        dg.generate_description_file(json_file, self.desc_file)
        self._start_server()

        r = requests.get(self.base_url+'/system/all')
        self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.TEXT_PLAIN)
        self.assertEqual(r.text, eu.ERR_ENTITY_NOT_EXISTS_MSG)

        self._shutdown_server()

    def apitest_1system_1tank_1sensor(self):
        json_file = '/data/1system_1tank_1sensor.json'
        dg.generate_description_file(json_file, self.desc_file)
        self._start_server()

        # system all, no query params
        r = requests.get(self.base_url+'/system/all')
        self.assertEqual(r.status_code, HTTPStatus.OK)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.APPLICATION_JSON)
        systems = r.json()
        self.assertEqual(len(systems), 1)
        system1_uuid = systems[0][ch.KEY_UUID]
        self.assertTrue(is_valid_uuid(system1_uuid))
        self.assertEqual(systems[0][ch.KEY_NAME], "sys1")

        # tanks all, no query params
        r = requests.get(self.base_url+'/tank/all')
        self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.TEXT_PLAIN)
        self.assertEqual(r.text, eu.ERR_MISSING_PARAM_MSG)
        # tanks all, invalid uuid param
        r = requests.get(self.base_url+'/tank/all?uuid=6b88fed7-02b8-44b2-8de3')
        self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.TEXT_PLAIN)
        self.assertEqual(r.text, eu.ERR_ENTITY_NOT_EXISTS_MSG)
        # tanks all, correct uuid
        r = requests.get(self.base_url+'/tank/all?uuid={}'.format(system1_uuid))
        self.assertEqual(r.status_code, HTTPStatus.OK)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.APPLICATION_JSON)
        tanks = r.json()
        system1_tank1_uuid = tanks[0][ch.KEY_UUID]
        self.assertTrue(is_valid_uuid(system1_tank1_uuid))
        self.assertEqual(tanks[0][ch.KEY_NAME], "tank1")

        # crops all, no query params
        r = requests.get(self.base_url+'/crop/all')
        self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.TEXT_PLAIN)
        self.assertEqual(r.text, eu.ERR_MISSING_PARAM_MSG)
        # crops all, invalid uuid param
        r = requests.get(self.base_url+'/crop/all?uuid=6b88fed7-02b8-44b2-671c45d41c99')
        self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.TEXT_PLAIN)
        self.assertEqual(r.text, eu.ERR_ENTITY_NOT_EXISTS_MSG)
        # crops all, correct uuid
        r = requests.get(self.base_url+'/crop/all?uuid={}'.format(system1_uuid))
        self.assertEqual(r.status_code, HTTPStatus.OK)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.APPLICATION_JSON)
        crops = r.json()
        self.assertEqual(crops, [])

        # sensors all, no query params
        r = requests.get(self.base_url+'/sensor/all')
        self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.TEXT_PLAIN)
        self.assertEqual(r.text, eu.ERR_MISSING_PARAM_MSG)
        # sensors all, invalid uuid param
        r = requests.get(self.base_url+'/sensor/all?uuid=6b88fed7-02b8-8de3-671c45d41c99')
        self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.TEXT_PLAIN)
        self.assertEqual(r.text, eu.ERR_ENTITY_NOT_EXISTS_MSG)
        # sensors all, correct uuid
        r = requests.get(self.base_url+'/sensor/all?uuid={}'.format(system1_tank1_uuid))
        self.assertEqual(r.status_code, HTTPStatus.OK)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.APPLICATION_JSON)
        sensors = r.json()
        self.assertTrue(is_valid_uuid(sensors[0][ch.KEY_UUID]))
        self.assertEqual(sensors[0][ch.KEY_TYPE], "pH")

        # actuators all, no query params
        r = requests.get(self.base_url+'/actuator/all')
        self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.TEXT_PLAIN)
        self.assertEqual(r.text, eu.ERR_MISSING_PARAM_MSG)
        # actuators all, invalid uuid param
        r = requests.get(self.base_url+'/actuator/all?uuid=6b88fed7-44b2-8de3-671c45d41c99')
        self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.TEXT_PLAIN)
        self.assertEqual(r.text, eu.ERR_ENTITY_NOT_EXISTS_MSG)
        # actuators all, correct uuid
        r = requests.get(self.base_url+'/actuator/all?uuid={}'.format(system1_tank1_uuid))
        self.assertEqual(r.status_code, HTTPStatus.OK)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.APPLICATION_JSON)
        actuators = r.json()
        self.assertEqual(actuators, [])

        self._shutdown_server()

    def apitest_2system_full(self):
        json_file = '/data/2system_full.json'
        dg.generate_description_file(json_file, self.desc_file)
        self._start_server()

        # system all, no query params
        r = requests.get(self.base_url+'/system/all')
        self.assertEqual(r.status_code, HTTPStatus.OK)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.APPLICATION_JSON)
        systems = r.json()
        self.assertEqual(len(systems), 2)
        system1_uuid = systems[0][ch.KEY_UUID]
        self.assertTrue(is_valid_uuid(system1_uuid))
        self.assertEqual(systems[0][ch.KEY_NAME], "mainsys")
        system2_uuid = systems[1][ch.KEY_UUID]
        self.assertTrue(is_valid_uuid(system2_uuid))
        self.assertEqual(systems[1][ch.KEY_NAME], "backupsys")

        # tanks all, no query params
        r = requests.get(self.base_url+'/tank/all')
        self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.TEXT_PLAIN)
        self.assertEqual(r.text, eu.ERR_MISSING_PARAM_MSG)
        # tanks all, invalid uuid param
        r = requests.get(self.base_url+'/tank/all?uuid=anincorrectvalue')
        self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.TEXT_PLAIN)
        self.assertEqual(r.text, eu.ERR_ENTITY_NOT_EXISTS_MSG)
        # tanks all, correct uuid
        r = requests.get(self.base_url+'/tank/all?uuid={}'.format(system1_uuid))
        self.assertEqual(r.status_code, HTTPStatus.OK)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.APPLICATION_JSON)
        tanks = r.json()
        system1_tank1_uuid = tanks[0][ch.KEY_UUID]
        self.assertTrue(is_valid_uuid(system1_tank1_uuid))
        self.assertEqual(tanks[0][ch.KEY_NAME], "fishtank1")

        # crops all, no query params
        r = requests.get(self.base_url+'/crop/all')
        self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.TEXT_PLAIN)
        self.assertEqual(r.text, eu.ERR_MISSING_PARAM_MSG)
        # crops all, invalid uuid param
        r = requests.get(self.base_url+'/crop/all?uuid=another_incorrect_value')
        self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.TEXT_PLAIN)
        self.assertEqual(r.text, eu.ERR_ENTITY_NOT_EXISTS_MSG)
        # crops all, correct uuid
        r = requests.get(self.base_url+'/crop/all?uuid={}'.format(system2_uuid))
        self.assertEqual(r.status_code, HTTPStatus.OK)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.APPLICATION_JSON)
        crops = r.json()
        system2_crop1_uuid = crops[0][ch.KEY_UUID]
        self.assertTrue(is_valid_uuid(system2_crop1_uuid))
        self.assertEqual(crops[0][ch.KEY_NAME], "growbed1")

        # sensors all, no query params
        r = requests.get(self.base_url+'/sensor/all')
        self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.TEXT_PLAIN)
        self.assertEqual(r.text, eu.ERR_MISSING_PARAM_MSG)
        # sensors all, invalid uuid param
        r = requests.get(self.base_url+'/sensor/all?uuid=yet-another-incorrect-value')
        self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.TEXT_PLAIN)
        self.assertEqual(r.text, eu.ERR_ENTITY_NOT_EXISTS_MSG)
        # sensors all, correct uuid
        r = requests.get(self.base_url+'/sensor/all?uuid={}'.format(system2_crop1_uuid))
        self.assertEqual(r.status_code, HTTPStatus.OK)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.APPLICATION_JSON)
        sensors = r.json()
        self.assertTrue(is_valid_uuid(sensors[0][ch.KEY_UUID]))
        self.assertEqual(sensors[0][ch.KEY_TYPE], "temp")

        # actuators all, no query params
        r = requests.get(self.base_url+'/actuator/all')
        self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.TEXT_PLAIN)
        self.assertEqual(r.text, eu.ERR_MISSING_PARAM_MSG)
        # actuators all, invalid uuid param
        r = requests.get(self.base_url+'/actuator/all?uuid=r3411y.b4d.at.th15')
        self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.TEXT_PLAIN)
        self.assertEqual(r.text, eu.ERR_ENTITY_NOT_EXISTS_MSG)
        # actuators all, correct uuid
        r = requests.get(self.base_url+'/actuator/all?uuid={}'.format(system1_tank1_uuid))
        self.assertEqual(r.status_code, HTTPStatus.OK)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.APPLICATION_JSON)
        actuators = r.json()
        self.assertTrue(is_valid_uuid(actuators[0][ch.KEY_UUID]))
        self.assertEqual(actuators[0][ch.KEY_TYPE], "bubbler")

        self._shutdown_server()



if __name__ == "__main__":
    unittest.main(verbosity=2)
