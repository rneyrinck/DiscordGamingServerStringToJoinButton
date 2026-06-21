import os
import psycopg
from psycopg.rows import dict_row

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    return psycopg.connect(
        DATABASE_URL,
        row_factory=dict_row
    )


def increment_join():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE stats
                SET joins = joins + 1
                WHERE id = 1
            """)
        conn.commit()


def get_join_count():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT joins
                FROM stats
                WHERE id = 1
            """)
            row = cur.fetchone()

            if row:
                return row["joins"]

            return 0