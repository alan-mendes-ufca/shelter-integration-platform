import os
import mysql.connector


class Database:
    @staticmethod
    def query(query:dict = None):
        """Executes a database query using the provided query object and an optional returning query."""

        def get_new_client():
            new_client = mysql.connector.connect(
                    host=os.getenv('MYSQL_HOST'),
                    user=os.getenv('MYSQL_USER'),
                    password=os.getenv('MYSQL_PASSWORD'),
                    database=os.getenv('MYSQL_DATABASE')
                )
            return new_client


        if query is None:
            print("No query object provided.")
            return None

        client = None
        cursor = None

        try:
            client = get_new_client()
            cursor = client.cursor(dictionary=True)
            result = cursor.execute(query['text'], query['values'])
            client.commit() # Ensure that changes are saved to the database

            return cursor.fetchall()

        except mysql.connector.Error as err:
            if client: client.rollback()  # Rollback any changes if an error occurs
            raise Exception(f"Error connecting to database: {err}")

        finally:
            if cursor: cursor.close()
            if client: client.close()


