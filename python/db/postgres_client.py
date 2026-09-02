import logging
import sqlite3
import pandas as pd
from typing import Optional, Dict, Any, List
from python.config import (
    POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, BASE_DIR
)

logger = logging.getLogger("PostgresClient")

class PostgresClient:
    """
    Manages database connections to PostgreSQL with fallback to SQLite for lightweight local testing.
    """
    def __init__(self):
        self.use_sqlite = False
        self.sqlite_path = BASE_DIR / "data" / "supply_chain_local.db"
        self._test_connection()

    def _test_connection(self):
        try:
            import socket
            # Fast socket check before psycopg2 connect
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.2)
            res = s.connect_ex((POSTGRES_HOST, POSTGRES_PORT))
            s.close()
            if res != 0:
                raise ConnectionError("Postgres port not open")

            import psycopg2
            conn = psycopg2.connect(
                host=POSTGRES_HOST,
                port=POSTGRES_PORT,
                dbname=POSTGRES_DB,
                user=POSTGRES_USER,
                password=POSTGRES_PASSWORD,
                connect_timeout=1
            )
            conn.close()
            logger.info("Connected to PostgreSQL successfully.")
        except Exception as e:
            logger.info(f"PostgreSQL unavailable ({e}). Using local SQLite fallback database.")
            self.use_sqlite = True
            self.sqlite_path.parent.mkdir(parents=True, exist_ok=True)

    def get_connection(self):
        if self.use_sqlite:
            conn = sqlite3.connect(str(self.sqlite_path))
            return conn
        else:
            import psycopg2
            return psycopg2.connect(
                host=POSTGRES_HOST,
                port=POSTGRES_PORT,
                dbname=POSTGRES_DB,
                user=POSTGRES_USER,
                password=POSTGRES_PASSWORD
            )

    def execute_script(self, sql_script: str):
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            if self.use_sqlite:
                # Remove schemas in SQLite syntax for compatibility
                lines = []
                for line in sql_script.splitlines():
                    if "CREATE SCHEMA" in line or "COMMENT ON SCHEMA" in line:
                        continue
                    lines.append(line)
                sql_clean = "\n".join(lines)
                sql_clean = sql_clean.replace(" CASCADE", "")
                sql_clean = sql_clean.replace("bronze.", "bronze_").replace("silver.", "silver_").replace("gold.", "gold_")
                sql_clean = sql_clean.replace("JSONB", "TEXT").replace("TIMESTAMP WITH TIME ZONE", "TIMESTAMP")
                cur.executescript(sql_clean)
            else:
                cur.execute(sql_script)
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Error executing script: {e}")
            raise e
        finally:
            conn.close()

    def write_df(self, df: pd.DataFrame, table_name: str, schema: str = "bronze", if_exists: str = "append"):
        full_table = f"{schema}.{table_name}" if not self.use_sqlite else f"{schema}_{table_name}"
        conn = self.get_connection()
        try:
            if self.use_sqlite:
                df.to_sql(full_table, conn, if_exists=if_exists, index=False)
            else:
                from sqlalchemy import create_engine
                engine = create_engine(f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")
                df.to_sql(table_name, engine, schema=schema, if_exists=if_exists, index=False)
            logger.info(f"Wrote {len(df)} rows to {full_table}")
        except Exception as e:
            logger.error(f"Error writing DataFrame to {full_table}: {e}")
            raise e
        finally:
            conn.close()

    def read_df(self, query: str) -> pd.DataFrame:
        conn = self.get_connection()
        try:
            if self.use_sqlite:
                query = query.replace("bronze.", "bronze_").replace("silver.", "silver_").replace("gold.", "gold_")
            df = pd.read_sql_query(query, conn)
            return df
        except Exception as e:
            logger.error(f"Error executing query ({query}): {e}")
            return pd.DataFrame()
        finally:
            conn.close()
