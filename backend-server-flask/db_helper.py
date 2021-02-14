import time
from datetime import datetime

import psycopg2
from psycopg2 import pool

import config_utils as ch
import db_utils as dbu


ERR_BAD_SENSOR_PARAM = 100
ERR_BAD_SENSOR_PARAM_MSG = "The referenced sensor item is missing or invalid."
ERR_BAD_START_TIME_PARAM = 99
ERR_BAD_START_TIME_PARAM_MSG = "The provided start time is missing or invalid."
ERR_BAD_END_TIME_PARAM = 98
ERR_BAD_END_TIME_PARAM_MSG = "The provided end time is missing or invalid."
ERR_START_AFTER_END = 97
ERR_START_AFTER_END_MSG = "The provided start time must be equal to or less than end time."


class DataAccessLayer(object):

    def __init__(self, dbname, user, password, host, port, minconn=0, maxconn=4):
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
        self.time_row_idx = self._get_time_row_idx()

    def _get_time_row_idx(self):
        for idx, col_name in enumerate(self.sensor_cols):
            if col_name == dbu.SENSOR_TIMESTAMP_COL_NAME:
                return idx
        raise Exception("No timestamp row found in sensor column list.")

    def get_conn(self):
        num_retries = 0
        while num_retries < 10:
            try:
                conn = self._conn_pool.getconn()
                print("Connected to db successfully")
                return conn
            except psycopg2.OperationalError:
                print("Connection to db failed. Attempting reconnect...")
                time.sleep(1)
                num_retries += 1
        raise Exception("Could not connect to PostgreSQL server at '{}', port '{}'".format(self._host, self._port))

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
                print("Connected to db successfully")
                return conn_pool
            except psycopg2.OperationalError:
                print("Connection to db failed. Attempting reconnect...")
                time.sleep(1)
                num_retries += 1
        raise Exception("Could not connect to PostgreSQL server at '{}', port '{}'".format(self._host, self._port))

    def _get_tablename_from_sensor_item(self, sensor_item:dict):
        if not dbu.is_sensor_item(sensor_item):
            return None
        system = sensor_item[ch.KEY_SYSTEM]
        container = sensor_item[ch.KEY_TANK_OR_CROP]
        sensor_type = sensor_item[ch.KEY_TYPE]
        return dbu.get_sensor_tablename(system, container, sensor_type)

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

    def _get_data_from_results(self, results:list):
        new_results = list()
        for row in results:
            new_row = list(row)
            # convert datetime to string
            new_row[self.time_row_idx] = row[self.time_row_idx].isoformat()
        return new_results


    def get_sensor_data(self, sensor_item:str, start_time:str, end_time:str):
        # check sensor item param
        sensor_tablename = self._get_tablename_from_sensor_item(sensor_item)
        if sensor_tablename is None:
            return ERR_BAD_SENSOR_PARAM
        # check start time param (None = default)
        start_dt = None
        if start_time is not None:
            start_dt = dbu.get_datetime_from_iso8601_str(start_time)
            if start_dt is None:
                return ERR_BAD_START_TIME_PARAM
        # check end time param (None = default)
        end_dt = None
        if end_time is not None:
            end_dt = dbu.get_datetime_from_iso8601_str(end_time)
            if end_dt is None:
                return ERR_BAD_END_TIME_PARAM
        if start_dt is not None and end_dt is not None:
            if start_dt > end_dt:
                return ERR_START_AFTER_END
        # generate query
        query, query_params = self._get_sensor_data_query(sensor_tablename, start_dt, end_dt)
        # execute query
        try:
            conn = self.get_conn()
            with conn.cursor() as cur:
                results = cur.execute(query, query_params)
            self.put_conn(conn)
        except:
            print("Error executing query.")
            raise
        # prep data
        sensor_data = self._get_data_from_results(results)
        return sensor_data

    def shutdown(self):
        if self._conn_pool:
            try:
                self._conn_pool.closeall()
            except pool.PoolError:
                pass
