import time
from datetime import datetime
import logging
import json

import psycopg2
from psycopg2 import pool

import config_utils as ch
import db_utils as dbu
from http_utils import APIParams, APIErrors


class DataAccessLayer(object):

    def __init__(self, dbname, user, password, host, port, minconn=0, maxconn=4):
        self._logger = self._init_logging()
        self._dbname = dbname
        self._user = user
        self._password = password
        self._host = host
        self._port = port
        self._minconn = minconn
        self._maxconn = maxconn
        #self.conn = self._connect()
        self._conn_pool = self._get_conn_pool()
        self.sensor_cols = [dbu.SENSOR_TIMESTAMP_COL_NAME, dbu.SENSOR_READING_COL_NAME]
        self.time_row_idx = 0
        self.val_row_idx = 1

    def __del__(self):
        self.shutdown()

    def _init_logging(self):
        logger = logging.getLogger(__name__)
        s_handler = logging.StreamHandler()
        s_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('[%(asctime)s] %(name)s [%(levelname)s] %(message)s')
        s_handler.setFormatter(formatter)

        logger.addHandler(s_handler)
        logger.setLevel(logging.DEBUG)
        return logger

    def get_conn(self):
        num_retries = 0
        while num_retries < 10:
            try:
                conn = self._conn_pool.getconn()
                self._logger.debug("Successfully got db connection")
                return conn
            except psycopg2.OperationalError:
                self._logger.warning("Connection to db failed. Attempting reconnect...")
                time.sleep(1)
                num_retries += 1
        self._logger.error("Could not get connection at '{}', port '{}'".format(self._host, self._port))

    def put_conn(self, conn):
        self._conn_pool.putconn(conn)

    def _get_conn_pool(self):
        num_retries = 0
        while num_retries < 10:
            try:
                conn_pool = pool.ThreadedConnectionPool(
                    minconn = self._minconn,
                    maxconn = self._maxconn,
                    dbname = self._dbname,
                    user = self._user,
                    password = self._password,
                    host = self._host,
                    port = self._port
                )
                self._logger.debug("Started db connection pool")
                return conn_pool
            except psycopg2.OperationalError:
                self._logger.warning("Connection to db failed. Attempting reconnect...")
                time.sleep(1)
                num_retries += 1
        self._logger.error("Could not start connection pool at '{}', port '{}'".format(self._host, self._port))

    def _get_tablename_from_sensor_item(self, sensor_item:dict):
        if not dbu.is_sensor_item(sensor_item):
            return None
        system = sensor_item[ch.KEY_SYSTEM]
        container = sensor_item[ch.KEY_TANK_OR_CROP]
        if ch.KEY_NAME in sensor_item:
            sensor = sensor_item[ch.KEY_NAME]
        else:
            sensor = sensor_item[ch.KEY_TYPE]
        return dbu.get_sensor_tablename(system, container, sensor)

    def _get_sensor_data_query(self, tablename:str, start:datetime, end:datetime):
        query = "SELECT {col_names} FROM {table}".format(
            col_names=", ".join(self.sensor_cols),
            table=tablename
        )
        if start is not None or end is not None: query += " WHERE "
        query_params = []
        added_start = False
        if start is not None:
            query += "{timestamp_col} >= %s".format(
                timestamp_col=dbu.SENSOR_TIMESTAMP_COL_NAME
            )
            query_params.append(start)
            added_start = True
        if end is not None:
            if added_start: query += " AND "
            query += "{timestamp_col} <= %s".format(
                timestamp_col=dbu.SENSOR_TIMESTAMP_COL_NAME
            )
            query_params.append(end)
        query += ";"
        return query, query_params

    def _get_add_reading_query(self, tablename:str, reading:str):
        return "INSERT INTO {table} ({val_col}) VALUES ({value});".format(
            table=tablename,
            val_col=self.sensor_cols[self.val_row_idx],
            value=reading
        )

    def _get_sensor_data_from_results(self, results:list):
        new_results = list()
        for row in results:
            new_results.append({
                APIParams.SENSOR_READING_TIME  : row[self.time_row_idx].isoformat(),
                APIParams.SENSOR_READING_VALUE : row[self.val_row_idx]
            })
        return new_results

    def get_sensor_data(self, sensor_item:str, start_time:str=None, end_time:str=None):
        """Fetch sensor data from a preexisting database.

        Keyword arguments:
        sensor_item -- a dictionary following the schema defined in db_utils.
        start -- the start date, ISO-8601 format (default None).
        end -- the end date, ISO-8601 format (default None).
        """
        # check sensor item param
        sensor_tablename = self._get_tablename_from_sensor_item(sensor_item)
        if sensor_tablename is None:
            return APIErrors.ERR_BAD_SENSOR_PARAM
        self._logger.debug('Sensor tablename: {}'.format(sensor_tablename))
        # check start time param (None = default)
        self._logger.debug('Start time param: {}'.format(start_time))
        start_dt = None
        if start_time is not None:
            start_dt = dbu.get_datetime_from_iso8601_str(start_time)
            if start_dt is None:
                return APIErrors.ERR_BAD_START_TIME_PARAM
        # check end time param (None = default)
        self._logger.debug('End time param: {}'.format(end_time))
        end_dt = None
        if end_time is not None:
            end_dt = dbu.get_datetime_from_iso8601_str(end_time)
            if end_dt is None:
                return APIErrors.ERR_BAD_END_TIME_PARAM
        # check start time is before end time
        if start_dt is not None and end_dt is not None:
            if start_dt > end_dt:
                return APIErrors.ERR_START_AFTER_END
        # generate query
        query, query_params = self._get_sensor_data_query(sensor_tablename, start_dt, end_dt)
        self._logger.debug("Generated query: {}".format(query))
        self._logger.debug("Generated query params: {}".format(query_params))
        # execute query
        try:
            conn = self.get_conn()
            with conn.cursor() as cur:
                cur.execute(query, query_params)
                results = cur.fetchall()
            self.put_conn(conn)
            self._logger.debug('Raw query results: {}'.format(results))
        except Exception as e:
            self._logger.exception("Could not execute get sensor data SQL query.", exc_info=True)
            try:
                self.put_conn(conn)
            except:
                pass
            results = []
        # prep data
        sensor_data = self._get_sensor_data_from_results(results)
        self._logger.debug("Final sensor data: {}".format(sensor_data))
        return json.dumps(sensor_data)

    def add_sensor_reading(self, sensor_item:dict, reading:float):
        """Add a sensor reading to a preexisting database.

        Keyword arguments:
        sensor_item -- the sensor to add a reading for.
        reading -- the sensor reading to add.
        """
        if type(reading) != float:
            logging.error("Could not add sensor reading to db; type is '{}', not float".format(type(reading)))
            return 1
        sensor_tablename = self._get_tablename_from_sensor_item(sensor_item)
        if sensor_tablename is None:
            logging.error("Could not add sensor reading to db; sensor item is invalid")
            return 1
        add_query = self._get_add_reading_query(sensor_tablename, str(reading))
        self._logger.debug("Full add query: {}".format(add_query))
        # execute query
        try:
            conn = self.get_conn()
            with conn.cursor() as cur:
                cur.execute(add_query)
            conn.commit()
            self.put_conn(conn)
        except Exception as e:
            self._logger.exception("Could not execute add sensor reading SQL query.", exc_info=True)
            try:
                self.put_conn(conn)
            except:
                pass
            return 1
        self._logger.info("Added reading {} to table {}".format(reading, sensor_tablename))
        return 0

    def shutdown(self):
        if self._conn_pool:
            try:
                self._conn_pool.closeall()
            except pool.PoolError:
                pass
