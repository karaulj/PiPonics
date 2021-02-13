import time
from datetime import datetime

import psycopg2

import config_utils as ch
import db_utils as dbu

class DataAccessLayer:

    def __init__(self, dbname, user, password, host, port):
        self._dbname = dbname
        self._user = user
        self._password = password
        self._host = host
        self._port = port
        self.conn = self._connect()

    def _connect(self):
        num_retries = 0
        while num_retries < 10:
            try:
                conn = psycopg2.connect(
                    dbname = self._dbname,
                    user = self._user,
                    password = self._password,
                    host = self._host,
                    port = self._port
                )
                print("Connected to db successfully")
                return conn
            except psycopg2.OperationalError:
                print("Connection to db failed. Attempting reconnect...")
                time.sleep(1)
                num_retries += 1
        raise Exception("Could not connect to PostgreSQL server at '{}', port '{}'".format(self._host, self._port))

    def get_sensor_tablename(sensor_item:dict):
        system = sensor_item[ch.KEY_SYSTEM]
        container = sensor_item[ch.KEY_TANK_OR_CROP]
        sensor_type = sensor_item[ch.KEY_TYPE]
        return dbu.get_sensor_tablename(system, container, sensor_type)

    def get_sensor_values(self, sensor_item:dict, start_time:str, end_time:str):
        if not dbu.is_sensor_item(sensor_item): return None
        tablename = self.get_sensor_tablename(sensor_item)
        pass
