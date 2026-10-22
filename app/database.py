import os
import psycopg
from dotenv import load_dotenv

load_dotenv()


class DatabaseConfig:
    def __init__(self):
        database_url = os.environ["DATABASE_URL"]
        self.conninfo = database_url.replace("postgresql+psycopg://", "postgresql://", 1)

    def open_connection(self):
        return psycopg.connect(
            self.conninfo,
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