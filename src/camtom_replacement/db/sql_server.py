from contextlib import contextmanager
import pyodbc


class SqlServerClient:
    def __init__(self, server: str, database: str, username: str, password: str) -> None:
        self.connection_string = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            f"SERVER={server};"
            "PORT=1433;"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password}"
        )

    @contextmanager
    def connect(self):
        conn = pyodbc.connect(self.connection_string)
        try:
            yield conn
        finally:
            conn.close()
