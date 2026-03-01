import os
import sys
from urllib.parse import urlparse

import psycopg
from dotenv import load_dotenv

load_dotenv()


def create_database():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("Error: DATABASE_URL is not set in environment variables.")
        sys.exit(1)

    url = urlparse(database_url)
    db_name = url.path[1:]
    user = url.username
    password = url.password
    host = url.hostname
    port = url.port

    print(f"Checking database '{db_name}' on {host}:{port}...")

    # Connect to the default 'postgres' database to create the new database
    try:
        conn = psycopg.connect(
            dbname="postgres", user=user, password=password, host=host, port=port
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        exists = cursor.fetchone()

        if not exists:
            print(f"Database '{db_name}' does not exist. Creating...")
            cursor.execute(f"CREATE DATABASE {db_name}")
            print(f"Database '{db_name}' created successfully.")
        else:
            print(f"Database '{db_name}' already exists.")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error creating database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    create_database()
