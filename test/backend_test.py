import unittest
import sys, os
import time
import uuid
import random
from http import HTTPStatus
from datetime import timezone
import logging

import requests
import psycopg2

import description_gen as dg
import config_utils as ch
import db_utils as dbu
from http_utils import HTTPHeaders, HTTPHeaderValues, APIParams, APIErrors
import main


def is_valid_uuid(uuid_str):
    try:
        uuid.UUID(uuid_str, version=4)
        return True
    except ValueError:
        return False
    return False


class Test_static_api_methods(unittest.TestCase):

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
        self.assertEqual(r.text, APIErrors.ERR_ENTITY_NOT_EXISTS_MSG)

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
        self.assertEqual(r.text, APIErrors.ERR_MISSING_PARAM_MSG)
        # tanks all, invalid uuid param
        r = requests.get(self.base_url+'/tank/all?uuid=6b88fed7-02b8-44b2-8de3')
        self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.TEXT_PLAIN)
        self.assertEqual(r.text, APIErrors.ERR_ENTITY_NOT_EXISTS_MSG)
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
        self.assertEqual(r.text, APIErrors.ERR_MISSING_PARAM_MSG)
        # crops all, invalid uuid param
        r = requests.get(self.base_url+'/crop/all?uuid=6b88fed7-02b8-44b2-671c45d41c99')
        self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.TEXT_PLAIN)
        self.assertEqual(r.text, APIErrors.ERR_ENTITY_NOT_EXISTS_MSG)
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
        self.assertEqual(r.text, APIErrors.ERR_MISSING_PARAM_MSG)
        # sensors all, invalid uuid param
        r = requests.get(self.base_url+'/sensor/all?uuid=6b88fed7-02b8-8de3-671c45d41c99')
        self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.TEXT_PLAIN)
        self.assertEqual(r.text, APIErrors.ERR_ENTITY_NOT_EXISTS_MSG)
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
        self.assertEqual(r.text, APIErrors.ERR_MISSING_PARAM_MSG)
        # actuators all, invalid uuid param
        r = requests.get(self.base_url+'/actuator/all?uuid=6b88fed7-44b2-8de3-671c45d41c99')
        self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.TEXT_PLAIN)
        self.assertEqual(r.text, APIErrors.ERR_ENTITY_NOT_EXISTS_MSG)
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
        self.assertEqual(r.text, APIErrors.ERR_MISSING_PARAM_MSG)
        # tanks all, invalid uuid param
        r = requests.get(self.base_url+'/tank/all?uuid=anincorrectvalue')
        self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.TEXT_PLAIN)
        self.assertEqual(r.text, APIErrors.ERR_ENTITY_NOT_EXISTS_MSG)
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
        self.assertEqual(r.text, APIErrors.ERR_MISSING_PARAM_MSG)
        # crops all, invalid uuid param
        r = requests.get(self.base_url+'/crop/all?uuid=another_incorrect_value')
        self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.TEXT_PLAIN)
        self.assertEqual(r.text, APIErrors.ERR_ENTITY_NOT_EXISTS_MSG)
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
        self.assertEqual(r.text, APIErrors.ERR_MISSING_PARAM_MSG)
        # sensors all, invalid uuid param
        r = requests.get(self.base_url+'/sensor/all?uuid=yet-another-incorrect-value')
        self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.TEXT_PLAIN)
        self.assertEqual(r.text, APIErrors.ERR_ENTITY_NOT_EXISTS_MSG)
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
        self.assertEqual(r.text, APIErrors.ERR_MISSING_PARAM_MSG)
        # actuators all, invalid uuid param
        r = requests.get(self.base_url+'/actuator/all?uuid=r3411y.b4d.at.th15')
        self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.TEXT_PLAIN)
        self.assertEqual(r.text, APIErrors.ERR_ENTITY_NOT_EXISTS_MSG)
        # actuators all, correct uuid
        r = requests.get(self.base_url+'/actuator/all?uuid={}'.format(system1_tank1_uuid))
        self.assertEqual(r.status_code, HTTPStatus.OK)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.APPLICATION_JSON)
        actuators = r.json()
        self.assertTrue(is_valid_uuid(actuators[0][ch.KEY_UUID]))
        self.assertEqual(actuators[0][ch.KEY_TYPE], "bubbler")

        self._shutdown_server()


#@unittest.skip('not ready yet')
class Test_dal_api_methods(unittest.TestCase):
    def setUp(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        logging.disable(logging.CRITICAL)
        self.api_port = str(random.randint(49152, 65534))
        self.api_host = '127.0.0.1'
        self.base_url = 'http://{}:{}'.format(self.api_host, self.api_port)
        self.conn = self._get_db_conn()
        self._schema = 'sys'
        self.table = dbu.get_sensor_tablename(self._schema, 'test', 'data')
        self._create_schema(self.conn, schema=self._schema)
        self._create_table(self.conn, tablename=self.table)
        #self.conn.commit()
        #self.conn.close()
        self._set_desc_file(json_file='/data/dal_test.json')
        self._start_server()
        self.sensor_uuid = self._get_sensor_uuid()
    def tearDown(self):
        if not self.conn:
            self.conn = self._get_db_conn()
        self._drop_schema(self.conn, schema=self._schema)
        self.conn.close()
        self._shutdown_server()
        sys.stdout.close()
        sys.stdout = self._original_stdout
        logging.disable(logging.NOTSET)

    def _create_schema(self, conn, schema):
        with conn.cursor() as cur:
            cur.execute(dbu.get_sql_schema_create_str(
                schema_name=schema
            ))
        return

    def _create_table(self, conn, tablename):
        with conn.cursor() as cur:
            cur.execute(dbu.get_sql_table_create_str(
                table_name=self.table,
                columns=dbu.SENSOR_COLS
            ))
        return

    def _drop_schema(self, conn, schema):
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS {} CASCADE".format(schema))
        conn.commit()
        return

    def _get_db_conn(self):
        dbname = os.getenv('POSTGRES_DB')
        host = os.getenv('POSTGRES_HOST')
        password = os.getenv('POSTGRES_PASSWORD')
        user = os.getenv('POSTGRES_USER')
        port = os.getenv('POSTGRES_PORT')
        num_retries = 0
        connected = False
        last_exc = None
        while num_retries < 10:
            try:
                return psycopg2.connect(
                    dbname=dbname,
                    user=user,
                    host=host,
                    password=password,
                    port=port
                )
            except Exception as exc:
                last_exc = exc
                time.sleep(1)
            num_retries += 1
        if not connected:
            if last_exc is None:
                raise Exception("There was an error connecting to the database. Ensure it is running.")
            else:
                raise last_exc
        return

    def _set_desc_file(self, json_file):
        os.environ['DESCRIPTION_FILE'] = 'dal_desc.json'
        dg.generate_description_file(json_file, '/common/dal_desc.json')

    def _start_server(self):
        main.start_api_server(
            do_sem_init=True,
            do_dal_init=True,
            do_ioc_init=False,
            flask_host=self.api_host,
            flask_port=self.api_port
        )
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
        requests.get(self.base_url+'/shutdown')

    def _get_sensor_uuid(self):
        systems = requests.get(self.base_url+'/system/all').json()
        return systems[0][ch.KEY_TANKS][0][ch.KEY_SENSORS][0][ch.KEY_UUID]

    def _tests(self):
        for name in dir(self):
            if name.startswith('apitest'):
                yield name, getattr(self, name)

    def test_all_seq(self):
        for name, test_method in self._tests():
            test_method()
            time.sleep(0.1)

    def apitest_template(self):
        # tests are run against db container.
        # schema/table are created and destroyed in setUp/tearDown methods.
        # API server is also created in setUp and destroyed in tearDown.
        # db connections are automatically created/closed.

        # tests should include adding data to created table and
        # running queries against that data
        pass

    def apitest_get_sensor_data_multiple(self):
        with self.conn.cursor() as cur:
            cur.execute("""
            INSERT INTO
            {table} ({time_col}, {val_col})
            VALUES
            ('2021-02-15T02:53:18.932274'::timestamp, 32.1::FLOAT);
            INSERT INTO
            {table} ({time_col}, {val_col})
            VALUES
            ('2022-08-20T12:43:12.342174'::timestamp, 43.2::FLOAT);
            INSERT INTO
            {table} ({time_col}, {val_col})
            VALUES
            ('2024-11-21T22:48:10.342876'::timestamp, 54.3::FLOAT);
            """.format(
                table=self.table,
                time_col=dbu.SENSOR_TIMESTAMP_COL_NAME,
                val_col=dbu.SENSOR_READING_COL_NAME
            ))
        self.conn.commit()

        """ NO START TIME / NO END TIME TESTS """
        # no start/end times, missing uuid
        r = requests.get(self.base_url+'/sensor/data')
        self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.TEXT_PLAIN)
        self.assertEqual(r.text, APIErrors.ERR_MISSING_PARAM_MSG)
        # no start/end times, invalid uuid
        r = requests.get(self.base_url+'/sensor/data?{}=an-invalid-uuid'.format(ch.KEY_UUID))
        self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.TEXT_PLAIN)
        self.assertEqual(r.text, APIErrors.ERR_BAD_SENSOR_PARAM_MSG)
        # no start/end times, correct uuid
        r = requests.get(self.base_url+'/sensor/data?{}={}'.format(ch.KEY_UUID, self.sensor_uuid))
        self.assertEqual(r.status_code, HTTPStatus.OK)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.APPLICATION_JSON)
        data = r.json()
        self.assertEqual(len(data), 3)
        first_val = data[0][APIParams.SENSOR_READING_VALUE]
        self.assertEqual(first_val, 32.1)
        first_dt = dbu.get_datetime_from_iso8601_str(data[0][APIParams.SENSOR_READING_TIME])
        self.assertEqual(first_dt.year, 2021)
        self.assertEqual(first_dt.month, 2)
        self.assertEqual(first_dt.day, 15)
        self.assertEqual(first_dt.hour, 2)
        self.assertEqual(first_dt.minute, 53)
        self.assertEqual(first_dt.second, 18)
        second_val = data[1][APIParams.SENSOR_READING_VALUE]
        self.assertEqual(second_val, 43.2)
        second_dt = dbu.get_datetime_from_iso8601_str(data[1][APIParams.SENSOR_READING_TIME])
        self.assertEqual(second_dt.year, 2022)
        self.assertEqual(second_dt.month, 8)
        self.assertEqual(second_dt.day, 20)
        self.assertEqual(second_dt.hour, 12)
        self.assertEqual(second_dt.minute, 43)
        self.assertEqual(second_dt.second, 12)
        third_val = data[2][APIParams.SENSOR_READING_VALUE]
        self.assertEqual(third_val, 54.3)
        third_dt = dbu.get_datetime_from_iso8601_str(data[2][APIParams.SENSOR_READING_TIME])
        self.assertEqual(third_dt.year, 2024)
        self.assertEqual(third_dt.month, 11)
        self.assertEqual(third_dt.day, 21)
        self.assertEqual(third_dt.hour, 22)
        self.assertEqual(third_dt.minute, 48)
        self.assertEqual(third_dt.second, 10)

        """ YES START TIME / NO END TIME TESTS """
        # empty start time, no end time, correct uuid
        r = requests.get(self.base_url+'/sensor/data?{}={}&{}={}'.format(
            ch.KEY_UUID,
            self.sensor_uuid,
            APIParams.START_TIME,
            ''
        ))
        self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.TEXT_PLAIN)
        self.assertEqual(r.text, APIErrors.ERR_BAD_START_TIME_PARAM_MSG)
        # invalid start time, no end time, correct uuid
        r = requests.get(self.base_url+'/sensor/data?{}={}&{}={}'.format(
            ch.KEY_UUID,
            self.sensor_uuid,
            APIParams.START_TIME,
            'not_a_datetime'
        ))
        self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.TEXT_PLAIN)
        self.assertEqual(r.text, APIErrors.ERR_BAD_START_TIME_PARAM_MSG)
        # valid start time, no end time, correct uuid
        r = requests.get(self.base_url+'/sensor/data?{}={}&{}={}'.format(
            ch.KEY_UUID,
            self.sensor_uuid,
            APIParams.START_TIME,
            '2022-01-09T22:51:59.342174'        # should return last two records
        ))
        self.assertEqual(r.status_code, HTTPStatus.OK)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.APPLICATION_JSON)
        data = r.json()
        self.assertEqual(len(data), 2)
        second_val = data[0][APIParams.SENSOR_READING_VALUE]
        self.assertEqual(second_val, 43.2)
        second_dt = dbu.get_datetime_from_iso8601_str(data[0][APIParams.SENSOR_READING_TIME])
        self.assertEqual(second_dt.year, 2022)
        self.assertEqual(second_dt.month, 8)
        self.assertEqual(second_dt.day, 20)
        self.assertEqual(second_dt.hour, 12)
        self.assertEqual(second_dt.minute, 43)
        self.assertEqual(second_dt.second, 12)
        third_val = data[1][APIParams.SENSOR_READING_VALUE]
        self.assertEqual(third_val, 54.3)
        third_dt = dbu.get_datetime_from_iso8601_str(data[1][APIParams.SENSOR_READING_TIME])
        self.assertEqual(third_dt.year, 2024)
        self.assertEqual(third_dt.month, 11)
        self.assertEqual(third_dt.day, 21)
        self.assertEqual(third_dt.hour, 22)
        self.assertEqual(third_dt.minute, 48)
        self.assertEqual(third_dt.second, 10)
        # valid start time, no end time, correct uuid
        r = requests.get(self.base_url+'/sensor/data?{}={}&{}={}'.format(
            ch.KEY_UUID,
            self.sensor_uuid,
            APIParams.START_TIME,
            '2032-01-09T22:51:59.342174'        # should return no records
        ))
        self.assertEqual(r.status_code, HTTPStatus.OK)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.APPLICATION_JSON)
        data = r.json()
        self.assertEqual(len(data), 0)

        """ NO START TIME / YES END TIME TESTS """
        # no start time, empty end time, correct uuid
        r = requests.get(self.base_url+'/sensor/data?{}={}&{}={}'.format(
            ch.KEY_UUID,
            self.sensor_uuid,
            APIParams.END_TIME,
            ''
        ))
        self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.TEXT_PLAIN)
        self.assertEqual(r.text, APIErrors.ERR_BAD_END_TIME_PARAM_MSG)
        # no start time, invalid end time, correct uuid
        r = requests.get(self.base_url+'/sensor/data?{}={}&{}={}'.format(
            ch.KEY_UUID,
            self.sensor_uuid,
            APIParams.END_TIME,
            'still_not_a_datetime'
        ))
        self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.TEXT_PLAIN)
        self.assertEqual(r.text, APIErrors.ERR_BAD_END_TIME_PARAM_MSG)
        # no start time, valid end time, correct uuid
        r = requests.get(self.base_url+'/sensor/data?{}={}&{}={}'.format(
            ch.KEY_UUID,
            self.sensor_uuid,
            APIParams.END_TIME,
            '2022-08-20T12:43:12.342174'        # should return first two records
        ))
        self.assertEqual(r.status_code, HTTPStatus.OK)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.APPLICATION_JSON)
        data = r.json()
        self.assertEqual(len(data), 2)
        first_val = data[0][APIParams.SENSOR_READING_VALUE]
        self.assertEqual(first_val, 32.1)
        first_dt = dbu.get_datetime_from_iso8601_str(data[0][APIParams.SENSOR_READING_TIME])
        self.assertEqual(first_dt.year, 2021)
        self.assertEqual(first_dt.month, 2)
        self.assertEqual(first_dt.day, 15)
        self.assertEqual(first_dt.hour, 2)
        self.assertEqual(first_dt.minute, 53)
        self.assertEqual(first_dt.second, 18)
        second_val = data[1][APIParams.SENSOR_READING_VALUE]
        self.assertEqual(second_val, 43.2)
        second_dt = dbu.get_datetime_from_iso8601_str(data[1][APIParams.SENSOR_READING_TIME])
        self.assertEqual(second_dt.year, 2022)
        self.assertEqual(second_dt.month, 8)
        self.assertEqual(second_dt.day, 20)
        self.assertEqual(second_dt.hour, 12)
        self.assertEqual(second_dt.minute, 43)
        self.assertEqual(second_dt.second, 12)
        # valid start time, no end time, correct uuid
        r = requests.get(self.base_url+'/sensor/data?{}={}&{}={}'.format(
            ch.KEY_UUID,
            self.sensor_uuid,
            APIParams.END_TIME,
            '1932-01-09T22:51:59.342174'        # should return no records
        ))
        self.assertEqual(r.status_code, HTTPStatus.OK)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.APPLICATION_JSON)
        data = r.json()
        self.assertEqual(len(data), 0)

        """ YES START TIME / YES END TIME TESTS """
        # invalid start time, valid end time, correct uuid
        r = requests.get(self.base_url+'/sensor/data?{}={}&{}={}&{}={}'.format(
            ch.KEY_UUID,
            self.sensor_uuid,
            APIParams.START_TIME,
            '2023243-21-74T12:42:4112.23532532234',
            APIParams.END_TIME,
            '2024-11-21T22:48:10.342876'
        ))
        self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.TEXT_PLAIN)
        self.assertEqual(r.text, APIErrors.ERR_BAD_START_TIME_PARAM_MSG)
        # valid start time, invalid end time, correct uuid
        r = requests.get(self.base_url+'/sensor/data?{}={}&{}={}&{}={}'.format(
            ch.KEY_UUID,
            self.sensor_uuid,
            APIParams.START_TIME,
            '2022-08-20T12:43:12.342174',
            APIParams.END_TIME,
            '2024532543252333.35325443T'
        ))
        self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.TEXT_PLAIN)
        self.assertEqual(r.text, APIErrors.ERR_BAD_END_TIME_PARAM_MSG)
        # start time after end time, correct uuid
        r = requests.get(self.base_url+'/sensor/data?{}={}&{}={}&{}={}'.format(
            ch.KEY_UUID,
            self.sensor_uuid,
            APIParams.START_TIME,
            '2022-08-20T12:43:13.342174',
            APIParams.END_TIME,
            '2022-08-20T12:43:12.342174'
        ))
        self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.TEXT_PLAIN)
        self.assertEqual(r.text, APIErrors.ERR_START_AFTER_END_MSG)
        # valid start time, valid end time, correct uuid
        r = requests.get(self.base_url+'/sensor/data?{}={}&{}={}&{}={}'.format(
            ch.KEY_UUID,
            self.sensor_uuid,
            APIParams.START_TIME,
            '2022-08-20T12:43:12.342174',
            APIParams.END_TIME,
            '2022-08-20T12:43:12.342174'
        ))      # should return second record only
        self.assertEqual(r.status_code, HTTPStatus.OK)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.APPLICATION_JSON)
        data = r.json()
        self.assertEqual(len(data), 1)
        second_val = data[0][APIParams.SENSOR_READING_VALUE]
        self.assertEqual(second_val, 43.2)
        second_dt = dbu.get_datetime_from_iso8601_str(data[0][APIParams.SENSOR_READING_TIME])
        self.assertEqual(second_dt.year, 2022)
        self.assertEqual(second_dt.month, 8)
        self.assertEqual(second_dt.day, 20)
        self.assertEqual(second_dt.hour, 12)
        self.assertEqual(second_dt.minute, 43)
        self.assertEqual(second_dt.second, 12)
        # valid start time, valid end time, correct uuid
        r = requests.get(self.base_url+'/sensor/data?{}={}&{}={}&{}={}'.format(
            ch.KEY_UUID,
            self.sensor_uuid,
            APIParams.START_TIME,
            '2012-12-28T12:43:12.123456',
            APIParams.END_TIME,
            '2034-01-20T22:45:52.332674'
        ))      # should return all records
        self.assertEqual(r.status_code, HTTPStatus.OK)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.APPLICATION_JSON)
        data = r.json()
        self.assertEqual(len(data), 3)
        first_val = data[0][APIParams.SENSOR_READING_VALUE]
        self.assertEqual(first_val, 32.1)
        first_dt = dbu.get_datetime_from_iso8601_str(data[0][APIParams.SENSOR_READING_TIME])
        self.assertEqual(first_dt.year, 2021)
        self.assertEqual(first_dt.month, 2)
        self.assertEqual(first_dt.day, 15)
        self.assertEqual(first_dt.hour, 2)
        self.assertEqual(first_dt.minute, 53)
        self.assertEqual(first_dt.second, 18)
        second_val = data[1][APIParams.SENSOR_READING_VALUE]
        self.assertEqual(second_val, 43.2)
        second_dt = dbu.get_datetime_from_iso8601_str(data[1][APIParams.SENSOR_READING_TIME])
        self.assertEqual(second_dt.year, 2022)
        self.assertEqual(second_dt.month, 8)
        self.assertEqual(second_dt.day, 20)
        self.assertEqual(second_dt.hour, 12)
        self.assertEqual(second_dt.minute, 43)
        self.assertEqual(second_dt.second, 12)
        third_val = data[2][APIParams.SENSOR_READING_VALUE]
        self.assertEqual(third_val, 54.3)
        third_dt = dbu.get_datetime_from_iso8601_str(data[2][APIParams.SENSOR_READING_TIME])
        self.assertEqual(third_dt.year, 2024)
        self.assertEqual(third_dt.month, 11)
        self.assertEqual(third_dt.day, 21)
        self.assertEqual(third_dt.hour, 22)
        self.assertEqual(third_dt.minute, 48)
        self.assertEqual(third_dt.second, 10)
        # valid start time, valid end time, correct uuid
        r = requests.get(self.base_url+'/sensor/data?{}={}&{}={}&{}={}'.format(
            ch.KEY_UUID,
            self.sensor_uuid,
            APIParams.START_TIME,
            '1912-12-28T12:43:12.123456',
            APIParams.END_TIME,
            '1934-01-20T22:45:52.332674'
        ))      # should return no records
        self.assertEqual(r.status_code, HTTPStatus.OK)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.APPLICATION_JSON)
        data = r.json()
        self.assertEqual(len(data), 0)


class Test_ioc_api_methods(unittest.TestCase):
    def setUp(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        #logging.disable(logging.CRITICAL)
        self.api_port = str(random.randint(49152, 65534))
        self.api_host = '127.0.0.1'
        self.base_url = 'http://{}:{}'.format(self.api_host, self.api_port)
        self._start_server()
    def tearDown(self):
        sys.stdout.close()
        sys.stdout = self._original_stdout
        #logging.disable(logging.NOTSET)
        self._shutdown_server()

    def _start_server(self):
        main.start_api_server(
            do_sem_init=True,
            do_dal_init=False,
            do_ioc_init=True,
            flask_host=self.api_host,
            flask_port=self.api_port
        )
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
        requests.get(self.base_url+'/shutdown')

    def _tests(self):
        for name in dir(self):
            if name.startswith('apitest'):
                yield name, getattr(self, name)

    def test_all_seq(self):
        for name, test_method in self._tests():
            test_method()
            time.sleep(0.1)

    def apitest_drive(self):
        # no uuid, no drive val
        r = requests.post(self.base_url+'/actuator/drive')
        self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.TEXT_PLAIN)
        self.assertEqual(r.text, APIErrors.ERR_MISSING_PARAM_MSG)
        # invalid uuid, no drive val
        r = requests.post(self.base_url+'/actuator/drive?{}=invalid'.format(ch.KEY_UUID))
        self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.TEXT_PLAIN)
        self.assertEqual(r.text, APIErrors.ERR_BAD_ACTUATOR_PARAM_MSG)
        # valid uuid, invalid drive val
        ret_0_uuid = 'return0'
        r = requests.post(self.base_url+'/actuator/drive?{}={}&{}={}'.format(
            ch.KEY_UUID,
            ret_0_uuid,
            APIParams.ACTUATOR_DRIVE_VALUE,
            'an-invalid-drive-val'
        ))
        self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.TEXT_PLAIN)
        self.assertEqual(r.text, APIErrors.ERR_BAD_DRIVE_VAL_PARAM_MSG)
        # valid uuid, no drive val
        ret_1_uuid = 'return1'
        r = requests.post(self.base_url+'/actuator/drive?{}={}'.format(
            ch.KEY_UUID,
            ret_1_uuid
        ))
        self.assertEqual(r.status_code, HTTPStatus.OK)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.TEXT_PLAIN)
        self.assertEqual(r.text, '1')
        # valid uuid, valid drive val
        r = requests.post(self.base_url+'/actuator/drive?{}={}&{}={}'.format(
            ch.KEY_UUID,
            ret_0_uuid,
            APIParams.ACTUATOR_DRIVE_VALUE,
            125
        ))
        self.assertEqual(r.status_code, HTTPStatus.OK)
        self.assertEqual(r.headers[HTTPHeaders.CONTENT_TYPE], HTTPHeaderValues.TEXT_PLAIN)
        self.assertEqual(r.text, '0')


if __name__ == "__main__":
    unittest.main(verbosity=2)
