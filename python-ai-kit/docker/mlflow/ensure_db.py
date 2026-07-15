"""Create the MLflow database if it does not exist yet.

Runs inside the mlflow container (see docker-compose.yml), where psycopg2
ships with the ghcr.io/mlflow/mlflow:*-full image.
"""

import os

import psycopg2  # ty: ignore[unresolved-import]
from psycopg2 import sql  # ty: ignore[unresolved-import]


def main() -> None:
    db_name = os.environ["MLFLOW_DB_NAME"]
    conn = psycopg2.connect(
        host=os.environ["PGHOST"],
        port=os.environ["PGPORT"],
        user=os.environ["PGUSER"],
        password=os.environ["PGPASSWORD"],
        dbname="postgres",
    )
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
            if cur.fetchone():
                print(f"Database '{db_name}' already exists")
                return
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
            print(f"Created database '{db_name}'")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
