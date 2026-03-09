"""
Database setup script.
Run this first to create the database schema.
"""
import sys
from pathlib import Path

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from config import DBConfig, get_logger

logger = get_logger(__name__)

def create_database(cfg: DBConfig) -> None:
    """Create the target database if it does not already exist."""
    conn = psycopg2.connect(**{**cfg.as_dict(), "dbname": "postgres"})
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (cfg.name,))
            if cur.fetchone():
                logger.info("Database '%s' already exists.", cfg.name)
            else:
                cur.execute(f'CREATE DATABASE "{cfg.name}"')
                logger.info("Database '%s' created.", cfg.name)
    finally:
        conn.close()

def run_schema(cfg: DBConfig):
    """Run the schema.sql file."""
    schema_path = Path(__file__).parent / "schema.sql"
    if not schema_path.exists():
        raise FileNotFoundError(f"schema.sql not found at {schema_path}")

    sql = schema_path.read_text()
    conn = psycopg2.connect(**cfg.as_dict())
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
        logger.info("Schema applied successfully.")
    finally:
        conn.close()


def main() -> None:
    cfg = DBConfig()
    logger.info("Setting up database '%s' on %s:%s…", cfg.name, cfg.host, cfg.port)

    create_database(cfg)
    run_schema(cfg)

    logger.info("Setup complete. You can now run fetch_data.py.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        logger.error("Setup failed: %s", exc)
        sys.exit(1)