import psycopg


class DatabaseConfig:
    def __init__(self):
        self.dbname = "zayn_resort"
        self.user = "postgres"
        self.password = "Dohauhord1@%"
        self.host = "localhost"
        self.port = 5432

    def open_connection(self):
        return psycopg.connect(
            dbname = self.dbname,
            user = self.user,
            password = self.password,
            host = self.host,
            port = self.port,
            row_factory=psycopg.rows.dict_row
        )
    

db = DatabaseConfig()


def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    with db.open_connection() as conn:
        with conn.cursor() as cur:
            if params is not None:
                cur.execute(query, params)
            else:
                cur.execute(query)
            if fetch_one:
                return cur.fetchone()
            if fetch_all:
                return cur.fetchall()