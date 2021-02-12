import time

import psycopg2


class DataAccessLayer:

    def __init__(self, dbname, user, password, host, port):
        self._dbname = dbname
        self._user = user
        self._password = password
        self._host = host
        self._port = port
        self.conn = self._connect()
    """
    def _connect(self):
        num_retries = 0
        time.sleep(5)
        while num_retries < 10:
            try:
                return psycopg2.connect(
                    dbname = self._dbname,
                    user = self._user,
                    password = self._password,
                    host = self._host,
                    port = self._port
                )
            except psycopg2.OperationalError:
                print("Connection to db failed. Attempting reconnect...")
                time.sleep(1)
                num_retries += 1
        raise Exception("Could not connect to PostgreSQL server at '{}', port '{}'".format(self._host, self._port))
    """
    def _connect(self):
        time.sleep(10)
        print(self._dbname)
        print(self._user)
        print(self._password)
        print(self._host)
        print(self._port)
        return psycopg2.connect(
            dbname = self._dbname,
            user = self._user,
            password = self._password,
            host = self._host,
            port = self._port
        )
