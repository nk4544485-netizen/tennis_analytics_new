import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    host = os.getenv("MYSQL_HOST")
    port = int(os.getenv("MYSQL_PORT", "3306"))
    user = os.getenv("MYSQL_USER")
    password = os.getenv("MYSQL_PASSWORD")
    database = os.getenv("MYSQL_DATABASE")

    try:
        return mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
    except Exception as exc:
        # Provide a clearer, non-sensitive error message for deployment logs
        masked_host = host if host is None else host
        raise RuntimeError(
            f"Unable to connect to MySQL at '{masked_host}': {exc}. "
            "Check MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, and network access."
        ) from exc