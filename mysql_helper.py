import pymysql

class MySqlHelper:
    def __init__(self, host, user, password, database, port=3306):
        self.conn_params = {
            "host": host,
            "user": user,
            "password": password,
            "database": database,
            "port": port,
            "charset": "utf8mb4",
            "cursorclass": pymysql.cursors.DictCursor
        }

    def query(self, sql, params=None):
        conn = pymysql.connect(**self.conn_params)
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.fetchall()
        finally:
            conn.close()

    def execute(self, sql, params=None):
        conn = pymysql.connect(**self.conn_params)
        try:
            with conn.cursor() as cursor:
                result = cursor.execute(sql, params)
                conn.commit()
                return result
        except:
            conn.rollback()
            raise
        finally:
            conn.close()

    def executemany(self, sql, params_list):
        conn = pymysql.connect(**self.conn_params)
        try:
            with conn.cursor() as cursor:
                result = cursor.executemany(sql, params_list)
                conn.commit()
                return result
        except:
            conn.rollback()
            raise
        finally:
            conn.close()

    def transaction(self):
        return TransactionContext(self.conn_params)


class TransactionContext:
    def __init__(self, conn_params):
        self.conn_params = conn_params

    def __enter__(self):
        self.conn = pymysql.connect(**self.conn_params)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()
        self.cursor.close()
        self.conn.close()
