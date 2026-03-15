from dotenv import load_dotenv
import os
import re
import pathlib
import mysql.connector

load_dotenv(".env.development")


class Database:
    @staticmethod
    def get_new_client():
        new_client = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE"),
        )
        return new_client

    @classmethod
    def run_sql_file(cls, path: pathlib.Path):
        """
        Reads a SQL file, removes comments, splits it into individual statements, and executes them against the MySQL database.
        """
        with open(path, "r") as f:
            content = f.read()

        content = re.sub(r"--[^\n]*", "", content)
        statements = [s.strip() for s in content.split(";") if s.strip()]

        client = cls.get_new_client()
        cursor = client.cursor()
        try:
            for statement in statements:
                cursor.execute(statement)
            client.commit()
        except mysql.connector.Error as err:
            client.rollback()
            raise Exception(f"Erro ao executar {path.name}: {err}")
        finally:
            cursor.close()
            client.close()

    @classmethod
    def query(cls, query, params=None):
        if query is None:
            raise ValueError("No query object provided.")

        client = None
        cursor = None

        try:
            client = cls.get_new_client()
            cursor = client.cursor(dictionary=True, buffered=True)
            cursor.execute(query, params)
            client.commit()

            if cursor.lastrowid:
                return cursor.lastrowid

            return cursor.fetchall()

        except mysql.connector.Error as err:
            if client:
                client.rollback()
            raise Exception(f"Database error: {err}") from err

        finally:
            if cursor:
                cursor.close()
            if client:
                client.close()
