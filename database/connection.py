import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def _read_mysql_setting(key, fallback=None):
    """Read config from Streamlit secrets first, then environment variables."""
    try:
        import streamlit as st
        secrets = getattr(st, "secrets", {})
        if not isinstance(secrets, dict):
            secrets = {}

        for secret_key in (key, key.lower(), key.upper()):
            if secret_key in secrets:
                return secrets[secret_key]

        mysql_section = secrets.get("mysql", {})
        if isinstance(mysql_section, dict):
            for secret_key in (key, key.lower(), key.upper()):
                if secret_key in mysql_section:
                    return mysql_section[secret_key]
    except Exception:
        pass

    return os.getenv(key, fallback)


def get_connection():
    host = _read_mysql_setting("MYSQL_HOST")
    port = _read_mysql_setting("MYSQL_PORT", "3306")
    user = _read_mysql_setting("MYSQL_USER")
    password = _read_mysql_setting("MYSQL_PASSWORD")
    database = _read_mysql_setting("MYSQL_DATABASE")

    missing = [
        name for name, value in {
            "MYSQL_HOST": host,
            "MYSQL_PORT": port,
            "MYSQL_USER": user,
            "MYSQL_PASSWORD": password,
            "MYSQL_DATABASE": database,
        }.items() if value in (None, "")
    ]

    if missing:
        raise RuntimeError(
            "MySQL settings are missing. Set them in Streamlit secrets or environment variables: "
            + ", ".join(missing)
        )

    try:
        return mysql.connector.connect(
            host=host,
            port=int(port),
            user=user,
            password=password,
            database=database
        )
    except Exception as exc:
        masked_host = host if host is not None else "<unknown>"
        raise RuntimeError(
            f"Unable to connect to MySQL at '{masked_host}': {exc}. "
            "Check MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, and network access."
        ) from exc